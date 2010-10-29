# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from aha.widget.field import *
from aha.modelcontroller.formcontrol import FormControl
FC = FormControl
from formencode import validators as v

from aha.modelcontroller.crudcontroller import ModelCRUDController
from aha.controller.decorator import authenticate, expose, cache

from model import File, Path
from controller.page import ContentBase
from mimetypes import guess_type

from page import ContentEditHandler, ContentAddHandler
from aha import Config
config = Config()

class FileEditHandler(ContentEditHandler):
    FC = FormControl()

    @FC.handle_state(FormControl.SUCCESS)
    def process_data(self, controller):
        from google.appengine.api import memcache
        memcache.flush_all()

        obj = controller.content
        v = controller.form.validate_result
        replace_body = True
        for k in v:
            if k == 'body' and not v[k]:
                replace_body = False
            else:
                setattr(obj, k, v[k])
        if replace_body:
            f = controller.request.body_file.vars["body"]
            v['content_type'] = guess_type(f.filename)[0]
            v['filename'] = f.filename
        if not v.get('name', None):
            v['name'] = v['filename']
        if not v.get('title', None):
            v['title'] = v['name']
        obj.modified_at = datetime.now()
        obj.put()
        obj.sync_path(obj.get_path())

        controller.set_state(FC.INITIAL)
        controller.redirect(obj.get_parent().get_path()+'/list')


class FileController(ContentBase):
    """
    The controller for file
    """
    MODEL = File
    INDEX_TEMPLATE = '/common/view/file_index'

    @expose
    @cache()
    def index(self):
        obj = self.content
        hdrs = {'Content-Type':str(obj.content_type)}
        self.view.render(obj.body, hdrs)
        self.has_rendered = True

    edit = expose(authenticate(config.admin_auth)(FileEditHandler()))


    @classmethod
    def add_new_object(cls, v, ins):
        """
        A method to obtain new object
        """
        from aha import Config
        config = Config()
        f = ins.request.body_file.vars["body"]
        v['content_type'] = guess_type(f.filename)[0]
        v['filename'] = f.filename
        if not v.get('name', None):
            v['name'] = v['filename']
        if not v.get('title', None):
            v['title'] = v['name']
        cu = config.auth_obj().get_user(ins)
        v['creator'] = cu.get('nickname', '') or cu.get('email', '')
        d = {}
        [d.update({str(k): v[k]}) for k in v]
        o = cls.MODEL(**d)
        o.put()
        return o

    @classmethod
    def get_form(self, kind, ins = None):
        """
        A method to return form object based on given kind.
        kind must be one of 'add' or 'edit'
        """
        from aha.widget.form import Form

        class AddForm(Form):
            multipart = True
            form_title = u'Add New File'
            button_title = u'Add'
            submit = u'Save'
            name = TextField(title = u'ID', args = {'size':40},
                                validator = v.String(), required = False)
            title = TextField(title = u'Title', args = {'size':40},
                                validator = v.String(), required = False)
            body = FileField(title = u'File', required = True)
            description = RichText(title = u'Description',
                                args = dict(cols = 60, rows = 3),
                                collapsable = True)

        class EditForm(AddForm):
            form_title = u'Edit File'

        del EditForm['name']

        if kind == 'add':
            return AddForm()
        elif kind == 'edit':
            return EditForm()

