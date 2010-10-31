# -*- coding: utf-8 -*-
#
# main.py
# A main controller for corecms,
#   dispatching request to appropriate controller
#     based on content type
#
# Copyright 2010 Atsushi Shibata
#

"""
The collection of fields definitions for coregeo 

$Id: main.py 650 2010-08-16 07:45:11Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'MIT'


import sys
import os
import re
from inspect import ismethod
from urlparse import urlparse, urlsplit
import logging

from google.appengine.api import memcache
from aha.controller.makocontroller import MakoTemplateController
from aha.controller.decorator import expose
from aha import Config
config = Config()

from aha.controller.util import get_controller_class

from model.basictype import *

DLMT = '/'

def get_path_obj(path, in_rest = []):
    """
    A function to obtain Path object from given url
    """
    if path.endswith('/'): path = path[:-1]
    # try to find full url
    q = Path.all()
    q.filter('path =', path)
    #if q.count(10):
    pl = list(q.fetch(1))
    if pl:
        p = pl[0]
        rest = path.replace(p.get_path(), '')
        return p, (rest.split(DLMT)+in_rest)[1:]

    pl = path.split(DLMT)

    #if path object couldn't be found,
    #  try to find another one removing the tail.
    return get_path_obj(DLMT.join(pl[:-1]), [pl[-1]]+in_rest)


def dispatch(hnd, path, params):
    """
    A function to call appropriate controller and metod, 
        according to given path object and action
    """
    # getting controller from the object type in given path object.
    action = ''
    if params:
        action = params[0]
        params = params[1:]
    # If content type includes '.', it means 'PLUGINNAME.CONTENTTYPE'
    if '.' in path.ctype:
        plugin, controller = path.ctype.split('.')
        ctrl_clz = get_controller_class(controller, plugin)
    else:
        controller = path.ctype
        ctrl_clz = get_controller_class(controller)

    # create a controller instance
    ctrl = ctrl_clz(hnd, {'controller':controller.lower(),
                        'action':action})

    # assigning common objects to controller instance
    #    so that these can be used in template
    ctrl.controller = ctrl                    # contrlller itself
    ctrl.path_obj = hnd.path_obj              # Path object
    ctrl.content = hnd.path_obj.get_content() # content object
    ctrl.site_data = SiteData.get_data()      # site_data object

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
                         hnd.request.url, controller, action)

    # setting action to index, in case the action is not given.
    if not action: action = 'index';

    # getting action method from the controller instance.
    actionmethod = getattr(ctrl, action, None)

    # if the action is none ,
    #   or it is not decorated by using expose, raise exception
    #   to avoid unintended method traversal.
    if not actionmethod or not getattr(actionmethod, '_exposed_', False):
        if not os.environ.get('SERVER_SOFTWARE', '').startswith('Dev'):
            try:
                PAGE_CACHE_EXPIRE = config.page_cache_expire
            except:
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
            actionmethod(*params)
        else:
            actionmethod(*([ctrl]+params))
        ctrl.after_action()

    #check status
    st = ctrl.response._Response__status[0]
    if st >= 400:
        # error occured
        raise Exception('%s %s' % ctrl.response._Response__status)

    if not ctrl.has_rendered:
        ctrl.render(template = action, values = ctrl.__dict__)

    # manage cookies
    if ctrl.post_cookie.keys():
        c = ctrl.post_cookie
        cs = c.output().replace('Set-Cookie: ', '')
        ctrl.response.headers.add_header('Set-Cookie', cs)


class MainController(MakoTemplateController):
    """
    The Controller for universal access.
    """

    @expose
    def index(self):
        """
        A method to show list of published object.
        """
        p = urlsplit(self.request.url)[2]
        c = memcache.get(p)
        try:
            if c:
                # in case a given url has cached, we use it to make a response.
                resp = self.response
                r = self.response.out
                r.write(c['body'])
                for k, i in c['hdr'].items():
                    resp.headers[k] = i
                self.has_rendered = True
                self.cached = True
                return
        except:
            pass

        sc, loc, path, param, q, f = urlparse(self.request.url)
        p, m = get_path_obj(path)
        self.path_obj = p
        if config.debug:
            dispatch(self, p, m)
            self.has_rendered = True
        else:
            try:
                dispatch(self, p, m)
                self.has_rendered = True
            except Exception, e:
                # Display error page
                if config.error_template:
                    self.error = e
                    self.render(template = config.error_template)
                else:
                    raise e

