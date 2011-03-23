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
    """
    The authentication plugin class for App Engine native Google authentication.
    which is derived from BaseAuth.
    You may set class object to config object to use it.
    Write following code to config.py.::
    
        from aha.auth.appengine import AppEngineAuth
        config.auth_obj = AppEngineAuth
    
    """

    TYPE = 'appenginegoogle'

    def auth(self, ins, *param, **kws):
        """
        A method to perform authentication, or
        to check if the authentication has been performed.
        It returns true on success, false on failure.

        :param ins: The controller instance.
        :param param: parameter to the authentication function.
        :param kws: keyword argument to the authentication function.

        """
        u = users.get_current_user()
        if not u:
            return False
        return True


    def auth_redirect(self, ins, *param, **kws):
        """
        A method to perform redirection
        when the authentication fails, user doesn't have privileges, etc.
        It redirects access to the URL that App Engine's User service gives.

        :param ins: The controller instance.
        :param param: parameter to the authentication function.
        :param kws: keyword argument to the authentication function.
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
        It gets user information via App Engine's User service.

        :param ins: The controller instance.
        :param param: parameter to the authentication function.
        :param kws: keyword argument to the authentication function.
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


    def logout(self, ins, *param, **kws):
        """
        A method to perform logout action.
        Typically it's called from authenticate decorator.
        It redirects to the logout URL that App Engine's User service gives.

        :param ins: The controller instance.
        :param param: parameter to the authentication function.
        :param kws: keyword argument to the authentication function.
        """
        dest_url = ins.request.referer
        ins.redirect(create_logout_url(dest_url))


def main(): pass;

