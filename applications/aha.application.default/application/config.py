# -*- coding: utf-8 -*-

# config.py
#
# The application specific configulation comes here.
#

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'


import logging

def appConfig():
    import aha
    config = aha.Config()

    # your custom configurations follows
    # config.foo_config = 'spamspamspam'

    # your route follows.
    from aha.dispatch.router import get_router, get_fallback_router
    # set the fallback route leading to object structure dispatcher
    fr = get_fallback_router()
    fr.connect(r'*url', controller = 'main', action = 'index')

    config.debug = True
    config.useappstatus = False # Make it 'True' if you want to use appstats

    if config.debug:
        logging.basicConfig(level = logging.DEBUG)
    else:
        # setting log level
        logging.basicConfig(level = logging.DEBUG)


if __name__ == '__main__':
    main()
