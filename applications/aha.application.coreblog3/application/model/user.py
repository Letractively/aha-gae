# -*- coding: utf-8 -*-
#
# users.py
# A collection of model classes, that store information for users.
#
# Copyright 2010 Atsushi Shibata
#
"""
A collection of model classes, that store information for users.

$Id: forms.py 649 2010-08-16 07:44:47Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'MIT'


__all__ = ['User']

from google.appengine.ext import db
#from google.appengine.ext.db import Model as DBBASEMODEL
try:
    from aha.model.cachedmodel import CachedModelBase as DBBASEMODEL
except:
    from google.appengine.ext.db import Model as DBBASEMODEL

class User(DBBASEMODEL):
    """
    A model class for users.
    """
    __SAVED_PROPS__ = []
    TYPE = 'User'
    userid = db.StringProperty(required = False, default = '')
    nickname = db.StringProperty(required = False, default = '')
    realname = db.StringProperty(required = False, default = '')
    email = db.StringProperty(required = False, default = '')
    description = db.TextProperty(required = False, default = '')

    hash = db.StringProperty(required = False, default = '')

    auth_key = db.StringProperty(required = False, default = '')

    groups = db.ListProperty(item_type = str)

    created_at = db.DateTimeProperty(required = False, auto_now_add = True)
    modified_at = db.DateTimeProperty(required = False, auto_now_add = True)
    last_login = db.DateTimeProperty(required = False, auto_now_add = True)


class Group(DBBASEMODEL):
    """
    A model class for groups.
    """
    __SAVED_PROPS__ = []
    TYPE = 'Group'
    groupid = db.StringProperty(required = False, default = '')
    title = db.StringProperty(required = False, default = '')
    description = db.TextProperty(required = False, default = '')

    created_at = db.DateTimeProperty(required = False, auto_now_add = True)
    modified_at = db.DateTimeProperty(required = False, auto_now_add = True)

