# -*- coding: utf-8 -*-

import logging
import os

def appConfig():
    import aha
    config = aha.Config()

    # setting up well known config attributes
    config.initial_user = ['test@example.com', 'shib.ats@gmail.com', 'ats']
    config.site_root = 'http://coreblog.org'
    config.error_template = '/common/error'
    config.logout_url = '/logout'

    config.page_cache_expire = 60*60*4 # 8 hours
    config.query_cache_expire = 60*60*2 # 2 hours

    if not hasattr(config, 'site_admin_menus'):
        config.site_admin_menus = [
            ('/style/img/edit_icon.gif', 'Site setting', '/_edit_sitedata' ),
            ]

    # initialize route and the installed plugins
    from aha.dispatch import router
    # initialize router with fallback rule.
    fb = [router.Rule('.*', controller = 'main', action = "index")]
    r = router.Router(fallback = fb)
    # urls for admin interfaces
    r.connect('^/_edit_sitedata', controller = 'sitedata', action = 'edit')

    """
    from plugin.twitteroauth.twitter_auth import TwitterOAuth
    config.auth_obj = TwitterOAuth

    # route fot oauth redirector.
    r.connect('^/_oauth', controller = 'twitteroauth')

    config.consumer_key = 'wILd7AIBlLUTQNkMk4Aew'
    config.consumer_secret = 'CjalJllTlWAZIaqElA8egqsWFWLBkxAWNQNvjDUvwk'
    """

    # set the default authenticate function
    from util.authenticate import admin
    config.admin_auth = admin
    config.debug = True
    config.useappstatus = False

    if config.debug:
        from aha.auth.appengine import AppEngineAuth
        config.auth_obj = AppEngineAuth
        """
        from plugin.user.datastoreauth import DataStoreAuth
        config.auth_obj = DataStoreAuth
        config.login_url = '/login'
        """

        config.page_cache_expire = 0  # no caceh in development envronment.
        config.query_cache_expire = 0  # no caceh in development envronment.

        config.site_root = 'http://127.0.0.1:8080'
        # setting log level
        logging.basicConfig(level = logging.DEBUG)
    else:
        # setting log level
        logging.basicConfig(level = logging.DEBUG)


if __name__ == '__main__':
    main()
