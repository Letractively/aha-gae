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

__all__ = ['App']

from inspect import getargspec
import logging

from aha.controller.makocontroller import MakoTemplateController


class App(object):

    # class attributes.
    hnd = None
    request = None
    response = None


    def __init__(self, app_id):
        """
        """
        self.app_id = app_id
        self.controller = None


    def route(self, path, **params):
        """
        A method used as a decorator, set a route to application.
        """
        self.params = params

        def decorate(func, *args, **kws):
            from lib.aha.dispatch.router import get_router
            fr = get_router()
            argkeys = kws.keys()
            fr.connect(None, path, controller = func, **kws)
        
        return decorate


    def get_controller(self):
        """
        A method to get controller object via self.controller.
        If no controller instanciated, it makes new one.
        """
        if not self.hnd:
            raise Exception('A handler is to be set for getting contoller.')
        if not self.controller:
            self.controller = MakoTemplateController(self.hnd)
        return self.controller


    def render(self, *html, **opt):
        """
        A method to render template.
        """
        cnt = self.get_controller()
        cnt.render(*html, **opt)


    @classmethod
    def set_hnd(cls, hnd):
        """
        A method to set hnd object.
        """
        cls.hnd = hnd
        cls.request = hnd.request
        cls.response = hnd.response

