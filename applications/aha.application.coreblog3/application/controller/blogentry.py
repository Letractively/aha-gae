# -*- coding: utf-8 -*-
#
# blogentry.py
# A controller for BlogEntry, representing every blog entries
#
# Copyright 2010 Atsushi Shibata
#
"""
A controller for BlogEntry, representing every blog entries

$Id: forms.py 649 2010-08-16 07:44:47Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'MIT'

from datetime import datetime, timedelta

from aha.controller.decorator import authenticate, expose, cache
from aha.modelcontroller.formcontrol import FormControl
FC = FormControl
from aha import Config
config = Config()
from folder import ContainerBase, ContainerEditHandler, ContainerAddHandler
from model import Blog, BlogEntry, BlogCategory, BlogComment, BlogTrackback

from config import check_for_spartphone

class BlogentryEditHandler(ContainerEditHandler):
    FC = FormControl()

    def edit_form(self, parent = None):
        """
        A method to create edit form.
        """
        form = self.get_form('edit', self)
        cf = form['categories']
        blog = self.content.blog_object()
        cf.values = [(x.title, x.category_id)
                    for x in blog.get_categories(end = 100)]
        return form


class BlogcommentAddHandler(ContainerAddHandler):
    FC = FormControl()

    def make_form(self, controller):
        """
        A method to make form.
        """
        config = Config()
        authobj = config.auth_obj()
        user = authobj.get_user(controller)
        form = None
        if controller.content.blog_object().auth_comment and not user:
            form = controller.get_form('comment_add_auth', controller)
        if form == None:
            form = controller.get_form('comment_add', controller)

        form.action = controller.content.get_path()+'/postcomment'
        return form


    @FC.handle_state(FC.INITIAL, FC.FAILURE)
    def show_form(self, controller):
        """
        A method to show add form.
        You must override this method in your subclass.
        """
        controller.objects = controller.form.get_object_tag()
        controller.render(template = '/common/blog/commentform')


    @FC.handle_state(FC.SUCCESS)
    def process_data(self, controller):
        """
        A method to add new data by using posted values.
        You must override this method in your subclass.
        """
        from google.appengine.api import memcache
        from aha import Config
        config = Config()

        v = controller.form.values
        controller.content.add_comment(name = v['author_name'],
                        url = v.get('url', ''), email = v.get('email', ''),
                        title = v['title'], body = v['body'],
                        creator = controller.content.creator)
        memcache.flush_all()

        controller.redirect(config.site_root+controller.content.get_path())


    @FC.handle_validate(FC.INITIAL, FC.FAILURE)
    def do_validate(self, state, controller):
        """
        A validator method for edit transition
        """
        from aha import Config
        config = Config()
        authobj = config.auth_obj()
        user = authobj.get_user(controller)

        if controller.content.blog_object().auth_comment:
            # require authentication
            # when blog.auth_comment = True
            if not user:
                controller.session['referer'] = \
                config.site_root+controller.content.get_path()+'/postcomment'
                controller.session.put()
                authobj.auth_redirect(controller)

        if controller.content.blog_object().auth_comment and user:
            from aha.widget.field import HiddenField
            controller.form['author_name'].args.update(readonly = 'readonly')
            controller.form['author_name'].default = user.get('nickname', '')
            del controller.form['email']
            del controller.form['url']
            controller.form['url'] = \
                    HiddenField(name = 'url', default = user.get('url', ''))

        state = FC.INITIAL
        controller.blog = controller.content.blog_object()
        if controller.request.POST and \
            ('author_name' in controller.request.POST or
             'author_name2' in controller.request.POST):
            if not controller.request.POST:
                return FC.INITIAL
            e = controller.form.validate(dict([(x, controller.request.get(x))
                                    for x in controller.request.arguments()]))
            if e:
                # Some error occured
                return FC.FAILURE
            else:
                return FC.SUCCESS

        return FC.INITIAL

class BlogentryController(ContainerBase):
    """
    The controller for Blog Entry.
    """
    COMMENT_FC = FormControl()
    PAGE_SIZE = 20
    MODEL = BlogEntry
    INDEX_TEMPLATE = '/common/blog/entry'


    @classmethod
    def get_form(self, kind, ins = None):
        """
        A method to return form object based on given kind.
        kind must be one of 'add' or 'edit'
        """
        from aha.widget.form import Form
        from aha.widget.field import (TextField, RichText,
                                        TextArea, CheckboxGroup, SelectField)
        from formencode import validators as v

        class AddForm(Form):
            multipart = True
            form_title = 'Add New Entry'
            button_title = 'Add'
            submit = 'Save'
            name = TextField(title = 'ID', args = {'size':40},
                                validator = v.String(), required = True)
            title = TextField(title = 'Title', args = {'size':40},
                                validator = v.String(), required = True)
    
            body = RichText(title = 'Body',
                            args = dict(cols = 60, rows = 3, id = 'body'),
                            required = False)
            extend_body = RichText(title = 'Extended body',
                            args = dict(cols = 60, rows = 3, id = 'extended'),
                            collapsable = True)
    
            categories = CheckboxGroup(title = 'Category(s)',
                            values = ( ('No Category', 0), ), 
                            required = True)
    
            accept_comment = SelectField(title = 'Comments',
                            validator = v.Int(), required = True,
                            values = ( ('Accept', 1),
                                     ('Not Accept, Show', 2),
                                     ('Not Accept, Now Show', 3) ) )
            accept_trackback = SelectField(title = 'Trackbacks',
                            validator = v.Int(), required = True,
                            values = ( ('Accept', 1), ('Not Accept, Show', 2),
                                     ('Not Accept, Now Show', 3) ) )
    
        class EditForm(AddForm):
            form_title = u'Edit Blog Entry'
    
        del EditForm['name']

        class AddCommentForm(Form):
            multipart = True
            form_title = 'Post a comment'
            button_title = 'Post a comment'
            submit = 'Post a comment'
            author_name = TextField(title = 'Your Name', args = {'size':20},
                            validator = v.String(), required = True)
            email = TextField(title = 'email', args = {'size':20},
                            validator = v.Email(), required = False)
            url = TextField(title = 'URL', args = {'size':60},
                            validator = v.URL(), required = False)
            title = TextField(title = 'title', args = {'size':60},
                            validator = v.String(), required = True)
            body = TextArea(title = 'Body',
                            args = dict(cols = 60, rows = 3, id = 'body'),
                            required = True)

        class RequireAuth(Form):
            form_title = 'Post a comment'
            button_title = 'Log in(%s) to post a comment' % config.auth_obj.TYPE
            submit = 'Log in(%s) to post a comment' % config.auth_obj.TYPE


        if kind == 'add':
            return AddForm()
        elif kind == 'edit':
            return EditForm()
        elif kind == 'comment_add':
            return AddCommentForm()
        elif kind == 'comment_add_auth':
            return RequireAuth()


    @expose
    @cache()
    def index(self):
        """
        A handler for blog entry.
        """
        self.smartphone = check_for_spartphone(self.request)
        self.blog = self.content.blog_object()
        self.get_comment_form = self.make_comment_form
        self.render(template = self.INDEX_TEMPLATE)

    def set_side_menu_items(self):
        """
        A method to obtain menu list.
            each items in list contains title and link in a tuple.
            if tuple has 3 items and the third one is sequence,
                it means menu has sub items.
        """
        _ = self.translate
        c = self.content
        addable = c.ADDABLE[:]
        addable.remove(BlogComment.TYPE)
        addable.remove(BlogTrackback.TYPE)
        self.side_menu_items = (
            ('/style/img/edit_icon.gif', 'Edit Entry',
                                         c.get_path()+'/edit' ),
            ('/style/img/list_icon.gif', 'Show Comment(s)',
                                         c.get_path()+'/comments' ),
            ('/style/img/list_icon.gif', 'Show Trackback(s)',
                                         c.get_path()+'/trackbacks' ),
            ('/style/img/add_icon.gif', 'Add', '#',
                [('/style/img/%s_icon.gif' % x.lower(),
                  x, (c.get_path()+'/add?type = %s')%x)
                        for x in addable],
            )
            )
        if c.get_parent():
            self.side_menu_items = (
                ('', 'Going up', c.get_parent().get_path()+'/list' ),
                )+self.side_menu_items

    edit = expose(authenticate(config.admin_auth)(BlogentryEditHandler()))


    @classmethod
    def make_add_form(cls, parent = None):
        """
        A method to create add form.
        """
        form = cls.get_form('add', self)
        cf = form['categories']
        blog = parent
        cf.values = [(x.title, x.category_id)
                    for x in blog.get_categories(end = 100)]
        form['accept_comment'].default = blog.accept_comment
        form['accept_trackback'].default = blog.accept_trackback
        return form


    #
    # comments
    #

    def make_comment_form(self):
        """
        A method to make form.
        """
        form = None
        if self.content.blog_object().auth_comment:
            form = self.get_form('comment_add_auth', self)
        if form == None:
            form = self.get_form('comment_add', self)

        form.action = self.content.get_path()+'/postcomment'
        return form

    postcomment = BlogcommentAddHandler()

def main(): pass;

if __name__ == '__main__':
    main()
