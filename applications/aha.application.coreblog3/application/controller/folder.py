# -*- coding: utf-8 -*-
#
# folder.py
# A controller for Folder, content type holding sub object in it.
#
# Copyright 2010 Atsushi Shibata
#
"""
A controller for Folder, content type holding sub object in it.

$Id: forms.py 649 2010-08-16 07:44:47Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'MIT'


from datetime import datetime, timedelta

from aha.modelcontroller.formcontrol import FormControl

from aha.controller.decorator import authenticate, expose, cache
from aha import Config
config = Config()

from model import Folder, Path
from blogbase import ContainerBase

class FolderController(ContainerBase):
    """
    The controller for Folder.
    """
    MODEL = Folder
    LISTPAGE_TITLE = 'Object list'

    @classmethod
    def get_form(self, kind, ins = None):
        """
        A method to return form object based on given kind.
        kind must be one of 'add' or 'edit'
        """
        from aha.widget.field import (TextField, RichText)
        from aha.widget.form import Form
        from formencode import validators as v

        class AddForm(Form):
            multipart = True
            form_title = u'Add New Folder'
            button_title = u'Add'
            submit = u'Save'
            name = TextField(title = u'ID', args = {'size':40},
                                validator = v.String(), required = True)
            title = TextField(title = u'Title', args = {'size':40},
                                validator = v.String(), required = False)
            description = RichText(title = u'Description',
                                args = dict(cols = 60, rows = 3),
                                collapsable = True)
    
        class EditForm(AddForm):
            form_title = u'Edit Folder'
    
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
        cu = config.auth_obj().get_user(ins)
        v['creator'] = cu.get('nickname', '') or cu.get('email', '')
        d = {}
        [d.update({str(k): v[k]}) for k in v]
        o = cls.MODEL(**d)
        o.put()
        return o

def main(): pass;

if __name__ == '__main__':
    main()
