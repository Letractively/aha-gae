# -*- coding: utf-8 -*-

from unittest import TestCase
import logging
log = logging.getLogger(__name__)

from nose.tools import *

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


