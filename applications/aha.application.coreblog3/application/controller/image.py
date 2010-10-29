# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.api import images

from aha.widget.field import *
from aha.widget.form import Form, Fieldset, ULFieldset, ListForm, TableForm
from aha.modelcontroller.formcontrol import FormControl
FC = FormControl
from formencode import validators as v

from aha.modelcontroller.crudcontroller import ModelCRUDController
from aha.controller.decorator import authenticate, expose, cache

from aha.controller.util import get_current_user

from model import Image, Path
from page import ContentBase
from mimetypes import guess_type

from page import ContentEditHandler, ContentAddHandler

def detect_imagetype(image):
    if image[6:10] == 'JFIF': return 'image/jpeg'
    if image[0:3] == 'GIF': return 'image/gif'
    if image[1:4] == 'PNG': return 'image/png'

class ImageEditHandler(ContentEditHandler):
    FC = FormControl()

    def get_value(self, controller):
        """
        A method to obtain value from db, to supply to form fields.
        """
        obj = controller.content
        d = {}
        """
        for f in controller.form:
            n = f.get_name()
            if n != 'body' and hasattr(obj, n):
                d[n] = getattr(obj, n)
        d['body'] = controller.path_obj.get_path()
        """
        return d

    def make_form(self, controller):
        """
        A method to create edit form.
        """
        form = controller.get_form('edit')
        return form
        key = controller.params.get('id', '')
        form.values['body'] = controller.path_obj.get_path()
        form.set_action(controller.BASEPATH+'/edit/'+key)
        return form

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
            v['content_type'] = detect_imagetype(v['body'])
            i = images.Image(v['body'])
            v['width'], v['height'] = i.width, i.height
            v['filename'] = f.filename
        if not v.get('name', None) and v.get('filename'):
            v['name'] = v['filename']
        if not v.get('title', None):
            v['title'] = v['name']
        obj.modified_at = datetime.now()
        obj.put()
        obj.sync_path(obj.get_path())

        controller.set_state(FC.INITIAL)
        controller.redirect(obj.get_parent().get_path()+'/list')


class ImageController(ContentBase):
    """
    The controller for image
    """
    MODEL = Image

    @expose
    @cache()
    def index(self):
        obj = self.content
        hdrs = {'Content-Type':str(obj.content_type)}
        self.view.render(obj.body, hdrs)
        self.has_rendered = True


    @classmethod
    def add_new_object(cls, v, ins):
        """
        A method to obtain new object
        """
        from aha import Config
        config = Config()
        f = ins.request.body_file.vars["body"]
        v['content_type'] = detect_imagetype(v['body'])
        i = images.Image(v['body'])
        v['width'], v['height'] = i.width, i.height
        v['filename'] = f.filename
        if not v.get('name', None):
            v['name'] = v['filename']
        if not v.get('title', None):
            v['title'] = v['name']
        cu = config.auth_obj().get_user(ins)
        v['creator'] = cu.get('nickname', '') or cu.get('nickname', '')
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
            form_title = u'Add New Image'
            button_title = u'Add'
            submit = u'Save'
            name = TextField(title = u'ID', args = {'size':40},
                                validator = v.String(), required = False)
            title = TextField(title = u'Title', args = {'size':40},
                                validator = v.String(), required = False)
            body = ImageField(title = u'Image File', required = True)
            description = RichText(title = u'Description', 
                                args = dict(cols = 60, rows = 3),
                                collapsable = True)

        class EditForm(AddForm):
            form_title = u'Edit Image'

        del EditForm['name']
        EditForm['body'] = ImageField(title = u'Image File', required = False)

        if kind == 'add':
            return AddForm()
        elif kind == 'edit':
            return EditForm()
