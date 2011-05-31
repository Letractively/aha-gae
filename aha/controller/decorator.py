# -*- coding: utf-8 -*-

##############################################################################
#
# decorators.py
# A bunch of functions that work as decorators for controller methods.
#
# Copyright (c) 2010 Webcore Corp. All Rights Reserved.
#
##############################################################################
"""\
decorators.py - A bunch of functions that work as decorators
for controller methods.

$Id: decorator.py 6 2011-05-12 10:36:45Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'

__all__ = ('authenticate', 'expose', 'cache' )

import logging
from urlparse import urlsplit
from base64 import b64decode

from google.appengine.api import memcache

import aha
config = aha.Config()

class authenticate(object):
    """
    A decorator that catch method access, check authentication, 
    redirect is authentication needs.
    You may decorate handler methods in controllers like this::
    
        @authenticate()
        def some_funk(self):
            # your code here...
    
    """
    def __init__(self, check_func = None, auth_obj = None, *args, **kws):
        """
        An initialization method of decorator.
        The auth_obj argument is a object to perform authentication function.
        If auth_obj is given, __call__() uses it instead of
        one in config object.
        Otherwise, it uses default authentication given in config object.
        The check_funk argument is a hook method called after authentication.
        If chack_funk is given, __call__() method calls it
        after authentication.

        :param check_func       : a function called before authentication.
        :param auth_obj         : an authentication object.
        :param args             : a arguments to be passed to __call__().
        :param kws              : a keyword arguments to be passed to __call__().

        
        """
        self.args = args
        self.kws = kws
        if not hasattr(config, 'auth_obj') and not auth_obj:
            raise ValueError(("""You must specify auth_obj in config """
                              """argument"""))
        if auth_obj:
            self.auth_obj = auth_obj
        else:
            self.auth_obj = config.auth_obj
        self.check_func = check_func


    def __call__(self, func, *args, **kws):
        """
        A method that actually called as a decorator.
        It returns wrapped function(execute) so that the function
        works every time parent function is called.
        
        :param func         : a function to be decorated.
        """
        self.func = func
        def execute(me):
            try:
                if 'referer' not in me.session:
                    path = urlsplit(me.request.url)[2]
                    me.session['referer'] = config.site_root+path
                    me.session.put()
            except:
                pass
            aobj = self.auth_obj()
            auth_res = aobj.auth(me, *self.args, **self.kws)
            if auth_res and self.check_func:
                check_res = self.check_func(me, *self.args, **self.kws)
                if not check_res:
                    me.response.set_status(403)
                    aobj.auth_redirect(me, *self.args, **self.kws)
                    return

            if auth_res:
                return self.func(me, *args, **kws)
            aobj.auth_redirect(me, *self.args, **self.kws)

        return execute


class basicauth(object):
    """
    A decorator that catch method access, supply BASIC authentication.
    You may decorate handler methods in controllers like this::
    
        @basicauth()
        def some_funk(self):
            # your code here...
    
    """

    def __init__(self, user = None, password = None, realm = None):
        """
        An initialization method of decorator.
        Authentication information can be passed at initialization time,
        by using arguments. In case no arguments gives, it uses informations
        at configration.
        
        :param user         : an user name of BASIC authentication.
        :param password     : a passowrd of BASIC authentication.
        :param realm        : a realm of BASIC authentication.
        """
        if user is None or password is None:
            user = config.basicauth_user
            password = config.basicauth_password
        if realm is None:
            if hasattr(config, 'realm'):
                realm = config.realm
            else:
                realm = 'Auth'
        self.user = user
        self.password = password
        self.realm = realm


    def __call__(self, func, *args, **kws):
        """
        A method that actually called as a decorator.
        It performs BASIC authentication, checking header and return special
        header for authentication.
        
        :param func         : a function to be decorated.
        """
        self.func = func
        def execute(me):
            auth_header = me.request.headers.get('Authorization', '')
            if auth_header.split():
                scheme, code = auth_header.split()
            else:
                scheme = 'Basic'
                code = ''
            if scheme != 'Basic':
                raise ValueError('The authentication scheme is not BASIC')
            if b64decode(code):
                user, password = b64decode(code).split(':')
            else:
                user = password = ''
            if self.user == user and self.password == password:
                # the request already had valid authentication header.
                return self.func(me, *args, **kws)
            resp = me.response
            resp.set_status(401)
            me.render('Auth')
            resp.headers['WWW-Authenticate'] = 'Basic realm="%s"' % self.realm

        return execute


def expose(func):
    """
    A decorator function to let a method/function show via URL invokation,
    used to avoid method exposure.
    You have to decorate method you want it to receive request from http
    like following ::

        @expose
        def some_method(self):
            # some code...
    """
    func._exposed_ = True
    return func

try:
    PAGE_CACHE_EXPIRE = config.page_cache_expire
except:
    PAGE_CACHE_EXPIRE = 60*60


class cache(object):
    """
    A decorator to cache response.
    You can control decorate function by giving arguments.
    
    :param expire: used to specify expiration time by giving seconds.

    You can set special class namespace to control namespace of the cache.
    Or you can also use set_namespace_func() classmethod to set it
    outside of the class.

    :param namespace_func: used to set hook function, 
    which returns namespace string for memcache sotre.
    The hook function is called along with request object.
    You can use the hook function to return different response
    seeing language, user agent etc. in header.


    """
    namespace_func = None

    def __init__(self, expire = PAGE_CACHE_EXPIRE):
        self.expire = expire

    def __call__(self, func, *args, **kws):
        import os
        self.func = func
        def execute(me):
            p = urlsplit(me.request.url)[2]
            namespace = ''
            if self.namespace_func:
                namespace = self.namespace_func(me.request)
            c = memcache.get(p, namespace = namespace)
            if c:
                # in case a given url has cached, we use it to make a response.
                resp = me.response
                r = me.response.out
                r.write(c['body'])
                for k, i in c['hdr'].items():
                    resp.headers[k] = i
                me.has_rendered = True
                me.cached = True
                return

            r = self.func(me, *args, **kws)
            if self.expire == 0:
                return
            resp = me.response
            out = resp.out
            out.seek(0)
            try:
                memcache.set(p, {'hdr':resp.headers,'body':out.read()},
                             self.expire, namespace = namespace)
                logging.debug('%s is cahed' % p)
            except:
                memcache.flush_all()
                logging.debug('memcache is flashed.')

        return execute

    @classmethod
    def set_namespace_func(cls, func):
        """
        A classmethod to set namespace function.
        The namespace function returns short string working as a namespace
        for memcache.
        You can use it to store different cache according to environment
        variable in request.
        For example, if you want to respond to requests from smartphones
        in different output, you may check user agent in requests
        and returns special namespace for these requests.
        """
        cls.namespace_func = staticmethod(func)


def mail(): pass;

