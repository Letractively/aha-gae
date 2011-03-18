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

import re
import logging
from inspect import ismethod
from urlparse import urlsplit

from router import get_router, get_fallback_router
import sys 
import os
from traceback import *

from google.appengine.api import memcache

from aha import Config
from aha.controller.util import get_controller_class

def dispatch(hnd):
    """
    A function to dispatch request to appropriate handler class
    """
    # resolve the URL
    url = hnd.request.path
    r = get_router()
    route = r.match(url)

    if not route:
        fr = get_fallback_router()
        fr.match(url)
        route = fr.match(url)
        if not route:
            # raise exception because we couldn't find route for given url
            hnd.response.set_status(404)
            raise Exception('No route for url:%s' % url)

    # create the appropriate controller
    ctrlname = route['controller']
    plugin = ''
    if '.' in ctrlname:
        plugin, ctrlname = ctrlname.split('.')
    ctrl_clz = get_controller_class(ctrlname, plugin)

    # create a controller instance
    ctrl = ctrl_clz(hnd, route)
    #setting attributes

    # mixin application base controller
    try:
        exec('from controller import application') in globals()
        if application.Application not in ctrl_clz.__bases__:
            ctrl_clz.__bases__ += (application.Application,)
        if hasattr(ctrl, 'application_init'):
            ctrl.application_init()
    except:
        pass

    # dispatch
    logging.debug('URL "%s" is dispatched to: %sController#%s',
                 url,
                 route['controller'].capitalize(),
                 route.get('action', 'index'))

    ctrl.config = Config()

    # get the action from the controller
    actionmethod = getattr(ctrl, route.get('action', 'index'), None)

    # if the action is none ,
    #   or it is not decorated by using expose, raise exception
    #   to avoid unintended method traversal.
    if not actionmethod or not getattr(actionmethod, '_exposed_', False):
        if not ctrl.config.debug:
            try:
                PAGE_CACHE_EXPIRE = config.page_cache_expire
            except AttributeError:
                PAGE_CACHE_EXPIRE = 60*60
            p = urlsplit(hnd.request.url)[2]
            memcache.set(p, 'error', PAGE_CACHE_EXPIRE)
            logging.debug('%s is cahed as a error page' % p)
        ctrl.response.set_status(404)
        m = '%s %s (Method not found)'
        raise Exception(m % ctrl.response._Response__status)

    # if before_action returns False, terminate the remain action
    if ctrl.before_action() != False:
        if ismethod(actionmethod):
            actionmethod()
        else:
            actionmethod()
        ctrl.after_action()

    #check status
    st = ctrl.response._Response__status[0]
    if st >= 400:
        # error occured
        raise Exception('%s %s' % ctrl.response._Response__status)

    if not ctrl.has_rendered and not ctrl.has_redirected:
        ctrl.render(template = route['action'], values = ctrl.__dict__)

    ctrl.put_cookies()
