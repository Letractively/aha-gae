# -*- coding: utf-8 -*-

##############################################################################
#
# basecontroller.py
# Definitions of basic controller.
#     delived from AppEngine Oil's controller.__init__.py
#
# Copyright (c) 2010 Webcore Corp. All Rights Reserved.
#
##############################################################################
""" basecontroller.py - Classes to handle CRUD form for a model.

$Id: basecontroller.py 638 2010-08-10 04:05:57Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'

import os
import new
import re
import logging
from Cookie import SimpleCookie

from aha import Config
from google.appengine.ext.webapp import template
from django.template import Context, Template

class BaseController(object):
    """The BaseController is the base class of action controllers.
        Action controller handles the requests from clients.
    """
    _template_ext = '.html'

    def __init__(self, hnd, params = {}):
        self.hnd = hnd
        self.controller = self
        self.response = hnd.response
        self.request = hnd.request
        self.params = params
        
        for k in self.request.arguments():
            self.params[k] = self.request.get_all(k)
            if len(self.params[k]) == 1:
                self.params[k] = self.params[k][0]

        self._controller = params['controller']
        self._action = params['action']
        self.has_rendered = False
        self.has_redirected = False
        self.__config = Config()

        self.__tpldir = os.path.join(
            self.__config.template_dir,
            self._controller
        )
        self._template_values = {}

        # implement parameter nesting as in rails
        self.params = self.__nested_params(self.params)
        
        # alias the cookies
        self.cookies = self.request.cookies

        # cookie for responce
        self.post_cookie = SimpleCookie()

        # create the session
        try:
            store = self.__config.session_store
            exec('from aha.session.%s import %sSession' %
                (store, store.capitalize()))
        
            self.session = eval('%sSession' % store.capitalize())(
                                hnd, '%s_session' % self.__config.app_name)
        except:
            raise Exception('Initialize Session Error!')

        # add request method (get, post, head, put, ....)
        env = self.request.environ
        self._request_method = env.get('REQUEST_METHOD').lower()
        
        # tell if an ajax call (X-Request)
        self._is_xhr = env.has_key('HTTP_X_REQUESTED_WITH') and \
                       env.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
        
        # add helpers
        import helper

        self.helpers = helper.get_helpers()
        try:
            import application.util.helper
        except ImportError, e:
            pass

    def before_action(self):
        pass
    
    def after_action(self):
        pass
        

    def from_json(self, json):
        """ Convert a JSON string to python object """
        from django.utils import simplejson
        return simplejson.loads(json)

    def to_json(self, obj):
        """ Convert a dict/list to JSON. Use simplejson """
        from django.utils import simplejson
        return simplejson.dumps(obj)

    def parse_opt(self, encode = 'utf-8', **opt):
        """
        A method to parse from the 'opt' argument and get a template.
        """
        content = ''
        content_path = ''
        content_type = 'text/html; charset = %s' % encode
        if opt.has_key('expires'):
            hdrs['Expires'] = opt.get('expires')
            
        if opt.has_key('html'):
            content = opt.get('html').decode('utf-8')
        elif opt.has_key('text'):
            content_type = 'text/plain; charset = utf-8'
            content = str(opt.get('text')).decode('utf-8')
        elif opt.has_key('json'):
            content_type = 'application/json; charset = utf-8'
            content = opt.get('json').decode('utf-8')
        elif opt.has_key('xml'):
            content_type = 'text/xml; charset = utf-8'
            content = opt.get('xml').decode('utf-8')
        elif opt.has_key('script'):
            content_type = 'text/javascript; charset = utf-8'
            content = opt.get('script').decode('utf-8')
        elif opt.has_key('template'):
            tpname = opt.get('template')+self._template_ext
            content_path = os.path.join(self._controller, tpname)
        elif opt.has_key('template_string'):
            contnetopt.get('template_string')
        return content, content_path, content_type

    def render(self, *html, **opt):
        hdrs = {}

        content_type = 'text/html; charset = utf-8'
        
        if html:
            content = (''.join(html)).decode('utf-8')
            content_path=''
        elif opt:
            content, content_path, content_type = self.parse_opt(**opt)
        context = self.__dict__
        if isinstance(opt.get('values'), dict):
            context.update(opt.get('values'))
        # render content as a template
        if content_path:
            t= Template(content_path)
            c = Context(context)
            result = t.render(content_path, context)
        elif content:
            t = Template(content.encode('utf-8'))
            c = Context(context)
            result = t.render(c)
        else:
            raise Exception('Render type error')

        hdrs['Content-Type'] = content_type
        hdrs.update(opt.get('hdr', {}))

        # pass the output to the response object
        r = self.response
        if hdrs:
            for k, v in hdrs.items():
                r.headers[k] = v
        r.out.write(result)

        self.has_rendered = True

    def redirect(self, url, perm = False):
        self.has_redirected = True 
        self.has_rendered = True 
                    # dirty hack, make aha don't find the template
        self.hnd.redirect(url, perm)

    def respond_to(self, **blk):
        """ according to self.params['format'] to respond appropriate stuff
        """
        if self.params.has_key('format') and \
                blk.has_key(self.params['format']):
            logging.error(self.params['format'])
            blk[self.params['format']]()

    # Helper methods for parameter nesting as in rails
    def __appender(self,dict,arr,val):
            if len(arr) > 1:
                try:
                    dict[arr[0]]
                except KeyError:
                    dict[arr[0]] = {}
                return {arr[0]: self.__appender(dict[arr[0]],arr[1:],val)}
            else:
                dict[arr[0]] = val
                return 

    def __nested_params(self, prm):
        prm2 = {}
        for param in prm:
            parray = param.replace(']', '').split('[')
            if len(parray) == 1:
                parray = parray[0].split('-')
            self.__appender(prm2, parray, prm[param])
        return prm2

def main(): pass;

