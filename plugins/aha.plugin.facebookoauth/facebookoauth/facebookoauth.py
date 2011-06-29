# -*- coding: utf-8 -*-
#
# twitterauth.py
# A controller for OAuth.
#
# Copyright 2010 Atsushi Shibata
#
"""
A controller for OAuth.

$Id: facebookoauth.py 352 2011-06-29 00:22:09Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'MIT'

from google.appengine.api import memcache

from aha.controller.makocontroller import MakoTemplateController
from aha.controller.decorator import expose
from plugin.facebookoauth.facebook_auth import (FacebookOAuth,
                     FACEBOOK_NAMESPACE, OAUTH_ACCESS_TOKEN_COOKIE, EXPIRE)

class FacebookoauthController(MakoTemplateController):
    """
    A controller to set parameters in cookie sent from facebook
    """


    def __init__(self, hnd, params = {}):
        """
        Initialize method
        """
        super(FacebookoauthController, self).__init__(hnd, params)
        self.auth_obj = None


    @expose
    def index(self):
        token = self.params.get('oauth_token')
        self.auth_obj = FacebookOAuth()
        self.auth_obj.controller = self
        self.auth_obj.request = self.request
        self.auth_obj.request.args = self.request.params
        self.auth_obj.get_authenticated_user(self._post_action)


    def _post_action(self, user):
        """
        A method to put facebook user information to memcache
            and redirect to original page
        """
        if user:
            d = {'type':FacebookOAuth.TYPE,
               'nickname':user.get('username', '') or user.get('name', ''),
               'email':'',
               'userid':user.get('uid', ''),
               'realname':user.get('name', ''),
               'icon_url':user.get('pic_square', ''),
               }
            memcache.set(self.cookies.get(OAUTH_ACCESS_TOKEN_COOKIE),
                         d, namespace = FACEBOOK_NAMESPACE, time = EXPIRE)
            rurl = self.session.get('referer', '')
            if rurl:
                del self.session['referer']
            self.session.put()
            if rurl:
                self.redirect(rurl)
            else:
                self.redirect('/')

        self.render(' ')



def main(): pass;

if __name__ == '__main__':
    main()
