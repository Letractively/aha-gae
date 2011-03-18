# -*- coding: utf-8 -*-

import logging
import os
import sys

def initConfig(basedir):
    """
    Initialize config object
    """
    # add the project's directory to the import path list.
    sys.path = [basedir,
              os.path.join(basedir, 'application'),
              os.path.join(basedir, 'lib')]+sys.path

    import aha
    config = aha.Config()

    # setup the templates location
    config.template_dirs = [os.path.join(basedir, 'template'),
                            'plugin']

    # set custom dispatcher
    import dispatcher
    config.dispatcher = dispatcher

    config.debug = False
    config.useappstatus = False
    if os.environ.get('SERVER_SOFTWARE', '').startswith('Dev'):
        config.debug = True

    # setting up well known config attributes
    from aha.controller import makocontroller
    makocontroller.get_lookup()
    config.template_lookup = makocontroller.tlookup

    config.page_cache_expire = 60*60*4 # 8 hours
    config.query_cache_expire = 60*60*2 # 2 hours

    # determine the app is running development server or not.
    config.debug = os.environ.get('SERVER_SOFTWARE','').lower().startswith("dev")

    if config.debug:
        config.page_cache_expire = 0  # no caceh in development envronment.
        config.query_cache_expire = 0  # no caceh in development envronment.

        # setting log level
        logging.basicConfig(level = logging.DEBUG)
    else:
        # setting log level
        logging.basicConfig(level = logging.INFO)

    # now load all the names from application.
    from application import *

    if not hasattr(config, 'auth_obj'):
        # set auth_obj  for authentication.
        from aha.auth.appengine import AppEngineAuth
        config.auth_obj = AppEngineAuth

    if not hasattr(config, 'controller_class'):
        # set controller_class if it doesn't exist.
        from aha.controller.makocontroller import MakoTemplateController
        config.controller_class = MakoTemplateController


    return config


if __name__ == '__main__':
    main()
