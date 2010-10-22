# -*- coding: utf-8 -*-

##############################################################################
#
# makoemailengine.py
# Class to send email by using mako as a template engine.
#
# Copyright (c) 2010 Webcore Corp. All Rights Reserved.
#
##############################################################################
""" makoemailengine.py - Classes to handle CRUD form for a model.

$Id: makoemailengine.py 644 2010-08-10 04:15:42Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'

import logging
from google.appengine.api import mail
from controller import makocontroller 

import mako

class MakoEmailMessage(object):
    """
    A class to send email using mako template.
    """

    def __init__(self, template = '', templatepath = '', context = {},
                 contenttype = 'text/plain', **kwd):
        """
        An initialize method.
        """
        self._template = template
        self._templatepath = templatepath
        self._context = context
        self._rendered_body = ''
        self._contenttype = contenttype
        # set template lookup for mako
        makocontroller.get_lookup()
        self.email = mail.EmailMessage(**kwd)

    def render(self, template = '', templatepath = '', context = {}, contenttype = ''):
        """
        A method to render template based on given arguments
            and store result to the instance.
        """
        self._contenttype = contenttype or self._contenttype
        t = self._template or template
        if template:
            tmpl = mako.template.Template(t)
        else:
            tlu = makocontroller.tlookup
            tmpl = tlu.get_template(self._templatepath or templatepath)
        c = self._context or context
        self._rendered_body = tmpl.render(**c)


    def send(self, template = '', templatepath = '', context = {}, contenttype = ''):
        """
        A method to send email.
        """
        if not self._rendered_body:
            self.render(template, context, contenttype)
        if self._contenttype == 'text/plain':
            self.email.body = self._rendered_body
        elif self._contenttype == 'text/html':
            self.email.html = self._rendered_body

        self.email.send()

