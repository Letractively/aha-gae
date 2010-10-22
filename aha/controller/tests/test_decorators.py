# -*- coding: utf-8 -*-

from unittest import TestCase
import logging
log = logging.getLogger(__name__)

from nose.tools import *

from coregae.controller.decorators import *

class TestDecorators(TestCase):

    def test_authenticate(self):
        """
        Test for authenticate decorator
        """
        def f(self):
            return False

        def t(self):
            return True

        class foo(object):
            class request(object):
                url = 'http://www.example.com'

            @authenticate(t)
            def test_true(self):
                return "foo"

            @authenticate(f)
            def test_false(self):
                return "bar"

            def redirect(self, arg):
                self.redirected = True

            def set_status(self, *args):
                self.redirected = True


        i = foo()
        assert_equal(i.test_true(), 'foo')
        assert_equal(i.test_false(), None)
        assert_equal(i.redirected, True)

