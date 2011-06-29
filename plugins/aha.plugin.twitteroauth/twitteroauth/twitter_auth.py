# -*- coding: utf-8 -*-

##############################################################################
#
# twitteroauth.py
# A module to provide auth handler of Twitter OAuth,
#                            stores user data in memcache.
#
# Copyright (c) 2010 Webcore Corp. All Rights Reserved.
#
##############################################################################
""" twitteroauth.py
A module to provide auth handler of Twitter OAuth, 
                        stores user data in memcache.

$Id: appengine.py 638 2010-08-10 04:05:57Z ats $
"""

import logging

from google.appengine.api import memcache

from aha.auth.base import BaseAuth
from plugin.twitteroauth.twitter import TwitterMixin

TWITTER_NAMESPACE = 'twitter_login_users'
OAUTH_ACCESS_TOKEN_COOKIE = '_oauth_request_token'

EXPIRE = 60*60*24*7

class TwitterOAuth(BaseAuth, TwitterMixin):
    """
    A class to performs authentication via twitter oauth authentication.
    When you want to use twitter authentication in aha application,
    you may set auth_obj in configuration in config.py like following:
    
        from plugin.twitteroauth.twitter_auth import TwitterOAuth
        config.auth_obj = TwitterOAuth
    
    You may also set consume key and consume secret 
    for you twitter application.::

        config.consumer_key = '8tvBBBU4P8SqPypC1X4tpA'
        config.consumer_secret = 'RGdpAxEnuETjKQdpDxsJkR67Ki16st6gfv4URhfdM'
    
    """
    TYPE = 'twitter'

    def auth(self, ins, *param, **kws):
        """
        A method to perform authentication, or
        to check if the authentication has been performed.
        It returns true on success, false on failure.
        
        :param ins      : a controller instance.
        :param param    : parameters to be passed to authentication function.
        :param kws      : keyword arguments to be passed to authentication
        funciton.
        """
        u = self.get_user(ins, *param, **kws)
        if not u:
            return False
        return True


    def auth_redirect(self, ins, *param, **kws):
        """
        A method to perform redirection
        when the authentication fails, user doesn't have privileges, etc.

        :param ins      : a controller instance.
        :param param    : parameters to be passed to authentication function.
        :param kws      : keyword arguments to be passed to authentication
        funciton.
        """
        self.controller = ins
        url = self.authenticate_redirect()
        if not url:
            raise ValueError("authenticate_redirect() didn't return url.")
        
        ins.redirect(url)

    @classmethod
    def get_user(cls, ins):
        """
        A method to return current login user.
        It returns user dict if the user is logging in,
        None if doesn't.

        :param ins      : a controller instance.
        funciton.
        """
        key = ins.cookies.get(OAUTH_ACCESS_TOKEN_COOKIE, '')
        if key:
            user = memcache.get(key, namespace = TWITTER_NAMESPACE)
            if user: return user;

        return {}

    @classmethod
    def clear_user(cls, ins):
        """
        A method to clear current user in memcache.

        :param ins      : a controller instance.
        funciton.
        """
        key = ins.cookies.get(OAUTH_ACCESS_TOKEN_COOKIE, '')
        if key:
            memcache.delete(key, namespace = TWITTER_NAMESPACE)

        return {}


    def set_cookie(self, key, data):
        """
        A method to set cookie.
        It is called during auth_redirect() is called internally.
        """
        logging.debug('set cookie')
        self.controller.post_cookie[key] = data
        self.controller.post_cookie[key]['path'] = '/'


def main(): pass;

