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

import router
import sys 
import os
from traceback import *
from aha import Config

from aha.controller.util import get_controller_class

def dispatch(hnd):
    """
    A function to dispatch request to appropriate handler class
    """
    # resolve the URL
    url = hnd.request.path
    r = router.Router()
    route = r.resolve(url)

    if route is None:
        # raise exception because we couldn't find route for given url
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
                 route['action'])

    ctrl.config = Config()

    # get the action from the controller
    actionmethod = getattr(ctrl, route['action'], None)
    if actionmethod:
        # if before_action returns True,
        # terminate the remain action
        if ctrl.before_action() != False:
            if ismethod(actionmethod):
                actionmethod()
            else:
                actionmethod(*[ctrl])
            ctrl.after_action()

        if not ctrl.has_rendered:
            ctrl.render(template = route['action'],
                        values = ctrl.__dict__)
        # setting cookie
        if ctrl.post_cookie.keys():
            c = ctrl.post_cookie
            cs = c.output().replace('Set-Cookie: ', '')
            ctrl.response.headers.add_header('Set-Cookie', cs)

    else: # invalid action
        errstr = 'Invalid action `%s` in `%s`' % \
                                (route['action'], route['controller'])
        logging.error(errstr)
        raise Exception(errstr)
