# -*- coding: utf-8 -*-
#
# This code is derived from helper.py on App Engine Oil
#
# dispatch.py is originally from GAE Oil, dispatch.py
#     Copyright 2008 Lin-Chieh Shangkuan & Liang-Heng Chen
#
# Copyright 2010 Atsushi Shibata
#

"""
The collection of fields definitions for coregeo 

$Id: dispatcher.py 653 2010-08-23 02:00:58Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'

__all__ = ['dispatch']

from inspect import getargspec
import logging

def dispatch(hnd):
    """
    A function to dispatch request to appropriate handler function
    """
    from aha.dispatch.router import get_router
    from app import App
    # resolve the URL
    url = hnd.request.path
    r = get_router()
    route = r.match(url)
    if route:
        # call the controller function.
        func = route['controller']
        args, varargs, varkw, defaults = getargspec(func)
        # set request and response objects.
        App.set_handler(hnd)
        App.get_controller()
        if len(args) == 1:
            route['controller'](hnd)
        else:
            route['controller']()
        App.controller.put_cookies()
        App.clear_controller()

    else:
        # No route for given url found.
        hnd.response.set_status(404)
        raise Exception('No route for url:%s' % url)


