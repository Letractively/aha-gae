# -*- coding: utf-8 -*-
#
# blogcategory.py
# A controller for BlogCategory, representing categories of blog.
#
# Copyright 2010 Atsushi Shibata
#
"""
A controller for BlogCategory, representing categories of blog.

$Id: forms.py 649 2010-08-16 07:44:47Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'MIT'

from aha import Config
config = Config()

from model import Blog, BlogEntry, BlogCategory
from page import ContentBase

class BlogcategoryController(ContentBase):
    """The controller for blog category
    """

    PAGE_SIZE = 20
    MODEL = BlogCategory

    @classmethod
    def get_form(self, kind, ins = None):
        """
        A method to return form object based on given kind.
        kind must be one of 'add' or 'edit'
        """
        from aha.widget.form import Form
        from aha.widget.field import TextField, RichText
        from formencode import validators as v

        class AddForm(Form):
            multipart = True
            form_title = u'Add New Category'
            button_title = u'Add'
            submit = u'Save'
            name = TextField(title = u'ID', args = {'size':40},
                                validator = v.String(), required = True)
            title = TextField(title = u'Title', args = {'size':40},
                                validator = v.String(), required = True)
            description = RichText(title = u'Description', args = dict(rows = 4),
                                 required = False, collapsable = True)
    
        class EditForm(AddForm):
            form_title = u'Edit Category'
    
        del EditForm['name']

        if kind == 'add':
            return AddForm()
        elif kind == 'edit':
            return EditForm()


    @classmethod
    def add_new_object(cls, v, ins):
        """
        A method to obtain new object
        """
        cu = config.auth_obj().get_user(cls)
        v['creator'] = cu.get('nickname', '') or cu.get('email', '')
        d = {}
        [d.update({str(k): v[k]}) for k in v]
        o = cls.MODEL(**d)
        o.category_id = str(ins.content.get_unique_category_id())
        o.put()
        return o




