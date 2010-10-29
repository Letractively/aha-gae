# -*- coding: utf-8 -*-

import os
import unittest
import time
from datetime import datetime, timedelta

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

from application.model.basictype import Path
from application.model.blogengine import *

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

class BlogenbineTest(GAETestBase):

    def test_01_blog(self):

        f = Blog(name = '', creator = 'foo')
        f.put()
        f.sync_path('')

        cl = []
        c = BlogCategory(name = 'c1', creator = 'foo')
        c.put();
        f.add(c)

        c.set_category_id()
        cl.append(c)

        c = BlogCategory(name = 'c2', creator = 'foo')
        c.put();
        f.add(c)
        c.set_category_id()
        cl.append(c)

        assert_equal(cl[0].category_id, '1')
        assert_equal(cl[1].category_id, '2')

        assert_equal(cl[0].name, f.get_category_by_id(cl[0].category_id).name)
        assert_equal(f.get_category_by_id(100), None)

        pl = []
        for p in range(10):
            if p < 3:
                cs = ['1']
            elif p < 6:
                cs = ['2']
            else:
                cs = ['1', '2']
            p = BlogEntry(name = str(p), body = 'body of %s' % p, creator = 'foo',
                    categories = cs)
            p.put()
            f.add(p)
            p.sync_path(str(p))
            pl.append(p)

        # Root.get_parent() must be None
        assert_equal(f.get_parent(), None)

        # checking if child_count is correctly maintained
        assert_equal(len(f.get_entries()), 10)


        assert_equal(f.get_child('1').key(), pl[1].key())
        assert_equal(sorted([x.key() for x in f.get_entries()]),
                     sorted([x.key() for x in pl]))
        assert_equal(pl[1].get_path(), '/1')
        assert_equal(pl[1].get_parent().get_path(), f.get_path())

        assert_equal(sorted([x.key() for x in f.get_categories()]),
                     sorted([x.key() for x in cl]))

        # check for getting category object from entry
        assert_equal(sorted([x.name for x in pl[1].get_category_objects()]),
                     ['c1'])
        assert_equal(sorted([x.name for x in pl[7].get_category_objects()]),
                     ['c1', 'c2'])


        # check for category assignment
        assert_equal(sorted([x.name for x in cl[0].get_entries()]),
                     ['0', '1', '2', '6', '7', '8', '9'])

        assert_equal(sorted([x.name for x in cl[1].get_entries()]),
                     ['3', '4', '5', '6', '7', '8', '9'])


        # test for entry listing
        bd = datetime(2010, 1, 2, 12, 30, 20)
        for d, e in enumerate(pl):
            e.created_at = bd+timedelta(days = d)
            e.sync_path(e.get_path())
            e.put()

        # test for getting prev, next blog.
        assert_equal(pl[2].get_previous().name, pl[1].name)
        assert_equal(pl[5].get_next().name, pl[6].name)

        # test for getting entries in a date range.
        assert_equal(sorted([x.name
                     for x in f.get_entries(start_date = bd+timedelta(days = 2),
                                            end_date = bd+timedelta(days = 5))]),
                     ['2', '3', '4', '5'])
        """
        assert_equal(sorted([x.name
                     for x in f.get_entries(start = 2,
                                            start_date = bd+timedelta(days = 2),
                                            end_date = bd+timedelta(days = 5))]),
                     ['4', '5'])
        """

        # test for adding comments
        pl[2].add_comment('name1', 'http://foo1', 'mail1@com',
                          'title1', 'body', 'creator')
        time.sleep(1)
        pl[2].add_comment('name2', 'http://foo2', 'mail2@com', 
                          'title2', 'body', 'creator')
        time.sleep(1)
        pl[2].add_comment('name3', 'http://foo3', 'mail3@com', 
                          'title3', 'body', 'creator')
        time.sleep(1)

        assert_equal(sorted([x.name for x in pl[2].get_comments()]),
                     ['comment1', 'comment2', 'comment3'])
        assert_equal(sorted([x.author_name for x in pl[2].get_comments()]),
                     ['name1', 'name2', 'name3'])

        assert_false(sorted([x.name for x in pl[3].get_comments()]))

        pl[5].add_comment('name4', 'http://foo4', 'mail4@com', 
                          'title4', 'body', 'creator')

        assert_equal([x.author_name for x in f.get_comments()],
                     ['name4', 'name3', 'name2', 'name1'])
