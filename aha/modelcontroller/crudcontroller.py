# -*- coding: utf-8 -*-
##############################################################################
#
# crudcontroller.py
# Classes to handle CRUD form for a model.
#
# Copyright (c) 2010 Webcore Corp. All Rights Reserved.
#
##############################################################################
""" crudcontroller.py - Classes to handle CRUD form for a model.

$Id: crudcontroller.py 652 2010-08-23 01:58:52Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'



import os
from datetime import datetime
from hashlib import md5
import logging

from aha.controller.decorator import expose

from lib import formencode

from aha.controller.makocontroller import MakoTemplateController

from formcontrol import FormControl, handle_state, validate
FC = FormControl

from aha.controller.translation import *

from mako import template
from mako.lookup import TemplateLookup

tlookup = None

STATE_KEY = 'fc_state'


class CRUDHandlerMetaClass(type):
    def __new__(cls, name, bases, attrs):
        cl = []
        for c in bases[::-1]:
            if hasattr(c, 'FORMCONTROLLERS'):
                cl = c.FORMCONTROLLERS
            for fck in cl:
                if hasattr(c, fck) and fck in attrs :
                    ofc = getattr(c, fck)
                    nfc = attrs[fck]
                    states = set(nfc.get_states())
                    states |= set(ofc.get_states())
                    for s in states:
                        v = None
                        if s in nfc.get_states():
                            v = nfc.get_validator(s)
                        if not v:
                            ov = None
                            if s in ofc.get_states():
                                ov = ofc.get_validator(s)
                            if ov: nfc.add_validator(s, ov)
                        p = None
                        if s in nfc.get_states():
                            p = nfc.get_processor(s)
                        if not p:
                            op = None
                            if s in ofc.get_states():
                                op = ofc.get_processor(s)
                            if op: nfc.add_method(s, op)

        new_class = super(CRUDHandlerMetaClass,
                          cls).__new__(cls, name, bases, attrs)
        return new_class

# Request handler classes

class CRUDHandlerBase(object):
    """
    A base class to handle one of the CRUD form
        like create/update/delete objects.
    Subclasses are usually bound as attributes of controller class.
    """
    __metaclass__ = CRUDHandlerMetaClass

    FC = FormControl()
    FORMCONTROLLERS = ('FC', )
    _exposed_ = True

    def __call__(self, controller):
        """
        A method to handle request.
        This method dispatches to internal methods based on state.
        
        The argument "controller" is the instance of controller class.
        """
        from aha.widget.field import HiddenField
        # Making form
        controller.form = self.make_form(controller)
        # Adding hidden field to store session_key
        key = controller.get_sessionkey()
        controller.form['session_key'] = HiddenField(name = 'session_key',
                                                   default = key)
        # Getting state
        state = controller.get_state(key)
        state = self.FC.validate(state, self, controller = controller)
        controller.set_state(key, state)
        return self.FC.process(state, self, controller)

    def get_value(self, controller):
        """
        A method to obtain value from db, to supply to form fields.
        You must override this method in your subclass.
        """
        raise NotImplementedError()

    def make_form(self, controller):
        """
        A method to create edit form.
        You must override this method in your subclass.
        """
        raise NotImplementedError()

    @FC.handle_state(FC.PROCESSING, FC.FAILURE)
    def show_form(self, controller):
        """
        A method to show edit form.
        You must override this method in your subclass.
        """
        raise NotImplementedError()

    @FC.handle_state(FC.SUCCESS)
    def process_data(self, controller):
        """
        A method to process posted values, changing values etc.
        You must override this method in your subclass.
        """
        raise NotImplementedError()

    @FC.handle_validate(FC.INITIAL, FC.PROCESSING, FC.FAILURE)
    def do_validate(self, state, controller):
        """
        A validator method for edit transition
        """
        if state == FC.INITIAL:
            controller.form.values = self.get_value(controller)
            return FC.PROCESSING
        elif controller.request.POST:
            controller.form.values = dict([(x, controller.request.get(x))
                                   for x in controller.request.arguments()])
        e = controller.form.validate(controller.form.values)
        if e:
            # Some error occured
            return FC.FAILURE
        elif state == FC.INITIAL:
            return FC.PROCESSING
        else:
            return FC.SUCCESS

class CRUDControllerMixIn(object):
    """A controller that handles CRUD form of a Model.
       Some methods should be overridden.
       You can specify encode by using class attribute, something like.
       _charset = 'Shift-JIS'
    """

    # FormControl() instances.
    EDIT_FC = FormControl()
    ADD_FC = FormControl()
    DELETE_FC = FormControl()
    FORMCONTROLLERS = ('EDIT_FC', 'ADD_FC', 'DELETE_FC')

    PAGE_SIZE = 20

    #
    # Managing state - state information of CRUD form.
    #

    def get_state(self, key):
        """
        A method to get state
        """
        state = FC.INITIAL
        if key not in self.session:
            self.set_state(key, state)
        else:
            state = self.session[key]
        return state

    def set_state(self, key, state = FC.INITIAL):
        """
        A method to set state
        """
        if key not in self.session:
            state = FC.INITIAL
            self.session[key] = state
        else:
            self.session[key] = state
        self.session.put()

    def delete_state(self, key):
        """
        A method to delete state in session
        """
        try:
            del self.session[key]
        except:
            pass

    def get_sessionkey(self):
        """
        A method to obtain session key
        """
        key = self.request.params.get('session_key', '')
        if not key:
            key = md5(str(datetime.now())).hexdigest()
        return key

    #
    # Object listing
    #
    #class ListForm(Form):
    #    submit = "Delete"

    @expose
    def list(self):
        """
        A method to show list of object, add and delete
        """
        raise NotImplementedError()

    def get_objects(self, start = 0, end = -1):
        """
        A method to obtain list of objects, according to given arguments.
        -1 in end means getting all objects from start.
        Subclasses must override this method.
        """
        raise NotImplementedError()


class EditHandler(CRUDHandlerBase):
    """
    A hander to dispatch update process
    """
    FC = FormControl()
    FORM_TEMPLATE = 'form'

    def get_value(self, controller):
        """
        A method to obtain value from db, to supply to form fields.
        """
        key = controller.params.get('id', '')
        fd = controller.MODEL.get(key)
        d = {}
        for f in controller.form:
            n = f.get_name()
            if hasattr(fd, n):
                d[n] = getattr(fd, n)

        return d

    def make_form(self, controller):
        """
        A method to create edit form.
        You should override this method in your subclass
            in case you want to change the way of form creation.
        """
        form = controller.EditForm()
        key = controller.params.get('id', '')
        form.set_action(controller.BASEPATH+'/edit/'+key)
        return form

    @FC.handle_state(FC.PROCESSING, FC.FAILURE)
    def show_form(self, controller):
        controller.objects = controller.form.get_object_tag()
        controller.render(template = self.FORM_TEMPLATE)

    @FC.handle_state(FC.SUCCESS)
    def process_data(self, controller):
        key = controller.params.get('id', '')
        ob = controller.MODEL.get(key)
        v = self.form.validate_result
        for k in v:
            if hasattr(ob, k):
                setattr(ob, k, v[k])
        ob.put()

        controller.delete_state(self.get_sessionkey())
        controller.redirect(self.BASEPATH)


class AddHandler(CRUDHandlerBase):
    """
    A hander to dispatch create process
    """
    FC = FormControl()
    FORM_TEMPLATE = 'form'

    def get_value(self, controller):
        """
        A method to obtain value from db, to supply to form fields.
        """
        return {}

    def make_form(self, controller):
        """
        A method to create edit form.
        You may override this method in your subclass.
        """
        form = controller.AddForm()
        form.set_action(controller.BASEPATH+'/add')
        return form

    @FC.handle_state(FC.PROCESSING, FC.FAILURE)
    def show_form(self, controller):
        controller.objects = controller.form.get_object_tag()
        controller.render(template = self.FORM_TEMPLATE)

    @FC.handle_state(FC.SUCCESS)
    def process_data(self, controller):
        d = {}
        v = controller.form.validate_result
        ob = controller.MODEL(**v)
        ob.put()

        controller.set_state(FC.INITIAL)
        controller.redirect(controller.BASEPATH)


class ModelCRUDController(MakoTemplateController, CRUDControllerMixIn):
    """
    A controller that handles CRUD form of particular model.
    """
    EDIT_FC = FormControl()
    ADD_FC = FormControl()
    DELETE_FC = FormControl()
    MODEL = None
    LISTPAGE_TITLE = ''
    BASEPATH = ''
    EDIT_BASE = ''
    INDEX_TEMPLATE = '/model_index'
    FORM_TEMPLATE = 'form'

    LIST_ORDER = '-created_at'

    def __init__(self, hnd, params = {}):
        """
        Initialize method.
        """
        # set locale by seeing Accept-Language header
        
        langs = hnd.request.headers.get('Accept-Language', '').split(',')
        langs = get_languages(langs)
        formencode.api.set_stdtranslation(domain = "FormEncode",languages = langs)
        self.translate = get_gettextobject('aha', langs).ugettext
        self._ = self.translate

        super(ModelCRUDController, self).__init__(hnd, params)

    def get_index_object(self, start, end):
        """
        A method to generate query,
             that gets bunch of object to show in the list
        """
        query = self.MODEL.all()
        query.order(self.LIST_ORDER)
        self.edit_base = self.EDIT_BASE
        self.link_title = 'title'
        return list(query.fetch(self.PAGE_SIZE, offset = start))

    @expose
    def index(self):
        """
        A method to show list of published object.
        """
        start = int(self.params.get('id', '0'))
        end = start+self.PAGE_SIZE
        filt = self.params.get('id2', '')
        self.page_title = self.LISTPAGE_TITLE or \
                            'List of %s' % self.MODEL.__class__.__name__
        self.path = self.BASEPATH

        self.objects = self.get_index_object(start, end)
        self.prev = u'Prev'
        self.next = u'Next'
        if start:
            self.prev = u'<a href = "%s%s">前</a>'%\
                                    (self.path, max(start-self.PAGE_SIZE, 0))
        self.next = u'<a href = "%s%s">次</a>'%(self.path, start+self.PAGE_SIZE)
        self.render(template = self.INDEX_TEMPLATE)

    edit = EditHandler()

    add = AddHandler()


def main(): pass;

