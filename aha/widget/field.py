# -*- coding: utf-8 -*-

#
# field.py
# The collection of fields definitions for coregeo 
#
# Copyright 2010 Atsushi Shibata
#

"""
The collection of fields definitions for aha

$Id: field.py 654 2010-08-23 02:02:08Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'

__all__ = ('BaseField', 'TextField', 'HiddenField', 'RadioField',
           'CheckboxGroup', 'PasswordField', 'ButtonField', 
           'CheckboxField', 'SelectField', 'TextArea', 'RichText', 
           'DescriptionField', 'FileField', 'ImageField')

import os

from lib import formencode
v = formencode.validators

from handler import MediaHandler, templatehandler
th = templatehandler

BASE_PATH = os.path.dirname(__file__)

class FieldMixin(object):
    """
    A mixin class for Field
    """

    def get_title(self):
        return self.title

    def get_desc(self):
        return self.desc

    def set_name(self, name):
        self.name = name

    def get_name(self):
        if not self.name:
            raise AttributeError('The field(%s) has no name' % self)
        return self.name

    def set_id(self, in_id):
        self.id = in_id

    def get_id(self):
        if not self.id:
            raise AttributeError('The field(%s) has no id' % self)
        return self.id


def keyvalue2str(k, v):
    body = ''
    if isinstance(v, int):
        body = "%s = %s " % (k, v)
    else:
        body = """%s = "%s" """ % (k, v)
    return body

class BaseField(FieldMixin, MediaHandler):
    """
    A base class of fields, handing basic functions of fields.
    """
    DEFAULT_ENGINE = 'mako'
    USE_FIELD_TITLE = True
    RENDER_WRAPPER = True
    counter = 0

    def __init__(self):
        """
        Initialization function
        """
        self._counter = BaseField.counter
        self.parent = None
        BaseField.counter += 1
        

    def __repr__(self):
        """
        Returning standard class representation
        """
        return "<%s name = '%s'>" % (self.__class__.__name__, self.name)

    def set_parent(self, parent):
        self.parent = parent

    def get_parent(self):
        return self.parent

    def render_body(self, value = None, engine = '', translate = unicode):
        """
        An abstract method to render field and return rendered string
        """
        return ''
        raise NotImplementedError()

class TextField(BaseField):
    """
    A field class representing text field
    """
    TYPE = 'text'
    # a flag to show the field requires whole posted value on validation
    REQUIRE_VALUES_ON_VALIDATE = False

    FIELD_TEMPLATE = """<input type = '%(TYPE)s' %(args)s />"""

    def __init__(self, name = None, enginename = '', title = '', desc = '',
                 args = {}, objects = [], required = False, default = '',
                 validator = None, generate_id = False, collapsable = False):
        """
        Initialization function
        """
        self.name = name
        self.title = title
        self.desc = desc
        self.args = args
        self.objects = objects
        self.validator = validator
        self.collapsable = collapsable
        if required:
            if isinstance(self.validator, (list, tuple)):
                self.validator+= (v.NotEmpty(), )
            elif not self.validator:
                self.validator = v.NotEmpty()
            else:
                self.validator = [self.validator]+[v.NotEmpty()]
        self.required = required
        self.default = default
        if enginename:
            self.enginename = enginename
        else:
            self.enginename = self.DEFAULT_ENGINE
        if hasattr(self, 'OBJECTS'):
            objects = self.OBJECTS[:]
        MediaHandler.__init__(self, objects)
        self.id = None
        if generate_id:
            # TBD
            pass
        BaseField.__init__(self)


    def expand_args(self, value = None, except_value = False, except_name = False):
        argstr = ''
        if self.name and not except_name:
            argstr+= keyvalue2str('name', self.name)
        if self.id:
            argstr+= keyvalue2str('id', self.id)
        for k in sorted(self.args):
            if k != 'value' and self.args[k]:
                argstr+= keyvalue2str(k, self.args[k])
        if not except_value:
            if value:
                argstr+= keyvalue2str('value', value)
            elif self.default:
                argstr+= keyvalue2str('value', self.default)
        return argstr

    def render_body(self, value = None, engine = '', translate = unicode):
        """
        An abstract method to render field and return rendered string
        """
        context = {
            'args':self.expand_args(value = value),
            'title':self.title,
            'TYPE':self.TYPE
            }

        return self.FIELD_TEMPLATE % context


    def validate(self, input_value = None):
        """
        A method to check validation of input value.
        returns value and error string
        """
        value = input_value
        try:
            if not self.validator:
                return input_value, None
            v = self.validator
            if isinstance(v, (list, tuple)):
                iv = input_value
                for i in self.validator:
                    iv = i.to_python(iv)
                value = iv
            else:
                value = v.to_python(input_value)
        except formencode.Invalid, e:
            return None, e

        return value, None

class PasswordField(TextField):
    """
    A field class representing text field
    """
    TYPE = 'password'
    # a flag to show the field requires whole posted value on validation
    REQUIRE_VALUES_ON_VALIDATE = False

class ButtonField(TextField):
    """
    A field class representing text field
    """
    TYPE = 'button'
    USE_FIELD_TITLE = False
    # a flag to show the field requires whole posted value on validation
    REQUIRE_VALUES_ON_VALIDATE = False
    FIELD_TEMPLATE = """<input type = "%(TYPE)s" %(args)s value = "%(title)s"/>"""


class CheckboxField(TextField):
    TYPE = 'checkbox'
    FIELD_TEMPLATE = ("""<input type = "%(TYPE)s" %(args)s /> %(field_desc)s""")

    def __init__(self, name = None, enginename = '', title = '', desc = '',
                 field_desc = '', value = '', args = {}, objects = [],
                 required = False, default = '',
                 validator = None, generate_id = False, collapsable = False):
        self.value = value
        self.field_desc = field_desc
        TextField.__init__(self, name, enginename, title, desc,
                           args, objects, required, id, validator, generate_id,
                           collapsable)

    def render_body(self, value = None, engine = '', translate = unicode):
        """
        An abstract method to render field and return rendered string
        """
        context = {}
        context['TYPE'] = self.TYPE
        context['args'] = self.expand_args(except_value = True)
        if self.value:
            context['args'] += ' '+keyvalue2str('value', self.value)
        if value:
            context['args'] += ' '+keyvalue2str('checked', 'checked')
        context['field_desc'] = self.field_desc
        tbody = self.FIELD_TEMPLATE

        return tbody % context


class HiddenField(TextField):
    """
    A field class representing text field
    """
    RENDER_WRAPPER = False
    TYPE = 'hidden'
    FIELD_TEMPLATE = """<input type = "hidden" %(args)s />"""

    def render_body(self, value = None, engine = '', translate = unicode):
        """
        An abstract method to render field and return rendered string
        """
        context = {}
        context['args'] = self.expand_args(value = value or self.default)

        return self.FIELD_TEMPLATE % context

class RadioField(TextField):
    """
    A field class representing text field
    """
    TYPE = 'radio'
    FIELD_TEMPLATE = ("""%for t, v in values:\n"""
                     """<%if v == value:\n"""
                     """    checked = 'checked'\n"""
                     """else:\n"""
                     """    checked = ''\n"""
                     """%>\n"""
                    """<input type = 'radio' ${args} value = '${v}'"""
                    """ ${checked}>"""
                    """<div class = 'multi-title'>${t}</div>\n"""
                    """    %if vertical:\n"""
                    """    <br />\n"""
                    """    %endif\n"""
                    """%endfor""")
    SELECT_ATTR = 'checked'
    FLID = 'RadioFieldFIELD_TEMPLATE'
    th.get_template(string = FIELD_TEMPLATE, tid = FLID)

    def __init__(self, name = None, enginename = '', title = '', desc = '',
                 values = [], args = {}, objects = [], required = False, default = '',
                 validator = None, generate_id = False, collapsable = False,
                 vertical = False):
        """
        Initialization function
        The argument values must be sequence of sequence,
            which shows pair of name and value in each radio button,
            such as (('Female', 1), ('Male', 2), ('Gay', 3)).
        """
        self.vertical = vertical
        if not values:
            raise ValueError("The argument 'values' must be given")
        self.values = values
        TextField.__init__(self, name, enginename, title, desc,
                           args, objects, required, default,
                           validator, generate_id, collapsable)

    def render_body(self, value = None, engine = '', translate = unicode):
        """
        An abstract method to render field and return rendered string
        """
        context = {}
        context['args'] = self.expand_args(except_value = True)
        context['values'] = self.values
        context['value'] = value or self.default
        context['vertical'] = self.vertical
        return templatehandler.render(context, self.enginename, tid = self.FLID)

class CheckboxGroup(TextField):
    """
    A field class representing text field
    """
    TYPE = 'cehckbox'
    REQUIRE_VALUES_ON_VALIDATE = True
    FIELD_TEMPLATE = ("""%for t, v in values:\n"""
                    """<%if v in value:\n"""
                    """    selected = 'checked'\n"""
                    """else:\n"""
                    """    selected = ''\n"""
                    """%>\n"""
                    """<input type = "checkbox" ${args} value = "${v}" """
                    """ name = "${name}_${v}" ${selected}>"""
                    """<span class = "multi-title">${t}</span>\n"""
                    """    %if vertical:\n"""
                    """    <br />\n"""
                    """    %endif\n"""
                    """%endfor""")
    SELECT_ATTR = 'checked'
    FLID = 'CheckboxGroupFIELD_TEMPLATE'
    th.get_template(string = FIELD_TEMPLATE, tid = FLID)

    def __init__(self, name = None, enginename = '', title = '', desc = '',
                 values = [], args = {}, objects = [], required = False, default = '',
                 validator = None, generate_id = False, vertical = False,
                 collapsable = False):
        """
        Initialization function
        The argument values must be sequence of sequence,
            which shows pair of name and value in each radio button,
            such as (('Female', 1), ('Male', 2), ('Gay', 3)).
        """
        self.vertical = vertical
        if not values:
            raise ValueError("The argument 'values' must be given")
        self.values = values
        TextField.__init__(self, name, enginename, title, desc,
                           args, objects, required, id, validator, generate_id,
                           collapsable)

    def validate(self, input_value = None):
        """
        A method to check validation of input value.
        returns value and error string
        """
        values = []
        pv = ['%s_%s' % (self.name, x[1]) for x in self.values]
        for k in input_value:
            if k in pv:
                values.append(input_value[k])
        if input_value.get(self.name, None):
            values.extend(input_value[self.name])
        if not self.validator:
            return ((self.name, values, None), )
        try:
            v_v = []
            for ov in values:
                v = self.validator
                if isinstance(v, (list, tuple)):
                    iv = ov
                    for i in self.validator:
                        iv = i.to_python(iv)
                    value = iv
                else:
                    value = v.to_python(ov)
                v_v.append(value)
        except formencode.Invalid, e:
            return ((self.name, None, e), )

        return ((self.name, v_v, None), )

    def render_body(self, value = None, engine = '', translate = unicode):
        """
        An abstract method to render field and return rendered string
        """
    
        context = {}
        context['args'] = self.expand_args(except_value = True, except_name = True)
        context['values'] = [(x, unicode(y)) for x, y in self.values]
        if value:
            context['value'] = [unicode(x) for x in value]
        else:
            context['value'] = []
        context['name'] = self.name
        context['vertical'] = self.vertical
        return templatehandler.render(context, self.enginename, tid = self.FLID)
        


class SelectField(RadioField):
    SELECT_TEMPLATE = ("""<select ${args}>\n"""
                     """% for t, v in values:\n"""
                     """<%if v == value:\n"""
                     """    selected = 'selected'\n"""
                     """else:\n"""
                     """    selected = ''\n"""
                     """%>\n"""
                     """    <option value = "${v}" ${selected}>"""
                     """ ${t} </option>\n"""
                     """% endfor\n"""
                     """</select>""")
    FLID = 'SelectFieldSELECT_TEMPLATE'
    th.get_template(string = SELECT_TEMPLATE, tid = FLID)

    def render_body(self, value = None, engine = '', translate = unicode):
        """
        An abstract method to render field and return rendered string
        """
        context = {}
        context['args'] = self.expand_args(except_value = True)
        context['values'] = self.values
        context['value'] = value or self.default
        return templatehandler.render(context, self.enginename, tid = self.FLID)


class TextArea(TextField):
    FIELD_TEMPLATE = """<textarea ${args}>${value | h}</textarea>"""
    FLID = 'TextAreaFIELD_TEMPLATE'
    th.get_template(string = FIELD_TEMPLATE, tid = FLID)

    def render_body(self, value = None, engine = '', translate = unicode):
        """
        An abstract method to render field and return rendered string
        """
        context = {}
        context['args'] = self.expand_args(except_value = True)
        if value:
            context['value'] = value
        else:
            context['value'] = ''
        tbody = self.FIELD_TEMPLATE
        return templatehandler.render(context, self.enginename, tid = self.FLID)


class RichText(TextField):
    FIELD_TEMPLATE = """
<script type = "text/javascript">
    tinyMCE.init({
    mode : %(mode)s ,
    theme : "advanced",
    plugins : "table,inlinepopups",
    theme_advanced_buttons1 : "formatselect,|,bold,italic,underline,separator,strikethrough,justifyleft,justifycenter,justifyright, justifyfull,blockquote,bullist,numlist,table,|,undo,redo,link,unlink,image,|,code",
    theme_advanced_buttons2 : "",
    theme_advanced_buttons3 : "",
    theme_advanced_toolbar_location : "top",
    theme_advanced_toolbar_align : "left",
    theme_advanced_statusbar_location : "bottom",
    theme_advanced_resizing : true,
    relative_urls : false,
    remove_script_host : false,

    });

</script>
<textarea %(args)s >%(value)s</textarea>
"""
    OBJECTS = (('/js/tiny_mce/tiny_mce.js', 'text/javascript'),)

    def render_body(self, value = None, engine = '', translate = unicode):
        """
        An abstract method to render field and return rendered string
        """
        context = {}
        context['args'] = self.expand_args(except_value = True)
        id = self.args.get('id', '')
        if id:
            context['mode'] = '"exact", "elements" : "%s"' % id
        else:
            context['mode'] = '"textareas"'
        if value:
            context['value'] = value
        else:
            context['value'] = ''
        tbody = self.FIELD_TEMPLATE
        return self.FIELD_TEMPLATE % context

class DescriptionField(TextField):
    """
    A field class representing text field
    """
    FIELD_TEMPLATE = """<p %(args)s >%(message)s</p>"""
    USE_FIELD_TITLE = False

    def render_body(self, value = None, engine = '', translate = unicode):
        """
        An abstract method to render field and return rendered string
        """
        context = {}
        context['args'] = self.expand_args(value = value, except_name = True)
        context['message'] = self.title

        return self.FIELD_TEMPLATE % context

class FileField(TextField):
    """
    A field class representing file field
    """
    TYPE = 'file'
    FIELD_TEMPLATE = ("""<input type = "%(TYPE)s" %(args)s />\n"""
                    """%(disable)s"""
                    )
    REPLACE_PREFIX = '__replace_field_'

    def get_desc(self):
        """
        a method to return description
        """
        return self.desc

    def render_body(self, value = None, engine = '', translate = unicode):
        """
        An abstract method to render field and return rendered string
        """
        context = {}
        context['args'] = self.expand_args(except_value = True)
        context['title'] = self.title
        context['TYPE'] = self.TYPE
        if value is None:
            context['disable'] = ''
        else:
            a = {'name':self.REPLACE_PREFIX+self.name,
                }
            astr = ''
            for k in a:
                astr+= keyvalue2str(k, a[k])
            t = '<input type = "checkbox" %s />replace\n'
            context['disable'] = t % astr

        return self.FIELD_TEMPLATE % context
        return templatehandler.render(context, self.enginename, tid = self.FLID)


    def validate(self, input_value = None):
        """
        A method to check validation of input value.
        returns value and error string
        """
        value = input_value
        v = self.validator
        try:
            v = self.validator
            if v:
                if isinstance(v, (list, tuple)):
                    iv = input_value
                    for i in self.validator:
                        iv = i.to_python(iv)
                    value = iv
                else:
                    value = v.to_python(input_value)
        except formencode.Invalid, e:
            return None, e

        return value, None


class ImageField(FileField):
    """
    A field class representing image field
    It displays image using value as path
    """
    TYPE = 'file'
    FIELD_TEMPLATE = ("""%if value:\n"""
                    """<img src = "${value}" height = ${height} /><br />\n"""
                    """%endif:\n"""
                    """<input type = '${TYPE}' ${args} />\n"""
                    """%if cbargs != 'disabled':\n"""
                    """<input type = "checkbox" ${cbargs} />Delete Image\n"""
                    """%endif\n"""
                    )
    FLID = 'ImageFieldFIELD_TEMPLATE'
    th.get_template(string = FIELD_TEMPLATE, tid = FLID)
    ERASE_PREFIX = '__replace_field_'

    def render_body(self, value = None, engine = '', translate = unicode):
        """
        An abstract method to render field and return rendered string
        """
        context = {}
        context['args'] = self.expand_args(except_value = True)
        context['title'] = self.title
        context['TYPE'] = self.TYPE
        if value is None:
            context['cbargs'] = 'disabled'
        else:
            a = {'name':self.ERASE_PREFIX+self.name,
                }
            astr = ''
            for k in a:
                astr+= keyvalue2str(k, a[k])
            context['cbargs'] = astr
            context['value'] = str(value)
        context['height'] = 48
        tbody = self.FIELD_TEMPLATE

        return templatehandler.render(context, self.enginename, tid = self.FLID)

