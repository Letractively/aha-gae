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

from aha.modelcontroller.formcontrol import FormControl
from aha import Config

from aha.modelcontroller.crudcontroller import (ModelCRUDController,
                                                EditHandler, AddHandler)
from aha.controller.decorator import authenticate, expose, cache

from blogbase import BlogContentBase
from model import Page, Path
config = Config()

class ContentEditHandler(EditHandler):
    FC = FormControl()
    FORM_TEMPLATE = '/common/admin/object_form'

    def get_value(self, controller):
        """
        A method to obtain value from db, to supply to form fields.
        """
        obj = controller.content
        d = {}
        for f in controller.form:
            n = f.get_name()
            if hasattr(obj, n):
                d[n] = getattr(obj, n)
        return d

    def make_form(self, controller):
        """
        A method to create edit form.
        You should override this method in your subclass
            in case you want to change the way of form creation.
        """
        return controller.get_form('edit')

    @FC.handle_state(FormControl.PROCESSING, FormControl.FAILURE)
    def show_form(self, controller):
        controller.set_side_menu_items()
        obj = controller.content
        controller.form.set_action(obj.get_path()+'/edit')
        controller.objects = controller.form.get_object_tag()
        controller.render(template = self.FORM_TEMPLATE)

    @FC.handle_state(FormControl.SUCCESS)
    def process_data(self, controller):
        from datetime import datetime
        from google.appengine.api import memcache
        memcache.flush_all()

        obj = controller.content
        v = controller.form.validate_result
        for k in v:
            setattr(obj, k, v[k])
        obj.modified_at = datetime.now()
        obj.put()
        obj.sync_path(obj.get_path())

        controller.set_state(FormControl.INITIAL)
        rpath = config.site_root+obj.get_parent().get_path()+'/list'
        controller.redirect(rpath)

class ContentAddHandler(AddHandler):
    FC = FormControl()
    FORM_TEMPLATE = '/common/admin/object_form'

    def make_form(self, controller = None):
        form = self.get_form('add', self)
        return form

    @FC.handle_state(FormControl.PROCESSING, FormControl.FAILURE)
    def show_form(self, controller):
        controller.set_side_menu_items()
        obj = controller.content
        controller.objects = controller.form.get_object_tag()
        controller.render(template = self.FORM_TEMPLATE)


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



