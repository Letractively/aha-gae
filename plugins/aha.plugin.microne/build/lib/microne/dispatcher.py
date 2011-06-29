# -*- coding: utf-8 -*-
#
# Copyright 2011 Atsushi Shibata
# $Id: dispatcher.py 653 2010-08-23 02:00:58Z ats $


__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'

"""
A module which has a function to dispatch coming request to handers
according to settings of the routes.
Originally Aha has a dispatcher. But aha.plugin.microne deliver requests
in different way.
This is a customized version of the dispatcher.
"""


__all__ = ['dispatch']

from inspect import getargspec
import logging

def dispatch(hnd):
    """
    A function to dispatch request to appropriate handler function.
    It receive hander object which has request/response object.
    The dispatcher uses route to determine which controller is needed for
    the request, passes them to appropriate hander.
    This function internally called by wsgi application.
    """
    from aha.dispatch.router import get_router
    from plugin.microne.app import Microne
    # resolve the URL
    url = hnd.request.path
    r = get_router()
    route = r.match(url)
    if route:
        # call the controller function.
        func = route['controller']
        args, varargs, varkw, defaults = getargspec(func)
        # set request and response objects.
        Microne.set_handler(hnd, route)
        Microne.get_controller()
        if len(args) == 1:
            route['controller'](hnd)
        else:
            route['controller']()
        Microne.controller.put_cookies()
        Microne.clear_controller()

    else:
        # No route for given url found.
        hnd.response.set_status(404)
        raise Exception('No route for url:%s' % url)


