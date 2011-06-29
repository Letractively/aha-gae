# -*- coding: utf-8 -*-
#
# The application instance of aha-microne, paths to the application environment.
#
# Copyright 2011 Atsushi Shibata
# $Id: dispatcher.py 653 2010-08-23 02:00:58Z ats $

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'

__all__ = ['Microne']

"""\
This module contains class Microne, which works as a micro framework on the top of 
the web application framework `aha <http://coreblog.org/aha>`_.
"""

import logging
from urlparse import urlsplit
from django.template import Context


class Microne(object):
    """\
    The class Microne contains many access points to the resources, 
    which leads such as request/response object etc.
    It also has decorators as a method. They can be used to connect path to 
    funtions, wrap authentication for functions, etc.
    Typically you make application as a module - single python source code file.
    In the application, you may use Microne class like following. ::
    
        from plugins.microne.app import Microne
        app = Microne(__file__)
    
    And then, you may use app object for decorating function to connect to a path,
    in this case it's '/foo'. ::
    
        @app.route('/foo')
        def foo():
            app.render('Welcome to my first application !')
    
    You can also use app instance in the function. It has some method used to make
    response etc.
    
    app object also has request object. When you want to get parameter from URL, 
    you do like following. ::
    
        @app.route('/foo/{id}')
        def foo():
            the_id = request.params.get('id', '')
            app.render('The id is %s' % the_id )

    The constructor has few arguments.

    :param app_id: The ID of the application. Just pass __file__
    if you don't care about it.

    app instance has several attributes that you can use in your web application::

    :request:   A WebOb.request object. You can get many data such as
    request headers, POST/GET data, URL, etc. from this attribute
    :response:  A WebOb.response object. You can pass informations
    by adding header and so on.
    :params:    Parameters that routes returns. In case you set route '/url/{id}'
    by using @app.route(), and the URL is '/url/foo',
    you will get string 'foo' by giving 'app.params.get('id') in your code.
    :context:   The context object that is passed to app.render().
    :session:   The volatile session object. You can use session object
    the same way as dictionary. Don't forget to call session.put()
    to store session data.
    :config:    The config object of Aha, which has many global configulation
    information.
    """

    # class attributes.
    config = None
    hnd = None
    request = None
    response = None
    controller = None
    params = None
    context = None

    def __init__(self, app_id):
        """
        A constructor for App instance.
        """
        # getting config object.
        self.get_config()
        self.app_id = app_id
        # a dictionary to store expires and namespace functions
        # for each decorated function,
        #    setting function object as a key to the dictionary.
        self.cache_expires = {}
        self.cache_nsfuncs = {}


    def route(self, path, **params):
        """\
        A method used as a decorator, set a route to application.
        Usage::

            app.route('/path/to/function')
            def some_func():
                # do something....

        Microne uses python routes, which provides RoR's route like function.
        You may put parameter in URL to remain in cool URL like following.::

            app.route('/path/{id}/{kind}')
            def some_func():
                id = app.params.get('id', '')
                kind = app.params.get('kind', '')
                # do something....

        :param path: URL path. It is passed to routes.

        :param params: Not in use.

        """

        def decorate(func):
            """
            A function returned as a object in load time,
            which set route to given url along with decorated function.
            """
            from aha.dispatch.router import get_router
            r = get_router()
            r.connect(None, path, controller = func, **params)
            return func
        
        return decorate


    def render(self, *html, **opt):
        """
        A method used to render output.

        Usage ::

            @app.route('/path')
            def foo():
                app.render('This is direct string output')

        You can also use `mako <http://www.makotemplates.org/>` template.::

            @app.route('/path')
            def foo():
                app.render(template='some_template')

        render() has some expected arguments. 

        :param template : path to the template file. Extension of the template
        is 'html'. Just omit extension. 
        :param html     : raw html for the output.
        :param json     : raw json for the output.
        :param xml      : raw xml for the output.
        :param script   : raw java script for the output.
        :param expires  : expire date as a string.
        :param text     : raw text for the output.
        :param encode   : encode for the output.
        :param context  : the context dictionaly passed to template.

        """
        context = self.context
        # add request, response to context implicitly.
        context['request'] = self.request
        context['response'] = self.response
        if 'context' in opt:
            context.update(opt['context'])
        opt['context'] = context.dicts[0]
        cnt = self.get_controller()
        cnt.render(*html, **opt)


    def redirect(self, path):
        """
        A method to perform redirection.
        
        :param path: The path to redirect.
        """
        self.get_controller().redirect(path)


    def error(self, code, message = ''):
        """
        A method to return error page.
        
        :param code: The http status code such as 404.
        :param message: The message to show in error page.
        """
        self.response.set_status(404)
        raise Exception(message)


    def cache(self, expire = 0, namespace_func = None):
        """
        A method used to cache outputs of the decorated function.
        It caches the output of the decorated function.
        Usage::
        
            @app.cache(expire = 600):  # expires in 10 minutes
            def foo():
                app.render('The output')

        It has some arguments to control caches::
        :param expire: the expiration time for cache in seconds.
        :param namespace_func: used to set hook function, 
        which returns namespace string for memcache sotre.
        The hook function is called along with request object.
        You can use the hook function to return different response
        seeing language, user agent etc. in header.
        """
        from google.appengine.api import memcache
        
        def decorate(func, *args, **kws):
            """
            A function returned as a object in load time,
            which returns inner function do_decorate().
            """
            # setting cache expires for given decorated function,
            #  if argument 'expire' is given.
            if expire:
                self.cache_expires[func] = expire
            else:
                self.cache_expires[func] = self.get_config().page_cache_expire
            if namespace_func:
                self.cache_nsfuncs[func] = namespace_func

            def do_cache(*args, **kws):
                """
                A function works every time decorated functions are called.
                """
                resp = self.response
                out = resp.out
                namespace = ''
                if self.cache_nsfuncs.get(func, None):
                    namespace = self.cache_nsfuncs[func](self.request)
                p = urlsplit(self.request.url)[2]
                c = memcache.get(p, namespace)
                if c:
                    # in case cache is found, use it 
                    #           instead of rendering by calling function.
                    out.write(c['body'])
                    for k, i in c['hdr'].items():
                        resp.headers[k] = i
                    return

                r = func(*args, **kws)
                expire = self.cache_expires.get(func, 0)
                if expire == 0:
                    return
                out.seek(0)
                try:
                    p = urlsplit(self.request.url)[2]
                    memcache.set(p, {'hdr':resp.headers,'body':out.read()},
                                 expire, namespace=namespace)
                    logging.debug('%s is cahed' % p)
                except:
                    memcache.flush_all()
                    logging.debug('memcache is flashed.')
            return do_cache

        return decorate


    def authenticate(self):
        """
        A method used to wrap function with authentication.
        Usage::

            @app.route('/foo2')
            @app.authenticate()
            def foo2():
                app.render('The output.')

        Note::
            app.route() must be come first.

        """

        def decorate(func, *args, **kws):
            """
            A function returned as a object in load time,
            which returns inner function do_decorate().
            """
            def do_authenticate():
                """
                A function to perform authentication
                    every time decorated function is called.
                """
                #try:
                if 1:
                    if 'referer' not in self.session:
                        path = urlsplit(self.request.url)[2]
                        self.session['referer'] = path
                        self.session.put()
                #except:
                #    pass
                aobj = self.config.auth_obj()
                self.get_controller()
                auth_res = aobj.auth(self.controller, *args, **kws)
                if auth_res:
                    return func(*args, **kws)
                aobj.auth_redirect(self.controller, *args, **kws)
                # clear controller for development environment.

            return do_authenticate

        return decorate


    @classmethod
    def set_handler(cls, hnd, route):
        """
        A class method to set handler object. Dispatcher uses this internally.
        
        :param hnd: The hander object.
        :param route: The router object.
        """
        cls.hnd = hnd
        cls.request = hnd.request
        cls.response = hnd.response
        cls.params = route
        if cls.context:
            del cls.context
        cls.context = Context()


    @classmethod
    def get_handler(cls):
        """
        A class method to return hander object. Dispatcher uses this internally.
        """
        if not cls.hnd:
            raise ValueError(("You must set handler by using set_hnd() method, "
                              "before calling get_handler() method."))
        return cls.hnd

    @classmethod
    def get_controller(cls):
        """
        A method to get controller object via cls.controller.
        Dispatcher uses this internally.
        If no controller instanciated, it makes new one.
        """
        if not cls.hnd:
            raise Exception('A handler is to be set for getting contoller.')
        if not cls.controller:
            cls.controller = cls.config.controller_class(cls.hnd)
            cls.session = cls.controller.session
        return cls.controller


    @classmethod
    def clear_controller(cls):
        """
        A method to clear controller object. Dispatcher uses this internally.
        If no controller instanciated, it makes new one.
        """
        del cls.controller
        cls.controller = None

    @classmethod
    def get_config(cls):
        """
        A method to attach config object to class object and returns it.
        Typicalli it is used internally.
        """
        if not cls.config:
            import aha
            cls.config = aha.Config()
        return cls.config





