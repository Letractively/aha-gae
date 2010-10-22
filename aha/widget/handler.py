# -*- coding: utf-8 -*-

#
# handler.py
# A collection of classes which handle file, template, etc.
#
# Copyright 2010 Atsushi Shibata
#

"""
handler.py
A collection of classes which handle file, template, etc.

$Id: handlers.py 651 2010-08-16 07:46:13Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'

import md5

from mako.template import Template
from mako.lookup import TemplateLookup
import os

__all__ = ('get_tag', 'MediaHandler', 'TemplateHandler', 'TemplateEngine',
         'templatehandler')

"""
The collection of fields definitions for aha 
"""

TEMPLATES = {'text/css':
           ("""<link rel = "stylesheet" type = "text/css" """
            """href = "%s" />"""),
           'text/javascript':
           ("""<script type = "text/javascript" """
            """src = "%s"></script>"""),
            }

def get_tag(file, contenttype):
    """
    A function to obtain tag from file and content-type. 
    """
    return TEMPLATES[contenttype] % file

class MediaHandler(object):
    """
    A class storing URI for media file, such as css, java script
             along with content type
    """


    def __init__(self, objects = []):
        """
        Initialization method.
        The argument objects must be sequence of sequence,
            like (('foo.css', 'text/css'), ('bar.js', 'text/javascript')).
        """
        self.order = []
        self.objects = {}
        if objects:
            for uri, ct in objects:
                self.add_object(uri, ct)


    def add_object(self, uri, contenttype):
        """
        A method to add given media object to the instance, keeping order.
        """
        if uri not in self.objects:
            self.order.append(uri)
            self.objects[uri] = contenttype


    def get_objects(self, ct = ''):
        """
        A method to return whole media objects in order.
        Returning value is list of tupple, 
            like (('foo.css', 'text/css'), ('bar.js', 'text/javascript')).
        """
        retl = []
        for k in self.order:
            if not ct or ct == self.objects[k]:
                retl.append( (k, self.objects[k]) )
        return retl



    def get_object_tag(self, ct = ''):
        """
        A method to obtain tag to read object.
        """
        retl = []
        for k in self.order:
            if not ct or ct == self.objects[k]:
                retl.append( get_tag(k, self.objects[k]) )
        return retl

DEFAULTENGINE = 'mako'

class TemplateHandler(object):
    """
    An abstract class to handle multiple template engine.
    """

    def __init__(self): 
        """
        Initialization methid
        """
        self.engines = {}
        self.defaultengine = DEFAULTENGINE


    def set_defaultengine(self, enginename):
        """
        A method to set default template engine name to given enginename
        """
        self.defaultengine = enginename


    def get_defaultengine(self):
        """
        A method to get default template engine name to given enginename
        """
        return self.defaultengine


    def add_engine(self, engine):
        """
        A method to add a template engine
        """
        if not isinstance(engine, TemplateEngine):
            raise TypeError( ("The argument 'engine' must be "
                              "a subclass of TemplateEngine") )
        self.engines[engine.get_name()] = engine


    def get_engine(self, enginename = ''):
        """
        A method to obtain TemplateEngine by using given enginename
        """
        if not enginename: enginename = self.defaultengine;
        if enginename not in self.engines:
            raise KeyError("No template engine for '%s'" % enginename)

        return self.engines[enginename]

    def get_template(self, enginename = '', path = '', string = '', tid = ''):
        """
        A method to render template by using given template string, context.
        """
        if not enginename: enginename = self.defaultengine;
        te = self.get_engine(enginename)
        return te.get_template(path = path, string = string, tid = tid)


    def render(self, context, enginename = '', path = '', string = '', tid = ''):
        """
        A method to render template by using given template string, context.
        """
        if not enginename: enginename = self.defaultengine;
        te = self.get_engine(enginename)
        return te.render(context, path = path, string = string, tid = tid)


class TemplateEngine(object):
    """
    An abstract class to store information, utility for template engine.
    """

    ENGINE_NAME = 'N/A'
    DEFAULT_EXTENSION = ''
    cache = {}

    def set_template_cache(self, t, tid = ''):
        """
        A method to set template by using given tid(template id).
        When tid is not given, it produce template id from template.
        """
        if not tid:
           tid = md5.new(str(t)).hexdigest()
        self.cache[tid] = t
        return tid

    def get_template_cache(self, tid):
        """
        A method to retrieve template by using given tid(template id).
        """
        return self.cache.get(tid, None)

    def get_cache_tid(self, t):
        """
        A method to retrieve template id by using given template object.
        """
        tid = md5.new(str(t)).hexdigest()
        if tid in self.cache: return tid
        for k in self.cache:
            if t == self.cache[k]: return k


    def get_name(self):
        """
        A method to obtain template engine name.
        """
        return self.ENGINE_NAME


    def get_template(self, path = '', string = '', tid = ''):
        """
        A method to obtain template object, by using given path or string.
        When argment path is given, method produce template string via file.
        When string is given, method uses string itself as a template.
        When the argument tid is given, it retrieve template object by using tid
         and render it.
        """
        if path and string:
            raise ValueError( ("Arguments 'path', 'string' must not be set"
                               " at the same time") )


    def render(self, context, template = None , path = '', string = '', tid = ''):
        """
        A method to render template by using given template string, context.
        """
        pass


class MakoTemplateEngine(TemplateEngine):
    """
    A TemplateEngine class for Mako template.
    """

    ENGINE_NAME = 'mako'
    DEFAULT_EXTENSION = '.mak'

    def __init__(self, extension = DEFAULT_EXTENSION,
                 dirs = [], charset = 'utf-8'):
        """
        Initialization method
        """
        self.templdirs = [os.path.dirname(__file__)]
        if dirs:
            self.templdirs.extend(dirs)
        self._charset = charset
        du = False
        if self._charset.lower() != 'utf-8':
            du = True
        self.tlookup = TemplateLookup(directories = self.templdirs,
                                    disable_unicode = du,
                                    input_encoding = self._charset,
                                    output_encoding = self._charset)
        self.ext = extension


    def get_template(self, path = '', string = '', tid = ''):
        """
        A method to obtain template object, by using given path or string.
        When argment path is given, method produce template string via file.
        When string is given, method uses string itself as a template.
        """
        if path and string:
            raise ValueError( ("Arguments 'path', 'string' must not be set"
                               " at the same time") )
        if tid or path:
            if not tid: tid = path;
            t = self.get_template_cache(tid)
            if t: return t

        if path:
            if not os.path.splitext(path)[1]: path += self.ext;
            t = self.tlookup.get_template(path)
            self.set_template_cache(t, path)
            return t
        elif string:
            """
            du = False
            if self._charset.lower() != 'utf-8':
                du = True
            """
            t = Template(string, input_encoding = self._charset,
                                    output_encoding = self._charset)
            self.set_template_cache(t, tid)
            return t


    def render(self, context, template = None , path = '', string = '', tid = ''):
        """
        A method to render template by using given template string, context.
        """
        if (path or string or tid) and not template:
            template = self.get_template(path, string, tid)
        return template.render(**context)


# Now we make singleton like instance of TemplateHander()
#  so that we can use it from any places.

templatehandler = TemplateHandler()
templatehandler.add_engine(MakoTemplateEngine())

def mail(): pass;


