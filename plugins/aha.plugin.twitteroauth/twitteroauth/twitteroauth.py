# -*- coding: utf-8 -*-
#
# twitterauth.py
# A controller for OAuth.
#
# Copyright 2010 Atsushi Shibata
#
"""
A controller for OAuth.

$Id: twitterauth.py 649 2010-08-16 07:44:47Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'MIT'

from google.appengine.api import memcache

from aha.controller.makocontroller import MakoTemplateController
from aha.controller.decorator import expose
from plugin.twitteroauth.twitter_auth import (TwitterOAuth, TWITTER_NAMESPACE,
                                       OAUTH_ACCESS_TOKEN_COOKIE, EXPIRE)

class TwitteroauthController(MakoTemplateController):
    """
    A controller to set parameters in cookie sent from twitter.
    It works after redirection from twitter's site
    after user pushes allow button.
    It receives authentication id in get parameter, 
    obtain user information at index() method
    and set informations of user to memcache.
    """


    def __init__(self, hnd, params = {}):
        """
        An initialize method.
        """
        super(TwitteroauthController, self).__init__(hnd, params)
        self.auth_obj = None
        


    @expose
    def index(self):
        """
        A method to receive redirection from twitter's site.
        Twitter gives token to an application by using 
        oauth_token get parameter.
        """
        token = self.params.get('oauth_token')
        self.auth_obj = TwitterOAuth()
        self.auth_obj.request = self.request
        self.auth_obj.request.args = self.request.params
        self.auth_obj.get_authenticated_user(self._post_action)


    def _post_action(self, user):
        """
        A method to put twitter user information to memcache
        and redirect to original page.
        It is called via callback set to get_authenticated_user() method.
        The method obtain user information from twitter, pass it to this
        method. This method stores the information to memcache.
        
        :param user : user information of twitter.
        """
        if user:
            d = {'type':TwitterOAuth.TYPE,
               'nickname':user.get('username', ''),
               'email':'',
               'userid':user.get('id', ''),
               'realname':user.get('name', ''),
               'icon_url':user.get('profile_image_url', ''),
               }
            token = user.get('access_token', '')
            if token:
                if token.get('secret', '') and token.get('key', ''):
                    d['access_secret'] = token.get('secret', '')
                    d['access_key'] = token.get('key', '')
            memcache.set(self.cookies.get(OAUTH_ACCESS_TOKEN_COOKIE),
                         d, namespace = TWITTER_NAMESPACE, time = EXPIRE)
            rurl = self.session.get('referer', '')
            if rurl:
                # clear 'referer' key in session object.
                del self.session['referer']
                self.session.put()
                self.redirect(rurl)
            else:
                self.redirect('/')

        self.render('blank')


    def twitter_request(self, path, access_token, callback = None,
                           post_args = None, **args):
        """
        A method to send request to twitter, by using informations in auth_obj.
        """
        api = self.auth_obj
        if not api:
            raise ValueError(("auth_obj is None. You must do "
                              "oauth authentication before sending request."))
        if not callback:
            callback = self._dummy_callback
        api.twitter_request(
                    path,
                    post_args = post_args,
                    access_token = access_token,
                    callback = callback)


    def _dummy_callback(self, arg):
        """
        Dummy callback. Do nothing.
        """
        pass


def main(): pass;

if __name__ == '__main__':
    main()
