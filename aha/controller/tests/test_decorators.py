# -*- coding: utf-8 -*-

from unittest import TestCase
import logging
log = logging.getLogger(__name__)

from nose.tools import *
from google.appengine.api import memcache

from aha.controller.decorator import *

class TestDecorators(TestCase):

    def test_authenticate(self):
        """
        Test for authenticate decorator
        """
        def f(self):
            return False

        def t(self):
            return True

        class authclass(object):
            def auth(arg1, *params, **kws):
                return True

            def auth_redirect(arg1, *params, **kws):
                # decorated (controller) class instance is passed
                #   in first parameter.
                params[0].redirected = True

        class foo(object):
            class request(object):
                url = 'http://www.example.com'

            class response:
                @staticmethod
                def set_status(a):
                    pass

            @authenticate(t, auth_obj=authclass)
            def test_true(self):
                return "foo"

            @authenticate(f, auth_obj=authclass)
            def test_false(self):
                return "bar"


        i = foo()
        # decorated method with function that always return true
        #        must proceed function code
        assert_equal(i.test_true(), 'foo')
        # decorated method with function that always return false
        #        must not proceed function code and returns false
        assert_equal(i.test_false(), None)
        # check if authclass.auth_redirect() sets i.redirected = True
        assert_true(i.redirected)

    def test_expose(self):
        """
        Test for expose decorater
        """

        # dummy function
        @expose
        def foo():
            pass

        # check if foo function has _exposed_ attribute
        assert_true(hasattr(foo, '_exposed_'))
        # check if foo,._exposed_ = True
        assert_true(foo._exposed_)

    def test_cache(self):
        """
        Test for cache decorator
        """
        import StringIO

        def nsfunc(request):
            return request.namespace

        class dummy_req(object):
            pass

        class handler(object):
            def __init__(self):
                self.response = dummy_req()
                self.response.headers = ''
                dummy_req.out = StringIO.StringIO()
                self.request = dummy_req()

            @cache()
            def handle1(self):
                self.response.out = StringIO.StringIO()
                self.response.out.write('handle1')

            @cache(expire = 0)
            def handle2(self):
                self.response.out = StringIO.StringIO()
                self.response.out.write('handle2')


        class handler2(handler):

            @cache()
            def handle3(self):
                self.response.out = StringIO.StringIO()
                self.response.out.write('handle3')

        hdn = handler()

        # check if simple cache decorator stores response to the memcache.
        hdn.request.url = 'http://example.com/the_url'
        hdn.handle1()
        assert_equal(memcache.get('/the_url').get('body', ''), 'handle1')

        # check if cache decorator with expire = 0 stores no cache.
        memcache.flush_all()
        hdn.handle2()
        assert_equal(memcache.get('/the_url'), None)

        # check if cache decorator with name space function store a cache
        #        along with the namespace returned by the function
        hdn2 = handler2()
        hdn2.request.url = 'http://example.com/the_url'
        cache.set_namespace_func(nsfunc)


        memcache.flush_all()
        hdn2.request.namespace = 'ns'
        hdn2.handle3()
        assert_equal(memcache.get('/the_url'), None)
        assert_equal(memcache.get('/the_url', namespace = 'ns').get('body'),
                     'handle3')


