# -*- coding: utf-8 -*-

import os
import unittest

from google.appengine.api import apiproxy_stub_map
from google.appengine.api.memcache import memcache_stub
from google.appengine.api import datastore_file_stub
from google.appengine.api import mail_stub
from google.appengine.api import urlfetch_stub
from google.appengine.api import user_service_stub
from google.appengine.ext import db, search

from nose.tools import *

from google.appengine.api import users
from google.appengine.api import memcache

from coregae.model.cachedmodel import *
from application.model.basictype import *

APP_ID = os.environ['APPLICATION_ID']
AUTH_DOMAIN = 'gmail.com'
LOGGED_IN_USER = 'test@example.com'

class GAETestBase(unittest.TestCase):

    def setUp(self):

       # Registering API Proxy
       apiproxy_stub_map.apiproxy =\
                apiproxy_stub_map.APIProxyStubMap()
       apiproxy_stub_map.apiproxy.RegisterStub( \
            'memcache', memcache_stub.MemcacheServiceStub())

       # Registering dummy Datastore
       stub = datastore_file_stub.DatastoreFileStub(APP_ID,'/dev/null',
                                                           '/dev/null')
       apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)

from coregae.model.cachedmodel import *

class CacheTest(GAETestBase):

    def test_cached_models(self):

        class CM(CachedModelBase):
            int_id = db.IntegerProperty(required = True)
            name = db.StringProperty(required = True)

        class CMT(CachedModelBase):
            int_id2 = db.IntegerProperty(required = True)
            name2 = db.StringProperty(required = True)

        # checking if the class caches data properly
        a = CM(int_id = 1, name = 'hoge')
        assert_false(a.cached)
        a.put()
        b = CM._get(a.key())
        assert_true(isinstance(b, dict))
        assert_true(sorted(b.keys()), sorted(['int_id', 'name']))

        # testing if classmethod get() and get_by_id() get works fine
        # which means it gets data from memcache.
        d = CM.get(a.key())
        assert_true(isinstance(d, CM))
        assert_true(d.cached)

        # checking if two key/id that are from datastore and cache are the same.
        assert_true(str(d.key()), str(a.key()))

        e = CM.get(a.key())
        assert_true(isinstance(e, CM))
        assert_true(e.cached)


        # testing if classmethod get() and get_by_id() get works fine
        #  when the option force is given, 
        #   which means it gets data from datastore.
        f = CM.get(a.key(), force = True)
        assert_true(isinstance(f, CM))
        assert_false(f.cached)

        memcache.flush_all()

        # checking if get() and get_by_id() get data from datasoter,
        #   in case cached data is flushed and does not exist.
        h = CM.get(a.key())
        assert_true(isinstance(h, CM))
        assert_false(h.cached)

        """
        memcache.flush_all()

        i = CM.get_by_id(a.key().id())
        assert_true(isinstance(i, CM))
        assert_false(i.cached)
        """

        # checking if the instance obtained from memcache can be modified

        h = CM.get(a.key())
        assert_true(h.cached)
        assert_true('int_id' in h._dic)
        assert_equal(h.int_id, 1)

        h.int_id = 2
        assert_equal(h.int_id, 2)
        #assert_equal(h._dic['int_id'], 2)

        # the data on datastore is not affected modification,
        #  until it is saved to the datastore.

        i = CM.get(a.key(), force = True)
        assert_equal(i.int_id, 1)

        # now put() data that was obtained from memcashe.

        h.put()

        # check if the data on datastore was modified

        i = CM.get(a.key(), force = True)
        assert_equal(i.int_id, 2)
        
        # making sure that __SAVED_PROPS__ is differ between classes.
        j = CMT(int_id2 = 0, name2 = 'foo')
        assert_not_equal(CM.__SAVED_PROPS__, CMT.__SAVED_PROPS__)
        assert_not_equal(i.__SAVED_PROPS__, j.__SAVED_PROPS__)

        # making sure that __SAVED_PROPS__ is created only once.
        CMT.__SAVED_PROPS__ = []
        j = CMT(int_id2 = 0, name2 = 'foo')
        assert_equal(sorted(CMT.__SAVED_PROPS__), sorted(['int_id2', 'name2']))
        CMT.__SAVED_PROPS__ = ['int_id2', 'name2', 'foo']
        j = CMT(d = {'1':1})
        assert_equal(sorted(CMT.__SAVED_PROPS__),
                     sorted(['int_id2', 'name2', 'foo']))

    def test_partialcached_models(self):

        class CM2(CachedModelBase):
            CACHE_PROPS = ('int_id', )
            int_id = db.IntegerProperty(required = True)
            name = db.StringProperty(required = True)

        # checking if the class caches data properly
        a = CM2(int_id = 1, name = 'hoge')

        a.int_id = 2
        a.put()

        # check if property in cache is properly modified
        b = CM2.get(a.key())
        assert_equal(b.int_id, 2)

        # check if property not in cache is properly modified
        a.name = 'foo'
        assert_equal(a.name, 'foo')
        a.put()

        # get the data from datastore, checking if data was modified
        b = CM2.get(a.key(), force = True)
        assert_equal(b.name, 'foo')

        # when the data is gotten from memcache,
        #  getting attribute 'name' returns none
        #    because the attribute is not cached
        b = CM2.get(a.key())
        assert_equal(b.name, None)

        # test for non caching instanciate
        a = CM2(int_id = 1, name = 'hoge', cache = False)
        a.put(cache = False)
        b = CM2.get(a.key())
        assert_false(b.cached)


    def test_cached_query(self):
        class CM3(CachedModelBase):
            ADD_PROPS = ('foo', 'bar')
            int_id = db.IntegerProperty(required = True)
            name = db.StringProperty(required = True)

        ol = []
        for i in range(20):
            o = CM3(int_id = i, name = 'name%d' % i)
            o.put()
            ol.append(o)

        # put all the instance in the caceh
        for i in ol:
            CM3.get(i.key())

        # doing new query
        q = CM3.all()
        assert_true(hasattr(q, 'cls'))
        assert_true(hasattr(q, 'query'))

        # new query produces non cached objects
        q.filter('int_id >', 10)
        nl = list(q.fetch(10))
        """
        for i in nl:
            assert_false(i.cached)
        """

        # the same query produces cached objects
        q = CM3.all()
        q.filter('int_id >', 10)
        nl = list(q.fetch(10))
        for i in nl:
            assert_true(i.cached)


        # doing new query
        q = CM3.all()
        q.filter('int_id >', 20)
        q.order('-int_id')
        nl = list(q.fetch(10))
        """
        for i in nl:
            assert_false(i.cached)
        """

        # cache with offset
        q = CM3.all()
        q.filter('int_id >', 10)
        q.order('-int_id')
        nl = list(q.fetch(10, offset = 5))
        q.filter('int_id >', 10)
        q.order('-int_id')
        nl = list(q.fetch(10, offset = 5))
        for i in nl:
            assert_true(i.cached)

        # test for fluch_cache()
        q = CM3.all()
        q.order('-int_id')
        q.filter('int_id >', 10)
        q.flush_cache()
        nl = list(q.fetch(10))
        """
        for i in nl:
            assert_false(i.cached)
        """

        q = CM3.all()
        q.order('-int_id')
        q.filter('int_id >', 10)
        nl = list(q.fetch(10))
        nl = list(q.fetch(10, offset = 5))

        q.flush_cache()
        q = CM3.all()
        q.order('-int_id')
        q.filter('int_id >', 10)
        nl = list(q.fetch(10, offset = 5))

        """
        for i in nl:
            assert_false(i.cached)
        """

        # test for special caching property.
        q = CM3.all()
        q.order('-int_id')
        nl = list(q.fetch(10))

        nl[0].foo = 'foo'
        nl[0].cache()
        n = CM3.get(nl[0].key())
        assert_equal(n.foo, 'foo')

        # cached properties must be stored after flushing cache
        q = CM3.all()
        q.order('-int_id')
        q.flush_cache()
        q = CM3.all()
        q.order('-int_id')
        nl = list(q.fetch(10))
        n = CM3.get(nl[0].key())
        assert_equal(n.foo, 'foo')

        # test for count()
        q = CM3.all()
        assert_eaual(q.count(), q.count(force = True))
        q = CM3.all()
        q.filter('int_id >', 10)
        assert_eaual(q.count(), q.count(force = True))

