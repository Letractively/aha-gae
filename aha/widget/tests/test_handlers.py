# -*- coding: utf-8 -*-


import os
from unittest import TestCase
import logging
log = logging.getLogger(__name__)

from nose.tools import *

from coregae.widget.handler import (MediaHandler, TemplateHandler,
                      TemplateEngine, MakoTemplateEngine)

class TestMediahandler(TestCase):

    def test_mediahandler(self):
        """
        Test for MediaHandler
        """
        mh = MediaHandler()
        obs = (('foo.css', 'text/css'),
               ('bar.css', 'text/css'),
               ('baz.js', 'text/javascript'),)
        mh.add_object(*obs[0])
        assert_equal(mh.get_objects(), [obs[0]])
        mh.add_object(*obs[1])
        assert_equal(mh.get_objects(), [obs[0], obs[1]])
        
        mh.add_object(*obs[0])
        assert_equal(mh.get_objects(), [obs[0], obs[1]])

        mh.add_object(*obs[2])
        mh.add_object(*obs[0])
        assert_equal(mh.get_objects(), [obs[0], obs[1], obs[2]])
        assert_equal(mh.get_objects('text/css'), [obs[0], obs[1]])
        assert_equal(mh.get_objects('text/javascript'), [obs[2]])


class TestTemplateHander(TestCase):

    def test_templatehandler(self):
        """
        Test for TemplateHandler
        """

        class DymmyTE1(TemplateEngine):
            ENGINE_NAME = 'dummy1'

        class DymmyTE2(TemplateEngine):
            ENGINE_NAME = 'dummy2'

        th = TemplateHandler()
        assert_equal(th.get_defaultengine(), 'mako')
        th.set_defaultengine('foo')
        assert_equal(th.get_defaultengine(), 'foo')
        th.set_defaultengine('mako')
        assert_raises(KeyError, th.get_engine, 'foo')
        e1 = DymmyTE1()
        e2 = DymmyTE2()
        th.add_engine(e1)
        assert_equal(th.get_engine('dummy1'), e1)
        assert_raises(KeyError, th.get_engine, 'dummy2')
        th.add_engine(e2)
        assert_equal(th.get_engine('dummy1'), e1)
        assert_equal(th.get_engine('dummy2'), e2)
        assert_raises(KeyError, th.get_engine, 'dummy3')

        th.set_defaultengine('dummy1')
        assert_equal(th.get_engine('dummy1'), e1)

        tid = e1.set_template_cache('foo')
        assert_equal(e1.get_template_cache(tid), 'foo')

        e1.set_template_cache('bar', 'foo_id')
        assert_equal(e1.get_template_cache('foo_id'), 'bar')

        assert_equal(e1.get_template_cache('foo_id_tmp'), None)

        assert_equal(e1.get_cache_tid('bar'), 'foo_id')
        assert_equal(e1.get_cache_tid('foo'), tid)


    def test_mako_render(self):
        """
        Test method for rendering funcions.
        """
        from mako.template import Template
        me = MakoTemplateEngine(dirs = [os.path.dirname(__file__)])
        assert_true(isinstance(me.get_template(string = 'foobar'), Template))
        assert_true(isinstance(me.get_template(path = 'mak'), Template))
        assert_true(isinstance(me.get_template(path = 'html.html'), Template))
        me2 = MakoTemplateEngine('.html', dirs = [os.path.dirname(__file__)])
        assert_true(isinstance(me2.get_template(path = 'html'), Template))

        def test_src(src):
            assert_true('FOO' in src)
            assert_true('BAR' in src)
            assert_true('likes' in src)
            assert_false('BAZ' in src)

        c = {'foo':'FOO', 'bar':'BAR'}
        src = me.render(c, me.get_template(path = 'mak'))
        test_src(src)

        src = me.render(c, path = 'mak')
        test_src(src)

        src = me.render(c, string = '${foo} likes the ${bar}')
        test_src(src)


