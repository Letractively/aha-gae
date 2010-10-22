# -*- coding: utf-8 -*-
#
# This code is derived from memcache.py on App Engine Oil
#
# Copyright 2008 Lin-Chieh Shangkuan & Liang-Heng Chen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
""" GAEO Session - memcache store """

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'


import random
import pickle
import logging
import Cookie
from rfc822 import formatdate
from datetime import datetime
from time import time

from google.appengine.api import memcache

from aha import session, Config

class MemcacheSession(session.Session):
    """ session that uses memcache """

    def __init__(self, hnd, name = session.COOKIE_NAME, timeout = 0):
        """
        timeout = 0  : setting timeout based on config.
        timeout = -1 : setting timeout to the long future.
        other than above : everlasting.
        """
        if not timeout:
            config = Config()
            timeout = getattr(config, 'session_timeout', 60*60)
        elif timeout == -1:
            timeout = 356*24*60*60*50
        super(MemcacheSession, self).__init__(hnd, name, timeout)

        # check from cookie
        if name in hnd.request.cookies:
            self._id = hnd.request.cookies[name]
            session_data = memcache.get(self._id)
            if session_data:
                self.update(pickle.loads(session_data))
                memcache.set(self._id, session_data, timeout)
        else:   # not in the cookie, set it
            c = Cookie.SimpleCookie()
            c[name] = self._id
            c[name]['path'] = '/'
            c[name]['expires'] = formatdate(time()+timeout)
            cs = c.output().replace('Set-Cookie: ', '')
            hnd.response.headers.add_header('Set-Cookie', cs)

    def put(self):
        if not self._invalidated:
            memcache.set(self._id, pickle.dumps(self.copy()), self._timeout)

    def invalidate(self):
        """Invalidates the session data"""
        self._hnd.response.headers.add_header(
            'Set-Cookie',
            '%s = ; expires = Thu, 1-Jan-1970 00:00:00 GMT;' % self._name
        )
        memcache.delete(self._id)
        self.clear()
        self._invalidated = True
