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
from django.template import Context

class Microne(object):
    """\
    The class Microne contains many access points to the resources, 
    which reads such as request/response object etc.
    It also has decorators as a method. They can be used to connect path to 
    funtions, wrap authentication to functions, etc.
    Typically your application forms module - single python source code file.
    In the application, you may use Microne class like following. ::
    
        from plugins.microne.app import Microne
        app = Microne(__file__)
    
    And then, you may use app object for decorating function to connect to a path,
    in this case it's '/foo'. ::
    
        @app.route('/foo')
        def foo():
            app.render('Welcome to my first application !')
    
    You also see app instance in the function. It has some method used to make
    response etc.
    
    app object also has request object. When you want to get parameter from URL, 
    you do like following. ::
    
        @app.route('/foo/{id}')
        def foo():
            the_id = request.params.get('id', '')
            app.render('The id is %s' % the_id )
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
        
        :param app_id: The ID of the application. Just pass __file__
        if you don't care about it.
        """
        self.get_config()
        self.app_id = app_id


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

        def decorate(func, *args, **kws):
            """
            A function returned as a object in load time,
                which set route to given url along with decorated function.
            """
            from aha.dispatch.router import get_router
            r = get_router()
            argkeys = kws.keys()
            r.connect(None, path, controller = func, **kws)
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
        if 'context' in opt:
            # add request, response to context implicitly.
            opt['context']['request'] = self.request
            opt['context']['response'] = self.response
            context.update(opt['context'])
        opt['context'] = context.dicts[0]
        cnt = self.get_controller()
        cnt.render(*html, **opt)


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
                try:
                    if 'referer' not in me.session:
                        path = urlsplit(me.request.url)[2]
                        me.session['referer'] = self.config.site_root+path
                        me.session.put()
                except:
                    pass
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
        A method to attach config object to class object. It is used internally 
        """
        if not cls.config:
            import aha
            cls.config = aha.Config()




