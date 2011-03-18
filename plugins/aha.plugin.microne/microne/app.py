# -*- coding: utf-8 -*-
#
# The application instance of aha-microne, paths to the application environment.
#
# Copyright 2011 Atsushi Shibata
#

"""
The application instance of aha-microne, paths to the application environment.

$Id: dispatcher.py 653 2010-08-23 02:00:58Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'

__all__ = ['App']

import logging

class App(object):

    # class attributes.
    config = None
    hnd = None
    request = None
    response = None
    controller = None

    def __init__(self, app_id):
        """
        A constructor for App instance.
        """
        self.get_config()
        self.app_id = app_id


    def route(self, path, **params):
        """
        A method used as a decorator, set a route to application.
        """
        self.params = params

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
        A method to render template.
        """
        cnt = self.get_controller()
        cnt.render(*html, **opt)
        # clear controller for development environment.


    def authenticate(self):
        """
        A method used as a decorator, 
            which wrap method only to be accessed with authentication.
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
    def set_handler(cls, hnd):
        """
        A method to set hnd object.
        """
        cls.hnd = hnd
        cls.request = hnd.request
        cls.response = hnd.response

    @classmethod
    def get_handler(cls):
        """
        A method to return hander object.
        """
        if not cls.hnd:
            raise ValueError(("You must set handler by using set_hnd() method, "
                              "before calling get_handler() method."))
        return cls.hnd

    @classmethod
    def get_controller(cls):
        """
        A method to get controller object.
        """

    @classmethod
    def get_controller(cls):
        """
        A method to get controller object via cls.controller.
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
        A method to clear controller object.
        If no controller instanciated, it makes new one.
        """
        del cls.controller
        cls.controller = None

    @classmethod
    def get_config(cls):
        """
        A method to attach config object to class object.
        """
        if not cls.config:
            import aha
            cls.config = aha.Config()


