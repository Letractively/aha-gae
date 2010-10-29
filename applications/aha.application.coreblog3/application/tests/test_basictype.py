# -*- coding: utf-8 -*-

import os
import unittest

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from google.appengine.api.memcache import memcache_stub
from google.appengine.api import mail_stub
from google.appengine.api import urlfetch_stub
from google.appengine.api import user_service_stub
from google.appengine.ext import db, search
from google.appengine.api import memcache

from nose.tools import *

from google.appengine.api import users

from application.model.basictype import *

APP_ID = os.environ['APPLICATION_ID']
AUTH_DOMAIN = 'gmail.com'
LOGGED_IN_USER = 'test@example.com'

class GAETestBase(unittest.TestCase):

    def setUp(self):

       # registering API Proxy
       apiproxy_stub_map.apiproxy =\
                apiproxy_stub_map.APIProxyStubMap()
       apiproxy_stub_map.apiproxy.RegisterStub( \
            'memcache', memcache_stub.MemcacheServiceStub())

       # registering dummy Datastore
       stub = datastore_file_stub.DatastoreFileStub(APP_ID,'/dev/null',
                                                           '/dev/null')
       apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)

class BasictypeTest(GAETestBase):

    def test_01_folder(self):

        f = Folder(name = '', creator = 'foo')
        f.put()
        f.sync_path('')
        pl = []
        for p in range(10):
            p = Page(name = str(p), body = 'body of %s' % p, creator = 'foo')
            p.put()
            f.add(p)
            p.sync_path(str(p))
            pl.append(p)

        # Root.get_parent() must be None
        assert_equal(f.get_parent(), None)

        # checking if child_count is correctly maintained
        assert_equal(f.child_count, 10)

        assert_equal(str(f.get_child('1').key()), str(pl[1].key()))
        assert_equal(sorted([str(x.key()) for x in f.get_childs()]),
                     sorted([str(x.key()) for x in pl]))
        assert_equal(pl[1].get_path(), '/1')
        assert_equal(pl[1].get_parent().get_path(), f.get_path())

        # check for parent key
        assert_equal(pl[1].cparent_key, f.get_namekey())


        f2 = Folder(name = 'foo', creator = 'foo')
        f2.put()
        f.add(f2)
        assert_equal(f.child_count, 11)
        assert_equal(f2.get_path(), '/foo')

        f3 = Folder(name = 'bar', creator = 'foo')
        f3.put()
        f2.add(f3)
        assert_equal(f3.get_path(), '/foo/bar') 

        p = Page(name = 'foopage', body = 'foobody', creator = 'foo')
        p.put()
        f3.add(p)
        assert_equal(p.get_path(), '/foo/bar/foopage') 

        # calling get_child() with type
        nl = sorted([x.name for x in f.get_childs(type = 'Folder')])
        assert_equal(nl, ['foo'])

        # calling get_child() with more than one types
        nl = sorted([str(x.name) for x in f.get_childs(type = ['Folder', 'Page'])])
        assert_equal(nl, sorted(['foo']+[x.name for x in pl]))

        # calling get_child() with more than one types,
        #  list and tuple may be accepted.
        nl = sorted([str(x.name) for x in f.get_childs(type = ('Folder', 'Page'))])
        assert_equal(nl, sorted(['foo']+[x.name for x in pl]))

        # checking remove() method of container
        f.remove('2')
        memcache.flush_all()
        nl = sorted([x.name for x in f.get_childs()])
        assert_equal(len(nl), 10)
        assert_true('2' not in nl)
        assert_equal(f.get_child('2'), None)
        assert_equal(f.child_count, 10)



