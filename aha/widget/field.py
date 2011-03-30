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
    A mixin class for the Field.
    """

    def get_title(self):
        """
        A method to get title of the field.
        """
        return self.title

    def get_desc(self):
        """
        A method to get description of the field.
        """
        return self.desc

    def set_name(self, name):
        """
        A method to set the name of the field.
        
        :param name: A name for the firld.
        """
        self.name = name

    def get_name(self):
        """
        A method to get the name of the field.
        """
        if not self.name:
            raise AttributeError('The field(%s) has no name' % self)
        return self.name

    def set_id(self, in_id):
        """
        A method to set id of the field.

        :param in_id: A id for the firld.
        """
        self.id = in_id

    def get_id(self):
        """
        A method to get id of the field.
        """
        if not self.id:
            raise AttributeError('The field(%s) has no id' % self)
        return self.id


def keyvalue2str(k, v):
    """
    A function to convert key - value convination to string.
    """
    body = ''
    if isinstance(v, int):
        body = "%s = %s " % (k, v)
    else:
        body = """%s = "%s" """ % (k, v)
    return body

class BaseField(FieldMixin, MediaHandler):
    """
    A base class of fields, handing basic functions of fields.
    The class has some attributes::
    
    :DEFAULT_ENGINE: A template engine to render result for fields.
    :USE_FIELD_TITLE: A flag to determine whether to write title 
    for the rendering result.
    :RENDER_WRAPPER: A flag to determine whether write wrapper
    including label, description etc. for the rendering result.
    """
    DEFAULT_ENGINE = 'mako'
    USE_FIELD_TITLE = True
    RENDER_WRAPPER = True
    counter = 0

    def __init__(self):
        """
        Initialization method.
        """
        self._counter = BaseField.counter
        self.parent = None
        BaseField.counter += 1
        

    def __repr__(self):
        """
        A method to return standard class representation.
        """
        return "<%s name = '%s'>" % (self.__class__.__name__, self.name)

    def set_parent(self, parent):
        """
        A method to set parent form.
        """
        self.parent = parent

    def get_parent(self):
        """
        A method to get parent form.
        """
        return self.parent

    def render_body(self, value = None, engine = '', translate = unicode):
        """
        An abstract method to render field and return rendered string.
        """
        return ''
        raise NotImplementedError()

class TextField(BaseField):
    """
    A field class representing simple text field.
    Initialization takes following arguments.

    :param name: A name of the field
    :param enginename: A template engine to render result.
    :param title: A title of the field.
    :param desc: A description of the field.
    :param args: Arguments to be rendered in response.
    :param objects: Files such as css, js to be used for the field.
    They are rendered along with the filed.
    :param required: A flag to determine the field is required or not.
    :param default: A default value of the field.
    :param validator: A validator function to be used for the input.
    :param generate_id: (Not in use)Flag to determine if the id
    is to be generated automatically.
    :param collapsable: A flag to determine 
    if the field is collapsable or not.
    """
    TYPE = 'text'
    # a flag to show the field requires whole posted value on validation
    REQUIRE_VALUES_ON_VALIDATE = False

    FIELD_TEMPLATE = """<input type = '%(TYPE)s' %(args)s />"""

    def __init__(self, name = None, enginename = '', title = '', desc = '',
                 args = {}, objects = [], required = False, default = '',
                 validator = None, generate_id = False, collapsable = False):
        """
        Initialization function.
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


    def expand_args(self, value = None,
                    except_value = False, except_name = False):
        """
        A method to expand attributes in HTML.
        An args {'class': 'foo', 'style': 'float: right;'} is expanded as
        "class='foo' style='float: right;'".
        Attributes self.id, self.name also are expanded as attributes.
        """
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
        A method to render field and return result as a string.
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
        returns validated and casted value and error string
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
    A field class representing password field.
    """
    TYPE = 'password'
    # a flag to show the field requires whole posted value on validation
    REQUIRE_VALUES_ON_VALIDATE = False

class ButtonField(TextField):
    """
    A field class representing button field.
    """
    TYPE = 'button'
    USE_FIELD_TITLE = False
    # a flag to show the field requires whole posted value on validation
    REQUIRE_VALUES_ON_VALIDATE = False
    FIELD_TEMPLATE = """<input type = "%(TYPE)s" %(args)s value = "%(title)s"/>"""


class CheckboxField(TextField):
    """
    A field class representing checkbox field.
    Initialization method takes following arguments.

    :param name: A name of the field
    :param enginename: A template engine to render result.
    :param title: A title of the field.
    :param desc: A description of the field.
    :param args: Arguments to be rendered in response.
    :param objects: Files such as css, js to be used for the field.
    They are rendered along with the filed.
    :param required: A flag to determine the field is required or not.
    :param default: A default value of the field.
    :param validator: A validator function to be used for the input.
    :param generate_id: (Not in use)Flag to determine if the id
    is to be generated automatically.
    :param collapsable: A flag to determine 
    if the field is collapsable or not.
    """
    
    TYPE = 'checkbox'
    FIELD_TEMPLATE = ("""<input type = "%(TYPE)s" %(args)s /> %(field_desc)s""")

    def __init__(self, name = None, enginename = '', title = '', desc = '',
                 field_desc = '', value = '', args = {}, objects = [],
                 required = False, default = '',
                 validator = None, generate_id = False, collapsable = False):
        """
        A initialization method.
        """
        self.value = value
        self.field_desc = field_desc
        TextField.__init__(self, name, enginename, title, desc,
                           args, objects, required, id, validator, generate_id,
                           collapsable)

    def render_body(self, value = None, engine = '', translate = unicode):
        """
        A method to render field and return rendered string.
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
    A field class representing hidden field.
    """
    RENDER_WRAPPER = False
    TYPE = 'hidden'
    FIELD_TEMPLATE = """<input type = "hidden" %(args)s />"""

    def render_body(self, value = None, engine = '', translate = unicode):
        """
        A method to render field and return rendered string.
        """
        context = {}
        context['args'] = self.expand_args(value = value or self.default)

        return self.FIELD_TEMPLATE % context

class RadioField(TextField):
    """
    A field class representing radio button field.
    Initialization takes following arguments.

    :param name: A name of the field
    :param enginename: A template engine to render result.
    :param title: A title of the field.
    :param desc: A description of the field.
    :param value: A values used to make radio buttons. Values must be
    sequence of pairs, such as (('Female', 1), ('Male', 2), ('Gay', 3))
    :param args: Arguments to be rendered in response.
    :param objects: Files such as css, js to be used for the field.
    They are rendered along with the filed.
    :param required: A flag to determine the field is required or not.
    :param default: A default value of the field.
    :param validator: A validator function to be used for the input.
    :param generate_id: (Not in use)Flag to determine if the id
    is to be generated automatically.
    :param collapsable: A flag to determine 
    if the field is collapsable or not.
    :param vertical: A flag to determine whether buttons lies vertically.
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
        Initialization function.
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
        A method to render field and return rendered string.
        """
        context = {}
        context['args'] = self.expand_args(except_value = True)
        context['values'] = self.values
        context['value'] = value or self.default
        context['vertical'] = self.vertical
        return templatehandler.render(context, self.enginename, tid = self.FLID)

class CheckboxGroup(TextField):
    """
    A field class representing checkbox field.
    Initialization takes following arguments.

    :param name: A name of the field
    :param enginename: A template engine to render result.
    :param title: A title of the field.
    :param desc: A description of the field.
    :param value: A values used to make radio buttons. Values must be
    sequence of pairs, such as (('Female', 1), ('Male', 2), ('Gay', 3))
    :param args: Arguments to be rendered in response.
    :param objects: Files such as css, js to be used for the field.
    They are rendered along with the filed.
    :param required: A flag to determine the field is required or not.
    :param default: A default value of the field.
    :param validator: A validator function to be used for the input.
    :param generate_id: (Not in use)Flag to determine if the id
    is to be generated automatically.
    :param collapsable: A flag to determine 
    if the field is collapsable or not.
    :param vertical: A flag to determine whether buttons lies vertically.
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
        Initialization function.
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
        It returns value and error string
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
        A method to render field and return rendered string
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
    """
    A field class representing select field.
    """
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
        A method to render field and return rendered string
        """
        context = {}
        context['args'] = self.expand_args(except_value = True)
        context['values'] = self.values
        context['value'] = value or self.default
        return templatehandler.render(context, self.enginename, tid = self.FLID)


class TextArea(TextField):
    """
    A field class representing text area field.
    """
    FIELD_TEMPLATE = """<textarea ${args}>${value | h}</textarea>"""
    FLID = 'TextAreaFIELD_TEMPLATE'
    th.get_template(string = FIELD_TEMPLATE, tid = FLID)

    def render_body(self, value = None, engine = '', translate = unicode):
        """
        A method to render field and return rendered string
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
    """
    A field class representing text area field that has WYSIWYG editor.
    """
    FIELD_TEMPLATE = """
<script type = "text/javascript">
    tinyMCE.init({
    mode : %(mode)s ,
    theme : "advanced",
    plugins : "table,inlinepopups",
    theme_advanced_buttons1 : "formatselect,styleselect, |,bold,italic,underline,separator,strikethrough,justifyleft,justifycenter,justifyright, justifyfull,blockquote,bullist,numlist,table,|,undo,redo,link,unlink,image,|,code",
    theme_advanced_buttons2 : "",
    theme_advanced_buttons3 : "",
    theme_advanced_toolbar_location : "top",
    theme_advanced_toolbar_align : "left",
    theme_advanced_statusbar_location : "bottom",
    theme_advanced_resizing : true,
    theme_advanced_styles : "code=code;float-right=floatright;float-left=floatleft",
    theme_advanced_blockformats : "p,h1,h2,h3,h4,blockquote,div",
    relative_urls : false,
    remove_script_host : false,

    });

</script>
<textarea %(args)s >%(value)s</textarea>
"""
    OBJECTS = (('/js/tiny_mce/tiny_mce.js', 'text/javascript'),)

    def render_body(self, value = None, engine = '', translate = unicode):
        """
        A method to render field and return rendered string
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
    A field class representing description field
    """
    FIELD_TEMPLATE = """<p %(args)s >%(message)s</p>"""
    USE_FIELD_TITLE = False

    def render_body(self, value = None, engine = '', translate = unicode):
        """
        A method to render field and return rendered string
        """
        context = {}
        context['args'] = self.expand_args(value = value, except_name = True)
        context['message'] = self.title

        return self.FIELD_TEMPLATE % context

class FileField(TextField):
    """
    A field class representing file field, used for uploading file.
    """
    TYPE = 'file'
    FIELD_TEMPLATE = ("""<input type = "%(TYPE)s" %(args)s />\n"""
                    """%(disable)s"""
                    )
    REPLACE_PREFIX = '__replace_field_'

    def get_desc(self):
        """
        a method to return description.
        """
        return self.desc

    def render_body(self, value = None, engine = '', translate = unicode):
        """
        A method to render field and return rendered string
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
        It returns value and error string.
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
    It displays image using value as path.
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
        A method to render field and return rendered string
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

