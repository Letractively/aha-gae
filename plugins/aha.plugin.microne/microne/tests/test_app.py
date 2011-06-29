# -*- coding: utf-8 -*-

from unittest import TestCase
import logging
log = logging.getLogger(__name__)

from nose.tools import *
from google.appengine.api import apiproxy_stub_map
from google.appengine.api.memcache import memcache_stub
from google.appengine.api import user_service_stub
from google.appengine.api import memcache

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

    def test_cache(self):
        # make a new router
        rebuild_router()
        app = Microne('cache text')

        foo = 'foo'

        @app.route('/c_url')
        @app.cache(expire = 10)
        def url():
            app.render(foo)

        @app.cache()
        @app.route('/c_url2')
        def url2():
            app.render(foo)

        @app.cache(expire = 0)
        @app.route('/c_url3')
        def url3():
            app.render(foo)

        @app.route('/c_url4')
        def url4():
            app.render(foo)

        def nsfunc(req):
            return req.params.get('baz', '')

        @app.route('/c_url5')
        @app.cache(namespace_func = nsfunc)
        def url5():
            app.render(foo)


        # checking if cached function returns 'foo' for the first time.
        resp = self.app.get('/c_url')
        assert_equal(resp.body, 'foo')
        assert_equal(memcache.get('/c_url').get('body', ''), 'foo')
        assert_equal(memcache.get('/c_url', 'baz'), None)

        resp = self.app.get('/c_url2')
        assert_equal(resp.body, 'foo')

        resp = self.app.get('/c_url3')
        assert_equal(resp.body, 'foo')

        resp = self.app.get('/c_url4')
        assert_equal(resp.body, 'foo')

        resp = self.app.get('/c_url5')
        assert_equal(resp.body, 'foo')


        # changing local variable to make it return different result
        #    in non-cached functions.
        foo = 'bar'

        # check if cached function returns the same response it produced 
        #  the last time.
        resp = self.app.get('/c_url')
        assert_equal(resp.body, 'foo')
        resp = self.app.get('/c_url2')
        assert_equal(resp.body, 'bar')

        # check if cached but expire = 0 and non-cached function
        #   returns different result.
        resp = self.app.get('/c_url3')
        assert_equal(resp.body, 'bar')
        resp = self.app.get('/c_url4')
        assert_equal(resp.body, 'bar')

        resp = self.app.get('/c_url5')
        assert_equal(resp.body, 'foo')
        assert_equal(memcache.get('/c_url5', 'bar'), None)

        #resp = self.app.get('/c_url5?baz=bar')
        #assert_equal(memcache.get('/c_url5', 'bar').get('body', ''), 'bar')
        #assert_equal(resp.body, 'bar')

