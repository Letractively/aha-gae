# -*- coding: utf-8 -*-
#
# This code is derived from memcache.py on App Engine Oil

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'


import random
import pickle
import logging
from Cookie import SimpleCookie
from rfc822 import formatdate
from datetime import datetime, timedelta
from time import time

from google.appengine.ext import db

from aha import session

SESSION_DURATION = timedelta(hours = 1)

class SessionStore(db.Model):
    id = db.StringProperty()
    value = db.BlobProperty()
    expires = db.DateTimeProperty()
    
    @classmethod
    def clear(cls):
        lst = cls.gql("WHERE expires < :1", datetime.now()).fetch(1000)
        for item in lst:
            item.delete()

class DatastoreSession(session.Session):
    """ session that uses the datastore """

    def __init__(self, hnd, name = session.COOKIE_NAME, timeout = 0):
        super(DatastoreSession, self).__init__(hnd, name, timeout)
        
        SessionStore.clear()
        
        # check from cookie
        if not timeout:
            config = Config()
            timeout = config.get('session_timeout', 60*60)
        elif timeout == -1:
            timeout = 356*24*60*60*50
        if name in hnd.request.cookies:
            self._id = hnd.request.cookies[name]
            res = SessionStore.gql("WHERE id = :1", self._id).get()
            if res:
                self._store = res
                session_data = self._store.value
                if session_data:
                    self.update(pickle.loads(session_data))
            else:
                self._create_store(self._id)
        else:   # not in the cookie, set it
            c = SimpleCookie()
            c[name] = self._id
            c[name]['path'] = '/'
            c[name]['expires'] = rfc822.formatdate(time()+timeout)
            cs = c.output().replace('Set-Cookie: ', '')
            hnd.response.headers.add_header('Set-Cookie', cs)
            self._create_store(self._id)

    def put(self):
        if not self._invalidated and self._store:
            self._store.value = pickle.dumps(self.copy())
            self._store.expires = datetime.now() + SESSION_DURATION
            self._store.put()

    def invalidate(self):
        """Invalidates the session data"""
        self._hnd.response.headers.add_header(
            'Set-Cookie',
            '%s = ; expires = Thu, 1-Jan-1970 00:00:00 GMT;' % self._name
        )
        self._store.delete()
        self._store = None
        self.clear()
        self._invalidated = True
        
    def _create_store(self, id):
        self._store = SessionStore(
                                   id = id,
                                   value = pickle.dumps(dict()),
                                   expires = datetime.now() + SESSION_DURATION)
        self._store.put()
        self._id = id
