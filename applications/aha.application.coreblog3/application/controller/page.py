# -*- coding: utf-8 -*-
#
# page.py
# A controller for Page, content type representing common web page.
#
# Copyright 2010 Atsushi Shibata
#
"""
A controller for Page, content type representing common web page.

$Id: page.py 649 2010-08-16 07:44:47Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'MIT'

import logging
from google.appengine.api import users

from aha import Config

from aha.modelcontroller.crudcontroller import (ModelCRUDController,
                                                EditHandler, AddHandler)
from aha.controller.decorator import authenticate, expose, cache

from blogbase import BlogContentBase
from model import Page, Path
config = Config()


class PageController(BlogContentBase):
    """The controller for page

    """
    PAGE_SIZE = 20
    MODEL = Page

    @classmethod
    def get_form(self, kind, ins = None):
        """
        A method to return form object based on given kind.
        kind must be one of 'add' or 'edit'
        """
        from aha.widget.field import TextField, RichText
        from aha.widget.form import Form
        from formencode import validators as v

        class AddForm(Form):
            multipart = True
            form_title = u'Add New Page'
            button_title = u'Add'
            submit = u'Save'
            name = TextField(title = u'ID', args = {'size':40},
                        validator = v.String(), required = True)
            title = TextField(title = u'Title', args = {'size':40},
                        validator = v.String(), required = True)
            description = RichText(title = u'Description',
                        args = dict(cols = 70, rows = 4, id = 'description'),
                        required = False, collapsable = True)
            body = RichText(title = u'Body', required = True,
                        args = dict(id = 'body'))
    
        class EditForm(AddForm):
            form_title = u'Edit Page'
    
        del EditForm['name']

        if kind == 'add':
            return AddForm()
        elif kind == 'edit':
            return EditForm()



