# -*- coding: utf-8 -*-
#
# blog.py
# A controller for Blog, top of the blog site.
#
# Copyright 2010 Atsushi Shibata
#
"""
A controller for Blog, top of the blog site.

$Id: blog.py 649 2010-08-16 07:44:47Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'MIT'

from datetime import datetime, timedelta

from aha.controller.decorator import authenticate, expose, cache
from aha.modelcontroller.formcontrol import FormControl
from aha import Config
config = Config()

from folder import ContainerBase
from model import Path, Blog, BlogEntry, BlogCategory
from application.controller import BlogContainerBase

class BlogController(ContainerBase):
    """
    The controller for Blog base.
    """
    PAGE_SIZE = 10
    MODEL = Blog
    LIST_ORDER = '-created_at'
    LISTPAGE_TITLE = 'Entry list'
    INDEX_TEMPLATE = '/common/blog/blog_index'


    @expose
    @cache()
    def index(self):
        """
        A handler for blog index.
        """
        self.blog = self.content
        self.set_common_headers()

        self.render(template = self.INDEX_TEMPLATE)


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
