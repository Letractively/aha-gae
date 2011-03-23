# -*- coding: utf-8 -*-

from unittest import TestCase
import logging
log = logging.getLogger(__name__)

from nose.tools import *
from google.appengine.api import apiproxy_stub_map
from google.appengine.api.memcache import memcache_stub
from google.appengine.api import user_service_stub

from aha.wsgi.appinit import get_app
from aha.dispatch.router import rebuild_router
from plugin.microne.config import *
from plugin.microne.app import *

import webtest

from plugin.microne.app import *

AUTH_DOMAIN = 'gmail.com'
LOGGED_IN_USER = 'test@example.com'

class TestDispatchers(TestCase):

    def setUp(self):
        if not apiproxy_stub_map.apiproxy.GetStub('memcache'):
            apiproxy_stub_map.apiproxy.RegisterStub( \
                'memcache', memcache_stub.MemcacheServiceStub())
        if not apiproxy_stub_map.apiproxy.GetStub('user'):
            apiproxy_stub_map.apiproxy.RegisterStub(
                                 'user', user_service_stub.UserServiceStub())

            os.environ['AUTH_DOMAIN'] = AUTH_DOMAIN
            os.environ['USER_EMAIL'] = LOGGED_IN_USER

        initConfig('./')
        self.app = webtest.TestApp(get_app(debug = True))

    def test_set_get_hander(self):
        # make a new router
        rebuild_router()
        
        class dummy(object):
            pass
        
        dummy_hnd = dummy()
        dummy_hnd.request = 'request'
        dummy_hnd.response = 'response'

        # clear App.hnd
        Microne.hnd = None

        app = Microne('route and render html test')
        # Calling Microne.get_hander() without set hander causes ValueError.
        assert_raises(ValueError, Microne.get_handler)

        # set dummy handler
        Microne.set_handler(dummy_hnd, dummy_hnd)

        # check if correct handler is returned.
        assert_equal(Microne.get_handler(), dummy_hnd)
        assert_equal(Microne.request, 'request')
        assert_equal(Microne.response, 'response')


    def test_route_renderhtml(self):
        # make a new router
        rebuild_router()
        app = Microne('route and render html test')

        @app.route('/url')
        def url():
            app.render('foo')

        @app.route('/url/{id}')
        def url_2():
            app.render('foo')

        resp = self.app.get('/url')
        assert_equal(resp.body, 'foo')

        resp = self.app.get('/url/the_id')
        assert_equal(resp.body, 'foo')

    def test_authenticate(self):
        # make a new router
        rebuild_router()
        app = Microne('authenticate test')
        from aha.auth.appengine import AppEngineAuth
        app.config.auth_obj = AppEngineAuth

        @app.route('/auth_url')
        @app.authenticate()
        def auth_url():
            app.render('foo')

        os.environ['USER_EMAIL'] = ''
        resp = self.app.get('/auth_url')
        # request without USER_EMAIL causes redirection.
        assert_equal(resp.status, '302 Moved Temporarily')

        os.environ['USER_EMAIL'] = LOGGED_IN_USER
        resp = self.app.get('/auth_url')
        # request with valid USER_EMAIL returns correct output.
        assert_equal(resp.body, 'foo')

    def test_render_with_context(self):
        rebuild_router()
        app = Microne('route and render html test')

        @app.route('/context')
        def context():
            app.context['hoge'] = 'hoge'
            app.render('foo ${hoge}')

        resp = self.app.get('/context')
        # request without USER_EMAIL causes redirection.
        assert_equal(resp.body, 'foo hoge')


