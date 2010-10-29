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
    from aha.dispatch import router
    # initialize router with fallback rule.
    fb = [router.Rule('.*', controller = 'main', action = "index")]
    r = router.Router(fallback = fb)

    config.debug = True
    config.useappstatus = False # Make it 'True' if you want to use appstats

    if config.debug:
        logging.basicConfig(level = logging.DEBUG)
    else:
        # setting log level
        logging.basicConfig(level = logging.DEBUG)


if __name__ == '__main__':
    main()
