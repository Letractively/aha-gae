# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from google.appengine.api import users

from aha.widget.field import *
from aha.widget.form import Form, Fieldset, ULFieldset, ListForm, TableForm
from aha.modelcontroller.formcontrol import FormControl, handle_state, validate
from aha import Config
config = Config()

from lib.formencode import validators as v

from aha.modelcontroller.crudcontroller import ModelCRUDController, EditHandler
from aha.controller.decorator import expose, authenticate

from model import SiteData, Folder, Path

class SitedataEditHandler(EditHandler):
    FC = FormControl()
    FORM_TEMPLATE = '/common/admin/object_form'

    def get_value(self, controller):
        """
        A method to obtain value from db, to supply to form fields.
        """
        obj = controller.MODEL.get_data()
        d = {}
        for f in controller.form:
            n = f.get_name()
            if hasattr(obj, n):
                d[n] = getattr(obj, n)
        return d

    @FC.handle_state(FC.PROCESSING, FC.FAILURE)
    def edit_form(self, controller):
        controller.set_side_menu_items()
        cu = config.auth_obj().get_user(controller)
        Folder.make_root_folder(cu.get('nickname', '') or cu.get('email', ''))
        controller.edit_sitedata = True
        controller.site_data = SiteData.get_data()
        controller.form.set_action(controller.BASEPATH)
        controller.objects = controller.form.get_object_tag()
        controller.render(template = self.FORM_TEMPLATE)

    @FC.handle_state(FC.SUCCESS)
    def edit_data(self, controller):
        obj = controller.MODEL.get_data()
        v = controller.form.values
        for k in v:
            setattr(obj, k, v[k])
        obj.put()

        controller.set_state(FormControl.INITIAL)
        controller.redirect('/list')


class SitedataController(ModelCRUDController):
    """The controller for SiteData

    """
    EDIT_FC = FormControl()
    PAGE_SIZE = 20
    MODEL = SiteData
    BASEPATH = '/_edit_sitedata'

    class EditForm(Form):
        multipart = True
        form_title = u'Edit Site Data'
        button_title = u'Edit'
        submit = u'Edit'
        title = TextField(title = u'Title', args = {'size':40},
                            validator = v.String(), required = True)
        description = TextArea(title = u'Site Summary',
                            args = dict(cols = 60, rows = 3))
        analytics_tag = TextArea(title = u'Tag for Google Analytics',
                            args = dict(cols = 60, rows = 3))
        admin_users = TextArea(title = u'Accounts of Site admin',
             desc = u'Separated in each lines in case of multiple account.',
                            args = dict(cols = 60, rows = 3))

    def set_side_menu_items(self):
        """
        A method to obtain menu list.
        """
        self.side_menu_items = config.site_admin_menus

    edit = expose(authenticate(config.admin_auth)(SitedataEditHandler()))

    def get_breadclumb(self):
        """
        A method to return special breadclumb for edit interface of sitedata
        """
        return self.translate("Edit Site Data")
