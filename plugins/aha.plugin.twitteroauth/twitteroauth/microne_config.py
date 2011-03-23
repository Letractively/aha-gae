# -*- coding: utf-8 -*-
"""
    tipfy.ext.auth.microne_config
    ~~~~~~~~~~~~~~~~~~~~~~

    A module for configuration functions for microne plugin.
"""
import logging
import aha
config = aha.Config()

__all__ = ['initConfig']


def initConfig(app, consumer_key, consumer_secret,
              oauth_redirect_path = '/oauth'):
    """
    A function to make configuration of twitter authentication for microne.
    Arguments :
    :param app             : App object of microne
    :param consumer_key    : Twitter consumer_key
    :param consumer_secret : Twitter consumer_secret
    """
    # set auth_obj  for authentication.
    from plugin.twitteroauth.twitter_auth import TwitterOAuth
    from plugin.twitteroauth.twitteroauth import TwitteroauthController

    # set up config attributes.
    config.auth_obj = TwitterOAuth
    config.consumer_key = consumer_key
    config.consumer_secret = consumer_secret

    @app.route(oauth_redirect_path)
    def oauth():
        """
        A function to receive oauth redirection.
        It passes information in url to TwitteroauthController._post_action()
        """
        controller = TwitteroauthController(app.get_handler())
        auth_obj = TwitterOAuth()
        auth_obj.request = app.request
        auth_obj.request.args = app.request.params
        auth_obj.get_authenticated_user(controller._post_action)
