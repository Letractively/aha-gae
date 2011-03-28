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
from urlparse import urlsplit
from Cookie import SimpleCookie

from aha import Config
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from django.template import Context, Template

from aha.controller.decorator import cache


class BaseController(object):
    """
    The BaseController is the base class of action controllers.
    Action controller handles the requests from clients.
    """
    _template_ext = '.html'

    def __init__(self, hnd, params = {}):
        """
        An initialization method. It sets some attributes for combenience.
        
        :param hnd     : a request object.
        :param params  : parameters given via dispacher.
        """
        self.hnd = hnd                  # hander itsrlf
        self.controller = self          # controller object
        self.response = hnd.response    # response object
        self.request = hnd.request      # request object
        self.params = params            # parameters

        # update parameters when some GET/POST parameters are given.
        for k in self.request.arguments():
            self.params[k] = self.request.get_all(k)
            if len(self.params[k]) == 1:
                self.params[k] = self.params[k][0]

        self._controller = params.get('controller', '') # controller as a string
        self._action = params.get('action', 'index') # action as a string
        self.has_rendered = False               # reset the rendering flag
        self.has_redirected = False             # reset the redirect flag
        self.__config = Config()                # config object

        self.__tpldir = os.path.join(
            self.__config.template_dir,
            self._controller
        )                                       # default template directory
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
        """
        A method called right before render() method.
        You can do pre render jobs in this method, something like caching, etc.
        """
        pass
    
    def after_action(self):
        """
        A method called right after render() method.
        """
        pass
        

    def from_json(self, json):
        """
        Convert a JSON string to python object.
        """
        from django.utils import simplejson
        return simplejson.loads(json)

    def to_json(self, obj):
        """
        Convert a dict/list to JSON. Use simplejson.
        """
        from django.utils import simplejson
        return simplejson.dumps(obj)

    def parse_opt(self, encode = 'utf-8', **opt):
        """
        A method to parse the 'opt' argument and get a template.
        It gets options as a keyword argument and parse them.
        
        :param template    : path to the template file.
        :param html        : raw html for the output.
        :param text        : raw text for the output.
        :param json        : raw json for the output.
        :param xml         : raw xml for the output.
        :param script      : raw java script for the output.
        :param encode      : encode for the output.
        :param expires     : expire date as a string.
        """
        content = ''
        template_path = ''
        content_type = 'text/html; charset = %s' % encode
        if opt.has_key('expires'):
            hdrs['Expires'] = opt.get('expires')
            
        if opt.has_key('html'):
            content = opt.get('html').decode('utf-8')
        elif opt.has_key('text'):
            content_type = 'text/plain; charset = %s' % encode
            content = opt.get('text')
        elif opt.has_key('json'):
            content_type = 'application/json; charset = %s' % encode
            content = opt.get('json')
        elif opt.has_key('xml'):
            content_type = 'text/xml; charset = %s' % encode
            content = opt.get('xml')
        elif opt.has_key('script'):
            content_type = 'text/javascript; charset = %s' % encode
            content = opt.get('script')
        elif opt.has_key('template'):
            tpname = opt.get('template')+self._template_ext
            template_path = os.path.join(self._controller, tpname)
        return content, template_path, content_type

    def render(self, *html, **opt):
        """
        A method to render output.
        In BaseController, it uses App Engine's default Django template.
        You may override this method when you make your own controller class
        that uses other template engine.

        It receives template string as non keyword argument, and
        following arguments.

        :param template    : path to the template file.
        :param html        : raw html for the output.
        :param text        : raw text for the output.
        :param json        : raw json for the output.
        :param xml         : raw xml for the output.
        :param script      : raw java script for the output.
        :param encode      : encode for the output.
        :param expires     : expire date as a string.
        :param context     : the context dictionaly passed to template.
        In case this argument doesn't exist, controller object will be used
        as the context.
        """

        hdrs = {}

        content_type = 'text/html; charset = utf-8'
        if html:
            content = u''.join(html)
            content_path = ''
            template_path = ''
        elif opt:
            content, template_path, content_type = self.parse_opt(**opt)
        context = opt.get('context', self.__dict__)
        if isinstance(opt.get('values'), dict):
            context.update(opt.get('values'))
        # render content as a template
        if template_path:
            t= Template(template_path)
            c = Context(context)
            result = t.render(context)
        elif content:
            result = content
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

    def put_cookies(self):
        """
        A method to put cookies to the response,
        called in dispatch function,
        or after render(), redirect() or called  etc.
        """
        if self.post_cookie.keys():
            c = self.post_cookie
            cs = c.output().replace('Set-Cookie: ', '')
            self.response.headers.add_header('Set-Cookie', cs)

    def redirect(self, url, perm = False):
        """
        A method to redirect response.
        
        :param url: the URL to redirect.
        """
        self.has_redirected = True 
        self.has_rendered = True 
                    # dirty hack, make aha don't find the template
        self.hnd.redirect(url, perm)

    def respond_to(self, **blk):
        """
        according to self.params['format'] to respond appropriate stuff
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

