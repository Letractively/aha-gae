# -*- coding: utf-8 -*-

from unittest import TestCase
import logging
log = logging.getLogger(__name__)

from nose.tools import *
from google.appengine.api import apiproxy_stub_map
from google.appengine.api.memcache import memcache_stub
from google.appengine.api import urlfetch_stub

from aha.wsgi.appinit import get_app
from aha.dispatch.router import rebuild_router

from plugin.microne.config import *
from plugin.microne.app import *

import webtest

class TestDispatchers(TestCase):

    def setUp(self):

        if not apiproxy_stub_map.apiproxy.GetStub('memcache'):
            apiproxy_stub_map.apiproxy.RegisterStub( \
                'memcache', memcache_stub.MemcacheServiceStub())
        if not apiproxy_stub_map.apiproxy.GetStub('urlfetch'):
            apiproxy_stub_map.apiproxy.RegisterStub( \
                'urlfetch', urlfetch_stub.URLFetchServiceStub())

    def test_route(self):
        # make a new router
        rebuild_router()

        foo = lambda x: x*2
        bar = lambda id: id*2

        app = Microne('foo')

        app.route('/foo_url')(foo)
        app.route('/bar_url/{id}')(bar)

        # checking if route for '/url' matches the function foo()
        from aha.dispatch.router import get_router

        router = get_router()
        route = router.match('/foo_url')
        assert_not_equal(route, None)
        assert_equal(route['controller'], foo)

        route = router.match('/bar_url/the_id')
        assert_not_equal(route, None)
        assert_equal(route['controller'], bar)


