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

from aha.modelcontroller.crudcontroller import ModelCRUDController
from aha.controller.decorator import authenticate, expose, cache
from aha import Config
config = Config()

from aha.controller.util import get_controller_class
from model import Folder, Path
from page import ContentEditHandler, ContentAddHandler

class ContainerEditHandler(ContentEditHandler):
    FC = FormControl()

    @FC.handle_state(FormControl.SUCCESS)
    def process_data(self, controller):
        from google.appengine.api import memcache
        super(ContainerEditHandler, self).process_data(controller)
        obj = controller.content
        p = obj.get_parent()
        if p:
            controller.redirect(config.site_root+p.get_path()+'/list')
        else:
            controller.redirect(config.site_root+obj.get_path()+'/list')


class ContainerAddHandler(ContentAddHandler):
    FC = FormControl()

    @classmethod
    def make_form(cls, controller, parent = None):
        tp = controller.params.get('type', 'Folder')
        if '.' in tp:
            plugin, cname = tp.split('.')
        else:
            plugin = ''
            cname = tp
        ctrl_clz = get_controller_class(cname, plugin)
        try:
            form = ctrl_clz.make_add_form(controller.content)
        except:
            form = ctrl_clz.get_form('add', controller)
        form.set_action(controller.content.get_path()+'/add'+\
                                    '?type='+tp)
        return form

    @FC.handle_state(FormControl.SUCCESS)
    def process_data(self, controller):
        from google.appengine.api import memcache

        v = controller.form.validate_result
        tp = controller.params.get('type', 'Folder')
        if '.' in tp:
            plugin, cname = tp.split('.')
        else:
            plugin = ''
            cname = tp
        ctrl_clz = get_controller_class(cname, plugin)
        o = ctrl_clz.add_new_object(v, controller)
        memcache.flush_all()
        controller.content.add(o)

        controller.set_state(FormControl.INITIAL)
        if not controller.has_redirected:
            p = config.site_root+controller.content.get_path()+'/list'
            controller.redirect(p)


class ContainerBase(ModelCRUDController):
    """The base controller of container

    """
    PAGE_SIZE = 10
    MODEL = Folder
    LISTPAGE_TITLE = 'Object list'
    LIST_ORDER = '-modified_at'
    LIST_TITLES = (('', u'Title'), ('middlelen', u'Modified'), 
                    ('shortlen', u'Edit'), ('shortlen', u'Delete'))
    FORM_TEMPLATE = '/common/admin/object_form'
    LIST_TEMPLATE = '/common/admin/model_list'
    INDEX_TEMPLATE = '/common/view/folder_index'

    @expose
    @cache()
    def index(self):
        obj = self.content
        if obj.index_name:
            # the container has special index object,
            # so we let it be shown as the index page of the container.
            # TDB
            pass
        t = self.INDEX_TEMPLATE
        if obj.template:
            t = obj.template
        self.render(template = t)

    def set_side_menu_items(self):
        """
        A method to obtain menu list.
            each items in list contains title and link in a tuple.
            if tuple has 3 items and the third one is sequence,
                it means menu has sub items.
        """
        _ = self.translate
        c = self.content
        self.side_menu_items = (
            ('/style/img/list_icon.png', 'Show list', c.get_path()+'/list' ),
            ('/style/img/edit_icon.png', 'Edit', c.get_path()+'/edit' ),
            ('/style/img/add_icon.png', 'Add', '#',
                [('/style/img/%s_icon.png' % x.lower(),
                  x, (c.get_path()+'/add?type=%s')%x)
                        for x in c.ADDABLE],
            )
            )
        if c.get_parent():
            self.side_menu_items = (
                ('', 'Going up', c.get_parent().get_path()+'/list' ),
                )+self.side_menu_items

    def get_index_object(self, start, end):
        """
        A method to generate query,
             that gets bunch of object to show in the list
        """
        query = Path.all()
        query.filter('parent_c_key =', self.content.get_namekey())
        query.order(self.LIST_ORDER)
        return list(query.fetch(self.PAGE_SIZE, offset = start))


    @expose
    @authenticate(config.admin_auth)
    def list(self):
        """
        A method to show list of published object.
        """
        self.set_side_menu_items()
        self.list_titles = self.LIST_TITLES
        obj = self.content
        start = int(self.params.get('start', '0'))
        end = start+self.PAGE_SIZE
        self.path = obj.get_path()
        self.edit_base = (obj.get_path())
        self.link_title = 'title'
        self.page_title = self.LISTPAGE_TITLE or \
                            'List of %s' % MODEL.__class__.__name__

        self.objs = self.get_index_object(start, end)
        self.start = start
        self.totla_count = obj.child_count
        self.page_size = self.PAGE_SIZE
        self.render(template = self.LIST_TEMPLATE)

    def get_listpage_item(self, obj):
        """
        A method to return items to be shown in list page on every row.
        """
        link = ''
        if obj.CONTAINER:
            link = obj.get_path()+'/list'
        return link, obj.title or obj.name


    edit = expose(authenticate(config.admin_auth)(ContainerEditHandler()))

    add = expose(authenticate(config.admin_auth)(ContainerAddHandler()))


    @classmethod
    def add_new_object(cls, v, ins):
        """
        A method to obtain new object
        """
        from google.appengine.api import memcache
        cu = config.auth_obj().get_user(ins)
        v['creator'] = cu.get('nickname', '') or cu.get('email', '')
        d = {}
        [d.update({str(k): v[k]}) for k in v]
        o = cls.MODEL(**d)
        o.put()
        return o


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
