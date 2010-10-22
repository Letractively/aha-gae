# -*- coding: utf-8 -*-

##############################################################################
#
# appengine.py
# A module to provide auth handler of App Engine's Google Authentication.
#
# Copyright (c) 2010 Webcore Corp. All Rights Reserved.
#
##############################################################################
""" appengine.py - A module to provide auth handler of
                App Engine's Google Authentication.

$Id: appengine.py 638 2010-08-10 04:05:57Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'

from google.appengine.api import users
from aha.auth.base import BaseAuth
from urlparse import urlsplit

class AppEngineAuth(BaseAuth):
    TYPE = 'appenginegoogle'

    def auth(self, ins, *param, **kws):
        """
        A method to perform authentication, or
            to check if the authentication has been performed.
        It returns true on success, false on failure.
        """
        u = users.get_current_user()
        if not u:
            return False
        return True


    def auth_redirect(self, ins, *param, **kws):
        """
        A method to perform redirection
            when the authentication fails, user doesn't have privileges, etc.
        """
        #path = urlsplit(ins.request.url)[2]
        #me.session['referer'] = config.site_root+path
        url = users.create_login_url(ins.request.url)
        ins.redirect(url)


    def get_user(self, ins, *param, **kws):
        """
        A method to return current login user.
        It returns user dict if the user is logging in,
            None if doesn't.
        """
        u = users.get_current_user()
        if u:
            return {'type':self.TYPE,
                    'nickname':u.nickname(),
                    'email':u.email(),
                    'userid':u.user_id(),
                    'realname':u.nickname(),
                    }
        else:
            return {}


def main(): pass;

