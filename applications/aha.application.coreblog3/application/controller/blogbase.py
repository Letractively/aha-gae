# -*- coding: utf-8 -*-
#
# blogbase.py
# A base classes of blog classes.
#
# Copyright 2011 Atsushi Shibata
#
"""
A base classes of blog classes.

$Id: blog.py 649 2010-08-16 07:44:47Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'MIT'

from datetime import datetime, timedelta

from aha.controller.util import get_controller_class
from aha.modelcontroller.formcontrol import FormControl
from aha.controller.decorator import authenticate, expose, cache
from aha import Config
config = Config()

from aha.modelcontroller.crudcontroller import (ModelCRUDController,
                                                EditHandler, AddHandler)

from model import Path, Page

TIME_TEMPLATE = '%a, %d %b %Y %H:%M:%S GMT'

def set_common_headers(headers, obj, delta):
    """
    A function to set common headers such as expires etc.
    """
    # setting headers
    headers['Last-Modified'] = obj.modified_at.strftime(TIME_TEMPLATE)
    headers['Expires'] = \
            (datetime.now()+delta).strftime(TIME_TEMPLATE)

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


class BlogContentBase(ModelCRUDController):
    """The base controller for content

    """
    PAGE_SIZE = 20
    FORM_TEMPLATE = '/common/admin/object_form'
    INDEX_TEMPLATE = '/common/view/page_index'
    EXPIRE_DELTA = timedelta(days=14)

    @expose
    @cache()
    def index(self):
        obj = self.content
        t = self.INDEX_TEMPLATE

        self.set_common_headers()
        # setting headers
        self.response.headers['Last-Modified'] = \
                self.content.modified_at.strftime('%a, %d %b %Y %H:%M:%S GMT')

        if obj.template:
            t = obj.template
        self.render(template = t)

    def set_common_headers(self):
        """
        A method to set common headers such as expires etc.
        """
        set_common_headers(self.response.headers, self.content,
                            self.EXPIRE_DELTA)


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
                ('/style/img/edit_icon.png', 'Edit', c.get_path()+'/edit' ),
            )
        if c.get_parent():
            self.side_menu_items = (
                ('', 'Going up', c.get_parent().get_path()+'/list' ),
                )+self.side_menu_items

    edit = expose(authenticate(config.admin_auth)(ContentEditHandler()))
    add = expose(authenticate(config.admin_auth)(ContentAddHandler()))

    @classmethod
    def get_form(self, kind, ins = None):
        """
        A method to return form object based on given kind.
        kind must be one of 'add' or 'edit'
        """
        from aha.widget.form import Form

        class AddForm(Form):
            multipart = True

        class EditForm(AddForm):
            pass

        if kind == 'add':
            return AddForm()
        elif kind == 'edit':
            return EditForm()

    @classmethod
    def make_add_form(cls, parent = None):
        """
        A method to create add form for the content object.
        You may override this method in your subclass.
        """

        form = self.get_form('edit', self)
        form.set_action(cls.BASEPATH+'/add')
        return form


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
    LISTPAGE_TITLE = 'Object list'
    LIST_ORDER = '-modified_at'
    LIST_TITLES = (('', u'Title'), ('middlelen', u'Modified'), 
                    ('shortlen', u'Edit'), ('shortlen', u'Delete'))
    FORM_TEMPLATE = '/common/admin/object_form'
    LIST_TEMPLATE = '/common/admin/model_list'
    INDEX_TEMPLATE = '/common/view/folder_index'
    EXPIRE_DELTA = timedelta(days=14)

    @expose
    @cache()
    def index(self):
        obj = self.content
        if obj.index_name:
            # the container has special index object,
            # so we let it be shown as the index page of the container.
            # TDB
            pass

        self.set_common_headers()

        t = self.INDEX_TEMPLATE
        if obj.template:
            t = obj.template
        self.render(template = t)

    def set_common_headers(self):
        """
        A method to set common headers such as expires etc.
        """
        set_common_headers(self.response.headers, self.content,
                            self.EXPIRE_DELTA)

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



class BlogContainerBase(ContainerBase):
    """
    The controller for Blog base.
    """
    EXPIRE_DELTA = timedelta(days=14)


    @expose
    @cache()
    def index(self):
        """
        A handler for blog index.
        """
        self.set_common_headers()
        self.blog = self.content

        self.render(template = self.INDEX_TEMPLATE)

    def set_common_headers(self):
        """
        A method to set common headers such as expires etc.
        """
        set_common_headers(self.response.headers, self.content, 
                           self.EXPIRE_DELTA)


    def set_side_menu_items(self, is_category = False):
        """
        A method to obtain menu list.
            each items in list contains title and link in a tuple.
            if tuple has 3 items and the third one is sequence,
                it means menu has sub items.
        """
        _ = self.translate
        c = self.content
        addable = c.ADDABLE[:]
        if is_category:
            addable = [BlogCategory.TYPE]
        else:
            addable.remove(BlogCategory.TYPE)
        self.side_menu_items = (
            ('/style/img/list_icon.gif', 'Show Entry list',
                                         c.get_path()+'/list' ),
            ('/style/img/list_icon.gif', 'Show Category list',
                                         c.get_path()+'/categories' ),
            ('/style/img/edit_icon.gif', 'Edit Blog Settings',
                                         c.get_path()+'/edit' ),
            ('/style/img/add_icon.gif', 'Add', '#',
                [('/style/img/%s_icon.gif' % x.lower(),
                  x, (c.get_path()+'/add?type=%s')%x)
                        for x in addable],
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
        query.filter('ctype =', BlogEntry.TYPE)
        query.order(self.LIST_ORDER)
        return list(query.fetch(self.PAGE_SIZE, offset = start))


    def get_listpage_item(self, obj):
        """
        A method to return items to be shown in list page on every row.
        """
        link = ''
        if obj.CONTAINER and obj.TYPE != BlogEntry.TYPE:
            link = obj.get_path()+'/list'
        return link, obj.title or obj.name


    @expose
    @authenticate(config.admin_auth)
    def categories(self):
        """
        A method to show list of published object.
        """
        _ = self.translate
        self.set_side_menu_items(is_category = True)
        self.list_titles = self.LIST_TITLES
        obj = self.content
        start = int(self.params.get('start', '0'))
        end = start+self.PAGE_SIZE
        self.path = obj.get_path()
        self.edit_base = (obj.get_path())
        self.link_title = 'title'
        self.page_title = self.LISTPAGE_TITLE or \
                            'List of %s' % MODEL.__class__.__name__

        self.objs = list([x.get_path_obj()
                for x in obj.get_categories(start, start+self.PAGE_SIZE)])
        self.start = start
        self.totla_count = obj.child_count
        self.page_size = self.PAGE_SIZE
        self.render(template = self.LIST_TEMPLATE)

    @expose
    @cache()
    def RSS2(self):
        """
        A handler for blog's RSS
        """
        self.blog = self.content
        self.render(template = '/common/rss')

    @expose
    def flush(self):
        from google.appengine.api import memcache
        import logging
        import aha
        config = aha.Config()
        memcache.flush_all()
        logging.debug('memcache is flushed.')
        self.redirect(config.site_root+self.content.get_path())


    @classmethod
    def get_form(self, kind, ins = None):
        """
        A method to return form object based on given kind.
        kind must be one of 'add' or 'edit'
        """
        from aha.widget.form import Form
        from aha.widget.field import (TextField, RichText,
                                        TextArea, SelectField, CheckboxField)
        from formencode import validators as v

        class AddForm(Form):
            multipart = True
            form_title = 'Add New Blog'
            button_title = 'Add'
            submit = 'Save'
            name = TextField(title = 'ID', args = {'size':40},
                                validator = v.String(), required = True)
            title = TextField(title = 'Title', args = {'size':40},
                                validator = v.String(), required = True)
            description = RichText(title = 'Description',
                        args = dict(cols = 60, rows = 3, id = 'description'),
                        collapsable = True)

            ping_urls = TextArea(title = 'PING Servers',
                        args = dict(cols = 60, rows = 3),
                                 collapsable = True)

            top_entry_count = TextField(title = 'Entry count to show on the top',
                        default = 4,
                        args = {'size':4}, validator = v.Int(), 
                        required = True)
            recent_item_count = TextField(
                        title = 'Item count to show at the side',
                        default = 4,
                        args = {'size':4}, validator = v.Int(), 
                        required = True)

            accept_comment = SelectField(title = 'Comments',
                        validator = v.Int(), required = True,
                        values = ( ('Accept', 1),
                                 ('Not Accept, Show', 2),
                                 ('Not Accept, Now Show', 3) ) )
            auth_comment = CheckboxField(
                        title = 'Require authentication before adding comment',
                        default = False, validator = v.Bool())
            accept_trackback = SelectField(title = 'Trackbacks',
                        validator = v.Int(), required = True,
                        values = ( ('Accept', 1), ('Not Accept, Show', 2),
                                 ('Not Accept, Now Show', 3) ) )

        class EditForm(AddForm):
            form_title = u'Edit Blog'

        del EditForm['name']

        if kind == 'add':
            return AddForm()
        elif kind == 'edit':
            return EditForm()


def main(): pass;

if __name__ == '__main__':
    main()
