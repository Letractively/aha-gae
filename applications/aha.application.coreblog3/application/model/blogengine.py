# -*- coding: utf-8 -*-
#
# blogengine.py
# A collection of model classes, that store information for blog content.
#
# Copyright 2010 Atsushi Shibata
#

"""
A collection of model classes, that store information for blog content.

$Id: forms.py 649 2010-08-16 07:44:47Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'MIT'

__all__ = ['Blog', 'BlogEntry', 'BlogComment', 'BlogTrackback', 'BlogCategory']

from datetime import datetime, timedelta
import re
import logging

from google.appengine.ext import db

from basictype import Path, ContentBase, Folder, register_content_class

class Blog(Folder):
    """
    A model class of blog, storing entries, categories, comments etc.
    """
    __SAVED_PROPS__ = []
    TYPE = 'Blog'

    # Properties

    ping_urls = db.TextProperty(required = False)

    top_entry_count = db.IntegerProperty(required = False, default = 0)
    recent_item_count = db.IntegerProperty(required = False, default = 0)

    accept_comment = db.IntegerProperty(required = False, default = 0)
    auth_comment = db.BooleanProperty(required = False, default = False)
    accept_trackback = db.IntegerProperty(required = False, default = 0)

    ADDABLE = ['BlogEntry', 'BlogCategory', #'BlogParts',
             'Folder', 'Page', 'File', 'Image']


    def get_entries(self, start = 0, end = -1, order = '-created_at',
                    start_date = None, end_date = None):
        """
        A method to obtain entries on a blog.
        """
        if not start_date and not end_date:
            return self.get_childs(start, end, order, type = 'BlogEntry')
        # try to find blog entry in given date range
        q = BlogEntry.all()
        q.filter('cparent_key =', self.get_namekey())
        q.filter('created_at >= ', start_date)
        q.filter('created_at <= ', end_date)
        q.order(order)
        if end == -1:
            end = start+self.BATCH_SIZE
        return list(q.fetch(end-start, offset = start))


    def get_categories(self, start = 0, end = -1, order = '-created_at'):
        """
        A method to obtain categories on a blog.
        """
        return self.get_childs(start, end, order, type = 'BlogCategory')


    def get_category_by_id(self, catid):
        """
        A method to obtain category by using given id.
        """
        q = BlogCategory.all()
        q.filter('category_id =', catid)
        r = q.fetch(1)
        if r:
            return list(r)[0]
        return None


    def get_unique_category_id(self):
        """
        A method to determine unique category id on the blog.
        """
        oid = 0
        for cat in self.get_childs(type = 'BlogCategory'):
            oid = max(oid, int(cat.category_id))
        return oid+1


    def get_comments(self, start = 0, end = -1, order = '-created_at',
                     start_date = None, end_date = None):
        """
        A method to obtain comments on a blog.
        """
        q = BlogComment.all()
        q.filter('parent_blog_key =', self.get_namekey())
        if start_date:
            q.filter('created_at >= ', start_date)
        if  end_date:
            q.filter('created_at <= ', end_date)
        q.order(order)
        if end == -1:
            end = start+self.BATCH_SIZE
        return list(q.fetch(end-start, offset = start))

    def get_trackbacks(self, start = 0, end = -1, order = '-created_at',
                     start_date = None, end_date = None):
        """
        A method to obtain trackbacks on a blog.
        """
        q = BlogTrackback.all()
        q.filter('parent_blog_key =', self.get_namekey())
        if start_date:
            q.filter('created_at >= ', start_date)
        if  end_date:
            q.filter('created_at <= ', end_date)
        q.order(order)
        if end == -1:
            end = start+self.BATCH_SIZE
        return list(q.fetch(end-start, offset = start))



class BlogEntry(Folder):
    """
    A model class of blog entry, that stores body, comments, trackbacks
    """
    __SAVED_PROPS__ = []
    TYPE = 'BlogEntry'

    body = db.TextProperty(required = False)
    extend_body = db.TextProperty(required = False)
    categories = db.ListProperty(item_type = str)

    accept_comment = db.IntegerProperty(required = False, default = 0)
    accept_trackback = db.IntegerProperty(required = False, default = 0)

    comment_count = db.IntegerProperty(required = False, default = 0)
    trackback_count = db.IntegerProperty(required = False, default = 0)

    ADDABLE = ['BlogComment', 'BlogTrackback', 'File', 'Image']


    def blog_object(self):
        """
        A method to obtain parent blog object.
        """
        return self.get_parent()


    def get_previous(self):
        """
        A method to obtain previous entry.
        """
        blog = self.blog_object()
        q = BlogEntry.all()
        q.filter('cparent_key =', blog.get_namekey())
        q.filter('created_at <', self.created_at)
        q.order('-created_at')
        e = None
        for e in q.fetch(1): pass;
        return e


    def get_next(self):
        """
        A method to obtain next entry.
        """
        blog = self.blog_object()
        q = BlogEntry.all()
        q.filter('cparent_key =', blog.get_namekey())
        q.filter('created_at >', self.created_at)
        q.order('created_at')
        e = None
        for e in q.fetch(1): pass;
        return e

    def get_category_objects(self):
        """
        A method to obtain category object associated to the entry
        """
        clist = []
        blog = self.blog_object()
        for cid in self.categories:
            cobj = blog.get_category_by_id(cid)
            if cobj: clist.append(cobj)
        return clist


    #
    # comment management
    #

    def get_comments(self, order = '-created_at'):
        """
        A method to obtain all the comments a entry has.
        """
        return self.get_childs(type = 'BlogComment', order = order)


    def add_comment(self, name, url, email, title, body, creator):
        """
        A method to add a comment
        """
        cid = 0
        for c in self.get_comments():
            cid = max(cid, int(c.name.replace('comment', '')))
        cid += 1
        c = BlogComment(author_name = name, url = url, email = email,
                      title = title, body = body, name = 'comment%s' % cid,
                      creator = creator,
                      parent_blog_key = self.blog_object().get_namekey())
        c.put()
        self.add(c)
        self.comment_count += 1
        self.put()


    #
    # trackback management
    #

    def get_trackbacks(self):
        """
        A method to obtain all the trackbacks a entry has.
        """
        return self.get_childs(type = 'BlogTrackback')


    def add_trackback(self, name, url, email, title, body, creator):
        """
        A method to add a comment
        """
        cid = 0
        for c in self.get_trackbacks():
            cid = max(cid, int(c.name.replace('trackback', '')))
        c = BlogComment(author_name = name, url = url, email = email,
                      title = title, body = body, name = 'trackback%s' % cid,
                      creator = creator,
                      parent_blog_key = self.blog_object().get_namekey())
        c.put()
        self.add(c)
        self.trackback_count += 1
        self.put()


class BlogComment(ContentBase):
    """
    A model class of blog comment, storing name, url, body etc.
    """
    __SAVED_PROPS__ = []
    TYPE = 'BlogComment'

    url = db.StringProperty(required = False)
    email = db.StringProperty(required = False)
    author_name = db.StringProperty(required = False)
    body = db.TextProperty(required = False)
    parent_blog_key = db.StringProperty(required = False)


class BlogTrackback(ContentBase):
    """
    A model class of blog trackback, storing name, url, body etc.
    """
    __SAVED_PROPS__ = []
    TYPE = 'BlogTrackback'

    url = db.StringProperty(required = False)
    email = db.StringProperty(required = False)
    author_name = db.StringProperty(required = False)
    body = db.TextProperty(required = False)
    parent_blog_key = db.StringProperty(required = False)


class BlogCategory(ContentBase):
    """
    A model class of blog category, representing categories on a blog.
    """
    __SAVED_PROPS__ = []
    TYPE = 'BlogCategory'

    category_id = db.StringProperty(required = False, default = '0')

    def set_category_id(self):
        """
        A method to set unique category id
        """
        blog = self.get_parent()
        self.category_id = str(blog.get_unique_category_id())
        self.put()


    def get_entries(self, start = 0, end = -1, order = '-created_at'):
        """
        A method to obtain entries in a category.
        """
        blog = self.get_parent()
        q = BlogEntry.all()
        q.filter('cparent_key =', blog.get_namekey())
        q.filter('categories =', self.category_id)
        q.order(order)
        if end == -1:
            end = start+blog.BATCH_SIZE
        return list(q.fetch(end-start, offset = start))

# registering classes

for klass in [Blog, BlogEntry, BlogComment, BlogTrackback, BlogCategory]:
    register_content_class(klass.TYPE, klass)

Folder.ADDABLE.append('Blog')


