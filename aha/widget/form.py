# -*- coding: utf-8 -*-

#
# form.py
# The collection of forms, the class holds fields or forms themselves.
#
# Copyright 2010 Atsushi Shibata
#

"""
The collection of fields definitions for aha 

$Id: form.py 655 2010-08-23 02:02:23Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'

__all__ = ['FieldHolder', 'BaseForm', 'Form', 'ListForm', 'TableForm',
       'Fieldset', 'ULFieldset', 'RootTabbedFieldset', 'InnerTabbedFieldset', 
       'SelectiveFieldset']

import os

from field import BaseField
from handler import MediaHandler, templatehandler, get_tag
th = templatehandler

def uc(src, enc = 'utf-8', mode = 'replace'):
    """
    A function to convert input string to unicode, if it needs.
    """
    if not isinstance(src, unicode):
        return unicode(src, enc, mode)
    return src


def get_attr_fields(cls, bases, attrs, with_base_fields = True):
    """
    Create a list of form field instances from attributes in 'attrs'
    """
    fields = []
    for field_name, obj in attrs.items():
        if isinstance(obj, BaseField):
            ft = (field_name, attrs.pop(field_name))
            fields.append(ft)
    fields.sort(lambda x, y: cmp(x[1]._counter, y[1]._counter))

    if with_base_fields:
        for base in bases[::-1]:
            if hasattr(base, 'fields'):
                fields = base.fields + fields
    else:
        for base in bases[::-1]:
            if hasattr(base, 'fields'):
                fields = base.fields + fields

    return fields


class AttrFieldsMetaclass(type):
    """
    Metaclass that converts Field attributes to a 'fields' attributes.
    """
    def __new__(cls, name, bases, attrs):
        attrs['fields'] = get_attr_fields(cls, bases, attrs)
        new_class = super(AttrFieldsMetaclass,
                     cls).__new__(cls, name, bases, attrs)
        return new_class

    def __delitem__(self, key):
        """
        A special method to support item deletion
        """
        i = [ x for x in self.fields if x[0] == key ][0]
        self.fields.remove( i )

    def __setitem__(self, key, item):
        """
        A special method to support item assignment
        """
        i = [ (idx, x) for idx, x in enumerate(self.fields) if x[0] == key ]
        item.set_name(key)
        if i:
            self.fields[i[0][0]] = (item.get_name(), item)
        else:
            fields.append((item.get_name(), item))


class FieldHolder(object):
    """
    An abstract class which holds multiple field instance,
        representing form.
    It can be accessed like dictionary, 
    """
    __metaclass__ = AttrFieldsMetaclass

    def __init__(self, fields = []):
        """
        A initialization method.
        """
        if fields:
            self.fields = []
            for f in fields:
                self.fields.append( (f.get_name(), f) )
        # setting names.
        for n, f in self.fields:
            f.set_name(n)
            f.set_parent(self)

    def get_items(self):
        """
        A method to obtain items(name, object) by itaration
        """
        for n, o in self.fields:
            yield n, o
            if isinstance(o, FieldHolder):
                for n2, o2 in o.get_items():
                    yield n2, o2

    def __getitem__(self, key):
        """
        A special method to retrieve field item inside FieldHolder.
        In case key is integer(>= 0), this method returns item based on index.
        In case key is string, this method returns item based on name.
        """
        if isinstance(key, int):
            fls = [x for n, x in self.get_items()]
            if len(fls) <= key:
                raise IndexError( ("This instance has %s field(s)."
                       " given value(%s) is greater than that") % (
                                                len(fls), key))
            return fls[key]
        elif isinstance(key, str) or isinstance(key, unicode):
            fls = [x for n, x in self.get_items() if n == key]
            if not fls:
                raise KeyError("A form named '%s' does not exist" % (key))
            return fls[0]
        elif isinstance(key, slice):
            fl = [f for n, f in self.get_items()]
            return fl.__getitem__(key)

    def __iter__(self):
        """
        A special method to perform iteration.
        """
        for f in self[:]: yield(f)

    def __len__(self):
        """
        A special method to measure number of field(s) the instance has.
        """
        return len(self.fields)

    def __setitem__(self, key, item):
        """
        A special method to set item in key (index).
        It raises IndexError when other FieldHolder is in given index.
        """
        try:
            f = self[key]
        except KeyError, e:
            # assigned new item with string key.
            # append it on the bottom of the fields
            self.fields.append( (key, item) )
            return
        if f.parent != self:
            idx = f.parent.fields.index((f.name, f))
            f.parent[idx] = item
            return
        i = self.fields.index((f.name, f))
        self.fields[i] = (item.name, item)

    def __add__(self, item):
        """
        A special method to add field on the bottom of the fields.
           representing a operation such as from = form+field
        """
        self.fields.append( (item.get_name(), item) )
        return self

    def __iadd__(self, item):
        """
        A special method to add field on the bottom of the fields.
           representing a operation such as from += field
        """
        return self.__add__(item)

    def __delitem__(self, key):
        """
        A special method to support item deletion
        """
        i = self[key]
        self.fields.remove( (key, i) )



class BaseForm(FieldHolder):
    """
    A class definition to perform form, holding multiple fields.
    """
    DEFAULT_ENGINE = 'mako'
    FORM_TEMPLATE = """<div class = "form-container">
%if form_title:
<h2>${_(form_title)}</h2>
%endif

<form ${attrs}>
${fields|n}
${buttons|n}
</form>
</div>
"""
    FORM_TEMPLATE = """<div class = "form-container">
%(form_title)s

<form %(attrs)s>
%(fields)s
%(buttons)s
</form>
</div>
"""


    SFIELD_TEMPLATE = \
"""
<div class = '%(cls)s'>
%(label)s
%(error)s
%(desc)s
%(field)s
</div>
"""


    OBJECTS = ()
    OBJECTS = (('/css/defaultform.css', 'text/css'), )
    action = ''
    method = 'post'
    submit = 'OK'
    button_title = ''
    clear = ''
    confirm_clear = False
    confirm_message = 'Are you sure ? Your changes will disappeared.'
    confirm_js = (r"""if(confirm("%s") == true) """
                r"""{location.replace(%s); return false;}"""
                r"""else"""
                r"""{return false;}""")
    retun_url = 'document.referrer'
    clas = ''
    id = ''
    form_title = ''
    multipart = False

    #FMID = 'BaseFormFORM_TEMPLATE'
    #th.get_template(string = FORM_TEMPLATE, tid = FMID)

    def __init__(self, action = '', method = '', submit = '', clear = '', id = '',
                 multipart = False, clas = '', enginename = '', 
                 form_title = '', fields = []):
        """
        A initialize method.
        """
        def checkandsetattr(obj, attr, v):
            if v: setattr(obj, attr, v)
        checkandsetattr(self, 'action', action)
        checkandsetattr(self, 'method', method)
        checkandsetattr(self, 'submit', submit)
        checkandsetattr(self, 'clear', clear)
        checkandsetattr(self, 'clas', clas)
        checkandsetattr(self, 'multipart', multipart)
        checkandsetattr(self, 'form_title', form_title)
        checkandsetattr(self, 'id', id)
        self.errors = {}
        self.values = {}
        self.validate_result = {}
        if enginename:
            self.enginename = enginename
        else:
            self.enginename = self.DEFAULT_ENGINE
        # calling __init__() method of the super class.
        super(BaseForm, self).__init__(fields)

    def set_action(self, action):
        """
        A method to set action string
        """
        self.action = action

    def get_attr_string(self):
        """
        A method to obtain attributes fields.
        """
        attrs = ""
        if self.method: attrs += """method = "%s" """ % self.method;
        if self.action: attrs += """action = "%s" """ % self.action;
        if self.clas: attrs += """class = "%s" """ % self.clas;
        if self.id: attrs += """id = "%s" """ % self.id;
        if self.multipart: attrs  += """ enctype = "multipart/form-data" """
        return attrs

    def get_button_string(self, translate):
        """
        A method to obtain button fields.
        """
        buttons = ""
        if self.submit:
            s = """<input type = "submit" value = "%s" name = 'ok' />"""
            buttons += s % translate(self.submit)
        if self.clear:
            if self.confirm_clear:
                js = self.confirm_js
                js = self.confirm_js % (translate(self.confirm_message),
                                      self.retun_url)
                s = """<input type = "submit" value = "%s" name = 'cancel' """
                s += """onclick = 'javascript:%s' />""" % js
                s = s % self.clear
            else:
                s = """<input type = "reset" value = "%s" name = 'cancel' />"""
                s = s % self.clear
            buttons += s
        return buttons

    def render_field(self, field, values = {}, errors = {}, translate = unicode):
        """
        A method to return rendered string of one field
        """
        if isinstance(field, FieldHolder):
            return field.render_body(values, errors, translate = translate)
        else:
            fieldbody = uc(field.render_body(
                                values.get(field.get_name(), None),
                                translate = translate))
            if not field.RENDER_WRAPPER: return fieldbody;
            c = {}
            title = translate(field.get_title())
            c['cls'] = 'controlset'
            if field.required: c['cls'] += ' required'
            c['label'] = ''
            if title and field.USE_FIELD_TITLE:
                c['label'] = '<label>%s' % title
                if getattr(field, 'collapsable', False):
                    c['label'] += ("<img src = '/style/img/collapsed.gif'"
                                 "class = 'toggle-button'/>")
                c['label'] += "</label>"
            c['field'] = fieldbody
            e = errors.get(field.get_name(), None)
            if e:
                c['error'] = "<div class = 'error'><p>%s</p></div>" % e
                c['cls'] = 'controlset errors'
            else:
                c['error'] = ''
            if field.get_desc():
                d = translate(field.get_desc() or ' ').strip()
                c['desc'] = "<div class = 'description'>%s</div>" % d
            else:
                c['desc'] = ''
            c['field'] = fieldbody
            if getattr(field, 'collapsable', False):
                t = "<div class = 'togglable' style = 'display: none;'>%s</div>"
                c['field'] = t%fieldbody
            return self.SFIELD_TEMPLATE % c


    def render(self, values = {}, errors = {}, translate = unicode):
        """
        A method to obtain rendered string of all fields the instance has.
        """
        fields = ""
        for k, f in self.fields:
            fields += self.render_field(f, values, errors, translate)

        attrs = self.get_attr_string()
        buttons = self.get_button_string(translate)
        context = {'attrs':attrs, 'fields':fields, 'buttons':buttons,
                 'form_title':'', '_':translate}
        if self.form_title:
            context['form_title'] = '<h2>%s</h2>' % self.form_title

        return self.FORM_TEMPLATE % context
        #return th.render(context, self.enginename, tid = self.FMID)


    def validate(self, values, originals = {}):
        """
        A method to validate all fields.
        values is a dictionary which has pairs of key/input values.
        """
        self.errors = {}
        for f in self[:]:
            n = f.get_name()
            self.values[n] = values.get(n, None)
            e = None
            if f.REQUIRE_VALUES_ON_VALIDATE:
                t = f.validate(values)
                for name, value, error in t:
                    if error:
                        self.errors[name] = error
                    self.validate_result[name] = value
            else:
                v, e = f.validate(values.get(n, ''))
                self.validate_result[n] = v
            if e:
                self.errors[n] = e

        return self.errors

    def get_values(self):
        return self.values

    def get_objects(self, ct = ''):
        """
        A method to obtain bunch of media files associated to fields
            such as java script, css, etc.
        """
        objs = []
        for o in self.OBJECTS:
            if not ct or ct == o[1]:
                objs.append(o)

        for f in self[:]:
            objs.extend(f.get_objects(ct))

        return set(objs)

    def get_object_tag(self, ct = ''):
        """
        A method to obtain bunch of media files associated to fields
            such as java script, css, etc.
            in format of tag.
        """
        objs = []
        for o in self.OBJECTS:
            if not ct or ct == o[1]:
                objs.append( get_tag(o[0], o[1]) )
        for f in self[:]:
            objs.extend(f.get_object_tag(ct))
        o2 = []
        for x in objs:
            if x not in o2: o2.append(x)
        return o2


class Fieldset(BaseForm, BaseField):
    """
    A class that holds some fields.
    """
    DEFAULT_ENGINE = 'mako'
    FIELDSET_TEMPLATE = u"""<fieldset ${attrs}>
<legend>${title}</legend>
${fields}
</fieldset>
"""
    FSID = 'FieldsetFIELDSET_TEMPLATE'
    th.get_template(string = FIELDSET_TEMPLATE, tid = FSID)
    REQUIRE_VALUES_ON_VALIDATE = True

    def __init__(self, title = '', name = '', clas = '', enginename = '', fields = []):
        """
        A initialize method.
        """
        self.title = title
        self.name = name
        self.desc = ''
        self.clas = clas
        self.enginename = enginename
        BaseField.__init__(self)
        FieldHolder.__init__(self, fields)


    def render_body(self, values = {}, errors = {}, translate = unicode):
        """
        A method to obtain rendered string of all fields the instance has.
        """
        fields = ""
        for k, f in self.fields:
            fields += self.render_field(f, values, errors, translate)

        c = {}
        if self.clas: c['attrs'] = "class = '%s'" % self.clas
        c['fields'] = fields
        c['title'] = self.title
        c['attrs'] = ''
        c['clas'] = self.clas
        c['_'] = translate

        return uc(th.render(c, self.enginename, tid = self.FSID),
                       'utf-8', 'replace')

    def validate(self, values, originals = {}):
        """
        A method to validate all fields.
        values is a dictionary which has pairs of key/input values.
        """
        results = []
        for f in self[:]:
            n = f.get_name()
            e = None
            v, e = f.validate(values.get(n, ''))
            results.append( (f.get_name(), v, e) )

        return results

    def get_objects(self, ct = ''):
        """
        A method to obtain bunch of media files associated to fields
            such as java script, css, etc.
        """
        return []

class ULFieldset(Fieldset):
    """
    A class that holds some fields, putting container flat by using css.
    """
    FIELDSET_TEMPLATE = """<fieldset ${attrs} >
<legend>${title}</legend>
<ul class = "${clas}">
${fields}
</ul>
</fieldset>
"""

    INPUT_TEMPLATE = \
"""
<li>
%if title:
${title}
%endif:
${field}
%if error:
<div class = 'error'><p>${error}</p></div>
% endif
%if description:
<span class = 'description'>${description}</span>
% endif
</li>
"""
    FSID = 'ULFieldsetFIELDSET_TEMPLATE'
    th.get_template(string = FIELDSET_TEMPLATE, tid = FSID)
    IPID = 'ULFieldsetINPUT_TEMPLATE'
    th.get_template(string = INPUT_TEMPLATE, tid = IPID)


    def __init__(self, title = '', name = '', clas = 'flat',
                 enginename = '', fields = []):
        """
        A initialize method.
        """
        self.title = title
        self.name = name
        self.desc = ''
        self.clas = clas
        self.enginename = enginename
        BaseField.__init__(self)
        FieldHolder.__init__(self, fields)


    def render_field(self, field, values = {}, errors = {}, translate = unicode):
        """
        A method to return rendered string of one field
        """
        context = {}
        context['title'] = field.get_title()
        context['name'] = field.get_name()
        context['_'] = translate
        if isinstance(field, FieldHolder):
            return field.render_body(values, errors, translate = translate)
        else:
            context['field'] = uc(field.render_body(
                            values.get(field.get_name(), None),
                            translate = translate))
            e = errors.get(field.get_name(), None)
            if e:
                context['error'] = uc(e.message)
            else:
                context['error'] = ''
            desc = field.get_desc()
            if desc:
                context['description'] = translate(field.get_desc())
            return uc(th.render(context, self.enginename, tid = self.IPID))


class SelectiveFieldset(Fieldset):
    """
    A class that holds some fields, show one according to menu selection.
    """
    OBJECTS = (('/js/jquery.js', 'text/javascript'),
             ('/js/ajax.js', 'text/javascript'),)
    FIELDSET_TEMPLATE = """<fieldset ${attrs} >
<legend>${title}</legend>
<select name = "${name}" onChange = "for(i = 0; i<length; i++){ $('#'+options[i].value).hide(); } $('#'+options[selectedIndex].value).show();">
%for n, t in items:
<option name = "${n}_id" ${'selected'*(n == selection)}>${t}</optoin>
%endfor
</select>
${fields}
</fieldset>
"""

    FSID = 'SELECTIVEFieldsetFIELDSET_TEMPLATE'
    th.get_template(string = FIELDSET_TEMPLATE, tid = FSID)

    def __init__(self, title = '', name = '', clas = 'flat',
                 enginename = '', fields = [], innerfields = []):
        """
        A initialize method.
        """
        self.required = False
        self.title = title
        self.name = name
        self.desc = ''
        self.clas = clas
        self.enginename = enginename
        BaseField.__init__(self)
        FieldHolder.__init__(self, fields)
        self.innerfields = innerfields
        idx = 0
        for n, t, fs in innerfields:
            for f in fs:
                f.set_name(n+'__'+f.get_name())
                f.set_id(f.get_name()+'_id')
                idx += 1

    def render_body(self, values = {}, errors = {}, translate = unicode):
        """
        A method to return rendered string of one field
        """
        context = {}
        context['title'] = translate(self.get_title())
        context['name'] = self.get_name()
        context['attrs'] = self.get_attr_string()
        context['items'] = [ (n, t) for n, t, fs in self.innerfields]
        context['_'] = translate
        sub_v = {}
        sel = ''
        if self.get_name() in values:
            try:
                d = eval(values[self.get_name()])
                sel = d.get('_selection', '')
                v = [x for x in self.innerfields
                        if x[0] == sel][0]
                sub_v = {}
                for k in d:
                    if k != '_selection':
                        sub_v[v[0]+'__'+k] = d[k]
                    else:
                        sub_v[k] = d[k]
            except:
                pass
        if not sub_v:
            sub_v = values
        fb = ''
        for n, t, fs in self.innerfields:
            tfb = ''
            for f in fs:
                tfb += self.render_field(f, sub_v, errors)
            if n != sel:
                tfb = """<div id = "%s" class = "hidden">%s</div>""" % (n, tfb)
            else:
                tfb = """<div id = "%s">%s</div>""" % (n, tfb)
            fb += tfb
        context['fields'] = fb
        context['selection'] = sel
        return uc(th.render(context, self.enginename, tid = self.FSID))

    def validate(self, input_value = None):
        """
        A method to check validation of input value.
        returns value and error string
        """
        c_selection = input_value.get(self.name)
        c_fs = [(x[0], x[2]) for x in self.innerfields if x[0] == c_selection]
        if c_fs: c_id, c_fs = c_fs[0]
        vs = {}
        es = {}
        for f in c_fs:
            n = f.get_name()
            v, e = f.validate(input_value.get(n, ''))
            vs[n] = v
            if e:
                es[n] = e
        ks = set(vs.keys()) | set(es.keys())
        kvs = [[k, vs.get(k, None), es.get(k, None)] for k in ks]
        vsr = {}
        for k in vs:
            vsr[k.replace(c_id+'__', '')] = vs[k]
        vsr['_selection'] = c_selection

        return [[self.name, vsr, None]]+kvs

class RootTabbedFieldset(SelectiveFieldset):
    """
    A class that holds some fields, putting them into few tabs,
        sit on the top of the fields.
    """

    OBJECTS = (('/js/ui.core.js', 'text/javascript'),
             ('/js/ui.tabs.js', 'text/javascript'),
             ('/css/ui.tabs.css', 'text/css')
            )

    FIELDSET_TEMPLATE = """
<script type = "text/javascript">
    $(function() {
        $('#tabbed-fieldset > ul').tabs();
    });
</script>
<div id = "tabbed-fieldset" ${attrs} >
    <ul>
    %for n, f in enumerate(innerfields):
        <li><a href = "#tab-${n+1}"><span>${f[0]}</span></a></li>
    %endfor
    </ul>
    %for n, f in enumerate(innerfields):
    <div id = "tab-${n+1}">
        <p>
        %for f2 in f[1]:
        ${render_field(f2, values, errors, _)}
        %endfor
        </p>
    </div>
    %endfor
</div>
"""

    FSID = 'RootTFFieldsetFIELDSET_TEMPLATE'
    th.get_template(string = FIELDSET_TEMPLATE, tid = FSID)

    REQUIRE_VALUES_ON_VALIDATE = False

    def __init__(self, title = '', name = '', clas = 'flat',
                 enginename = '', fields = [], innerfields = []):
        """
        A initialize method.
        """
        self.required = False
        self.fields = []
        self.title = title
        self.name = name
        self.desc = ''
        self.clas = clas
        self.enginename = enginename
        BaseField.__init__(self)
        FieldHolder.__init__(self, fields)
        self.innerfields = innerfields
        self.fields = []
        for fs in innerfields:
            for f in fs[1]:
                self.fields.append( (f.get_name(), f) )


    def render_body(self, values = {}, errors = {}, translate = unicode):
        """
        A method to obtain rendered string of all fields the instance has.
        """

        c = {}
        if self.clas: c['attrs'] = "class = '%s'" % self.clas
        c['innerfields'] = self.innerfields
        c['title'] = self.title
        c['attrs'] = ''
        c['values'] = values
        c['errors'] = errors
        c['clas'] = self.clas
        c['render_field'] = self.render_field
        c['_'] = translate

        return uc(th.render(c, self.enginename, tid = self.FSID),
                       'utf-8', 'replace')

    def validate(self, input_value = None):
        """
        A method to check validation of input value.
        returns value and error string
        """
        return None, None

class Form(BaseForm):
    """
    A class definition to perform form, showing fields in div elements.
    """
    OBJECTS = (('/css/defaultform.css', 'text/css'), )

    def render(self, values = {}, errors = {}, translate = unicode):
        """
        A method to obtain rendered string of all fields the instance has.
        """
        fields = ""
        for k, f in self.fields:
            fields += self.render_field(f, values, errors, translate)

        attrs = self.get_attr_string()
        buttons = self.get_button_string(translate)
        context = {'title':translate(self.button_title), 'name':'', 'error':'',
                 'description':''}
        context['field'] = buttons
        context['cls'] = 'controlset'
        buttons = '<div class = "submit">%s</div>' % buttons

        context2 = {'attrs':attrs, 'fields':fields, 'buttons':buttons,
                 'form_title':'', '_':translate}
        if self.form_title:
            context2['form_title'] = '<h2>%s</h2>' % self.form_title

        return self.FORM_TEMPLATE % context2

        """
        context2 = {'attrs':attrs, 'fields':fields, 'buttons':buttons,
                 'form_title':self.form_title, '_':translate}

        return uc(th.render(context2, self.enginename, tid = self.FMID),
                            'utf-8', 'replace')
        """


class ListForm(Form):
    """
    A class definition to perform form, showing fields in <li> ... </li>.
    """

    FORM_TEMPLATE = """<form %s>
<ul>
%s
<li class = "field">
%s
</li>
</ul>
</form>"""

    FIELD_TEMPLATE = \
"""<li class = "field">
%if title:
<label for = "${name}" >${title}</label>
% endif
${field}
%if error:
<div class = 'error'>${error}</div>
% endif
%if description:
<div class = 'description'>${description}</div>
% endif
</li>
"""

    FTID = 'ListFormFIELD_TEMPLATE'
    th.get_template(string = FIELD_TEMPLATE, tid = FTID)


class TableForm(Form):
    """
    A class definition to perform form, showing fields in <li> ... </li>.
    """
    FORM_TEMPLATE = """<form ${attrs}>
<table>
%if form_title:
<tr><th colspan = "2">
${form_title}
</td></tr>
%endif
<tbody>
${fields}
<tr><td colspan = "2">
${buttons|n}
</td></tr>
</tbody>
</table>
</form>"""

    FIELD_TEMPLATE = \
"""<tr>
<td>
%if title:
<label for = "${name}" >${title}</label>
% endif
%if description:
<div class = 'description'>${description}</div>
% endif
</td>
<td>
${field}
%if error:
<div class = 'error'>${error}</div>
% endif
</td>
</tr>
"""


    FMID = 'TableFormFORM_TEMPLATE'
    th.get_template(string = FORM_TEMPLATE, tid = FMID)
    FTID = 'TableFormFIELD_TEMPLATE'
    th.get_template(string = FIELD_TEMPLATE, tid = FTID)
