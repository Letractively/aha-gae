# -*- coding: utf-8 -*-

# config.py
#
# The application specific configulation comes here.
#

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'

import logging
import os

def appConfig():
    import aha
    config = aha.Config()
    # initialize route and the installed plugins
    from aha.dispatch.router import get_router, get_fallback_router
    # initialize router with default rule.
    r = get_router()

    # setting up well known config attributes

    # put initial user to access admin interface at the first time.
    config.initial_user = ['test@example.com']
    # put your site root here.
    config.site_root = 'http://your.site'

    config.error_template = '/common/error'
    config.logout_url = '/logout'

    config.page_cache_expire = 60*60*4 # 8 hours
    config.query_cache_expire = 60*60*2 # 2 hours

    if not hasattr(config, 'site_admin_menus'):
        config.site_admin_menus = [
            ('/style/img/edit_icon.gif', 'Site setting', '/_edit_sitedata' ),
            ]

    # urls for admin interfaces
    r.connect(r'/_edit_sitedata', controller = 'sitedata', action = 'edit')

    # set the default authenticate function
    from util.authenticate import admin
    config.admin_auth = admin
    from aha.auth.appengine import AppEngineAuth
    config.auth_obj = AppEngineAuth

    # set the fallback route leading to object structure dispatcher
    fr = get_fallback_router()
    fr.connect(r'*url', controller = 'main', action = 'index')

    if config.debug:
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
