# -*- coding: utf-8 -*-
#
# basictypes.py
# A collection of model classes, that store information for basic content.
#
# Copyright 2010 Atsushi Shibata
#
"""
A collection of model classes, that store information for basic content.

$Id: forms.py 649 2010-08-16 07:44:47Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'MIT'


__all__ = ['SiteData', 'Path', 'ContentBase', 'Folder', 'Page',
         'File', 'Image']

from inspect import isclass
from datetime import datetime, timedelta
import re
import logging

from google.appengine.ext import db

try:
    from aha.model.cachedmodel import CachedModelBase as DBBASEMODEL
except:
    from google.appengine.ext.db import Model as DBBASEMODEL

DRAFT = 0
PUBLISHED = 1

class SiteData(DBBASEMODEL):
    """
    A model class for site data.
    """
    title = db.StringProperty(required = False, default = '')
    description = db.TextProperty(required = False, default = '')
    analytics_tag = db.TextProperty(required = False, default = '')
    admin_users = db.TextProperty(required = False, default = '')

    @classmethod
    def get_data(cls):
        """
        A method to obtain / make single SiteData object.
        """
        q = cls.all()
        l = list(q.fetch(10))
        if not l:
            o = cls()
            o.put()
            return o
        return l[0]

def key2obj(key):
    """
    A function to obtain object from key,
        key must be a format of 'ClassName:Key'.
    """
    cname, dbkey = key.split(':')
    klass = get_content_class(cname)
    return klass.get(dbkey)


class Path(DBBASEMODEL):
    ctype = db.StringProperty(required = False)
    path = db.StringProperty(required = False)
    name = db.StringProperty(required = False)
    content_key = db.StringProperty(required = False)
    #content = db.ReferenceProperty(required = False, collection_name = 'obj')
    parent_c_key = db.StringProperty(required = False)
    #parent_c = db.ReferenceProperty(required = False, collection_name = 'parent_c')
    created_at = db.DateTimeProperty(required = False, auto_now_add = True)
    modified_at = db.DateTimeProperty(required = False, auto_now_add = True)


    def get_path(self):
        """
        A method to obtain path by using parent path and name
        """
        if not self.parent_c_key: return ''
        ppath = self.get_parent().get_path()
        return ppath+'/'+self.name


    def set_parent(self, par):
        """
        A method to set parent object
        """
        self.parent_c_key = str(par.key())


    def get_parent(self):
        """
        A method to obtain parent path object.
        """
        if getattr(self, '_parent', None):
            return getattr(self, '_parent')
        if self.parent_c_key:
            self._parent = key2obj(self.parent_c_key)
            return self._parent
        else:
            return None
        #return self.parent_c.path_ref


    def get_content(self):
        """
        A method to obtain content object associated to path object.
        """
        return key2obj(self.content_key)
        #return self.parent_c.path_ref


    @classmethod
    def get_root(cls):
        """
        A method to obtain root object
        """
        q = cls.all()
        q.filter('path =', '')
        return list(q.fetch(10))[0]


class ContentBase(DBBASEMODEL):
    """
    A base model class to store basic information of object.
    """
    TYPE = 'BASE'
    CONTENT_TYPE = 'text/html'
    CONTAINER = False

    ADD_PROPS = ('_path',)

    state = db.IntegerProperty(required = False, default = 0)
    name = db.StringProperty(required = False)

    title = db.StringProperty(required = False, default = '')
    description = db.TextProperty(required = False, default = '')
    size = db.IntegerProperty(required = False, default = 0)
    creator = db.StringProperty(required = True, default = '')

    created_at = db.DateTimeProperty(required = False, auto_now_add = True)
    modified_at = db.DateTimeProperty(required = False, auto_now_add = True)

    publish_date = db.DateTimeProperty(required = False, auto_now_add = True)

    template = db.StringProperty(required = False, default = '')

    path_key = db.StringProperty(required = False)
    #path_ref = db.ReferenceProperty(required = False)
    cparent_key = db.StringProperty(required = False)


    def get_namekey(self):
        """
        A method to obtain name and key combination from instance.
        """
        return '%s:%s' % (self.TYPE, self.key())


    def get_content_type(self):
        """
        A method to obtain content type
        """
        return self.CONTENT_TYPE


    def sync_path(self, path):
        """
        A method to set path
        """
        if not self.path_key:
            p = Path(path = path, name = self.name, created_at = self.created_at,
                     content_key = self.get_namekey(), ctype = self.TYPE)
            p.put()
            self.path_key = str(p.key())
            self.put()
        else:
            p = self.get_path_obj()
            p.path = path
            p.name = self.name
            p.created_at = self.created_at
            p.modified_at = self.modified_at
            p.content_key = self.get_namekey()
            p.put()
        self._path = path


    def delete_path(self):
        """
        A method to delete content path object.
        """
        if self.path_key:
            p = self.get_path_obj()
            p.delete()
            self.path_key = None
            self.put()


    def get_path(self):
        """
        A method to obtain path
        """
        if getattr(self, '_path', None):
            return self._path
        return self.get_path_obj().get_path()


    def get_parent(self):
        """
        A method to obtain parent object via Path object
        """
        return self.get_path_obj().get_parent()


    def get_path_obj(self):
        """
        A method to obtain path object.
        """
        return Path.get(self.path_key)


class Folder(ContentBase):
    """
    A model class to perform as folder, storeing other object in one.
    """
    TYPE = 'Folder'
    index_name = db.StringProperty(required = False)
    child_count = db.IntegerProperty(required = False, default = 0)
    BATCH_SIZE = 10
    ADDABLE = ['Page', 'Folder', 'File', 'Image']
    CONTAINER = True
    __SAVED_PROPS__ = []


    def get_child(self, name):
        """
        A method to obtain child object that has given name as its name.
        """
        q = Path.all()
        q.filter('parent_c_key =', self.get_namekey())
        q.filter('name =', name)
        pobjs = list(q.fetch(1))
        if not pobjs:
            return None
        return pobjs[0].get_content()


    def get_childs(self, start = 0, end = -1, order = '-created_at', type = None):
        """
        A method to obtain multiple child object based on given parameters
                start, end and order.
        If end is not given, it returns count of BATCH_SIZE.
        """
        q = Path.all()
        q.filter('parent_c_key =', self.get_namekey())
        if type:
            if isinstance(type, basestring):
                q.filter('ctype =', type)
            elif isinstance(type, list) or isinstance(type, tuple):
                q.filter('ctype IN', type)
        q.order(order)
        if end == -1:
            end = start+self.BATCH_SIZE
        return [x.get_content()
                for x in list(q.fetch(end-start, offset = start))]


    def add(self, obj):
        """
        A method to add child.
        """
        tp = obj.TYPE
        if '.' in tp: tp = tp.split('.')[1]
        if tp in self.ADDABLE:
            if not self.path_key:
                self.sync_path(self.name)
            # checking if the same name has already been registered as a child.
            if self.get_child(obj.name):
                raise ValueError(("The object cannot be added because "
                                  "there already be a object of the same"
                                  "name as '%s'") % obj.name)
            if not obj.path_key:
                obj.sync_path(self.get_path()+'/'+obj.name)
            obj.cparent_key = self.get_namekey()
            obj.put()
            p = obj.get_path_obj()
            p.parent_c_key = self.get_namekey()
            p.put()
            self.child_count += 1
            self.put()
        else:
            raise ValueError("'%s' cannot be added to '%s'" % \
                                    (obj.TYPE, self.TYPE))


    def remove(self, name):
        """
        A method to remove child ,which has name of given argument
            and delete it.
        """
        if not self.path_key:
            self.sync_path(self.name)
        o = self.get_child(name)
        if not o:
            raise KeyError("The object '%s' does not exist as a child" % name)
        p = o.get_path_obj()
        o.delete()
        p.delete()
        self.child_count -= 1
        self.put()


    @classmethod
    def make_root_folder(self, creator):
        """
        A method to make root folder, especialy in the initial stage.
        """
        q = Folder.all()
        if not list(q.fetch(10)):
            f = Folder(name = '', title = 'Root', creator = creator)
            f.put()
            f.sync_path('')


class Page(ContentBase):
    """
    A model class to store page information.
    """
    __SAVED_PROPS__ = []
    TYPE = 'Page'
    body = db.TextProperty(required = True, default = '')
    additional_header = db.TextProperty(required = False, default = '')


class File(ContentBase):
    """
    A model class to store file information.
    """
    __SAVED_PROPS__ = []
    TYPE = 'File'
    body = db.BlobProperty(required = True, default = '')
    filename = db.StringProperty(required = False, default = '')
    content_type = db.StringProperty(required = False,
                        default = 'application/octet-stream')


    def get_content_type(self):
        """
        A method to obtain content type
        """
        return self.content_type


class Image(File):
    """
    A model class to store file information.
    """
    __SAVED_PROPS__ = []
    TYPE = 'Image'
    width = db.IntegerProperty(required = False, default = 0)
    height = db.IntegerProperty(required = False, default = 0)


# registering ContentBase classes

types = {}

for c in dir():
    o = locals()[c]
    if o != ContentBase and isclass(o) and issubclass(o, ContentBase):
        types[c] = o

def get_content_class(name):
    """
    A function to obtain content class.
    """
    return types[name]


def register_content_class(name, klass):
    """
    A method to register content class
    """
    if name in types:
        raise ValueError('ContentType %s has been registered' % name)
    types[name] = klass

