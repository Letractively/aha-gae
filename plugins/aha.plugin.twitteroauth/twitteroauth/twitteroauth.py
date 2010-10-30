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
    A controller to set parameters in cookie sent from twitter
    """

    @expose
    def index(self):
        token = self.params.get('oauth_token')
        oa = TwitterOAuth()
        oa.request = self.request
        oa.request.args = self.request.params
        oa.get_authenticated_user(self._post_action)

    def _post_action(self, user):
        """
        A method to put twitter user information to memcache
            and redirect to original page
        """
        if user:
            d = {'type':TwitterOAuth.TYPE,
               'nickname':user.get('username', ''),
               'email':'',
               'userid':user.get('user_id', ''),
               'realname':user.get('name', ''),
               'icon_url':user.get('profile_image_url', ''),
               }
            memcache.set(self.cookies.get(OAUTH_ACCESS_TOKEN_COOKIE),
                         d, namespace = TWITTER_NAMESPACE, time = EXPIRE)
            rurl = self.session['referer']
            del self.session['referer']
            self.session.put()
            if rurl:
                self.redirect(rurl)
            else:
                self.redirect('/')

        self.render(template = '/common/blank')


def main(): pass;

if __name__ == '__main__':
    main()
