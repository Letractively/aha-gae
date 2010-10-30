# -*- coding: utf-8 -*-

##############################################################################
#
# makocontroller.py
# Classes handing mako as a template engine.
#
# Copyright (c) 2010 Webcore Corp. All Rights Reserved.
#
##############################################################################
""" makocontroller.py - Classes handing mako as a template engine.

$Id: makocontroller.py 644 2010-08-10 04:15:42Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'

import os
import re
from datetime import datetime
from hashlib import md5
from copy import copy
import logging

import aha
import helper

from aha.controller.basecontroller import BaseController

from mako import template, exceptions
from mako.lookup import TemplateLookup

tlookup = None
charset = 'utf-8'

def get_lookup(du = False):
    """
    A function to obtain global template lookup
    """
    global tlookup
    if not tlookup:
        SS = os.environ.get('SERVER_SOFTWARE','')
        config = aha.Config()
        tpdirs = config.template_dirs
        if not SS.lower().startswith("dev"):
            tlookup = TemplateLookup(directories = tpdirs, 
                 disable_unicode = du,
                 input_encoding = charset,
                 output_encoding = charset,
                 filesystem_checks = False, cache_type = 'memcached',
                 cache_dir = ".", cache_url = 'memcached://')
        else:
            tlookup = TemplateLookup(directories = tpdirs, 
                 disable_unicode = du,
                 input_encoding = charset,
                 output_encoding = charset)
        logging.debug('new TemplateLookup is loaded.')


class MakoTemplateController(BaseController):

    _template_ext = '.html'
    _charset = 'utf-8'

    def __init__(self, hnd, params = {}):
        """
        Initialize method
        """

        super(MakoTemplateController, self).__init__(hnd, params)
        self._config = aha.Config()
        self._tpldirs = self._config.template_dirs
        du = False
        if self._charset.lower() != 'utf-8': du = True
        get_lookup(du)

    def render(self, *html, **opt):
        hdrs = {}

        content_type = 'text/html; charset = %s' % self._charset
        
        if html:
            content = (''.join(html)).decode('utf-8')
            
        elif opt:
            # if the expires header is set
            content, content_path, content_type = self.parse_opt(**opt)
        else:
            raise Exception('Render type error')

        context = self.__dict__
        if isinstance(opt.get('values'), dict):
            context.update(opt.get('values'))
        # render content as a template
        if content_path:
            tmpl = tlookup.get_template(content_path)
        elif content:
            tmpl = template.Template(content)
            #context['path'] = path

        try:
            result = tmpl.render(**context)
        except:
            r = exceptions.html_error_template().render()
            raise Exception(r)


        hdrs['Content-Type'] = content_type
        hdrs.update(opt.get('hdr', {}))

        # pass the output to the response object
        r = self.response
        if hdrs:
            for k, v in hdrs.items():
                r.headers[k] = v
        r.out.write(result)

        self.has_rendered = True


def patch_beaker():
    import sys
    import google.appengine.api.memcache
    sys.modules['memcache'] = google.appengine.api.memcache
    import beaker.ext.memcached
    from beaker import synchronization
    beaker.ext.memcached.verify_directory = lambda x: None
    beaker.ext.memcached.MemcachedNamespaceManager.get_creation_lock = \
                            lambda x, y: synchronization.null_synchronizer()

def mako_patch():
    from mako.template import Lexer, codegen, types
    from google.appengine.api import memcache
    cvid = os.environ.get('CURRENT_VERSION_ID','')
    
    def _compile_text(template, text, filename):
        identifier = template.module_id
        no_cache = identifier.startswith('memory:') or \
            os.environ.get('SERVER_SOFTWARE','').lower().startswith("dev")
        #no_cache = identifier.startswith('memory:')
        cachekey = 'makosource:%s:%s' % (str(cvid), str(identifier))
        if not no_cache:
            source = memcache.get(cachekey)
        if no_cache or source is None:
            lexer = Lexer(text, filename, 
                          disable_unicode = template.disable_unicode, 
                          input_encoding = template.input_encoding,
                          preprocessor = template.preprocessor)
            node = lexer.parse()
            source = codegen.compile(node, template.uri, filename,
                             default_filters = template.default_filters, 
                             buffer_filters = template.buffer_filters, 
                             imports = template.imports)
            if not no_cache:
                memcache.set(cachekey, source)
                logging.debug("Store mako template: "+cachekey)
        cid = identifier
        if isinstance(cid, unicode):
            cid = cid.encode()
        module = types.ModuleType(cid)
        code = compile(source, cid, 'exec')
        exec code in module.__dict__, module.__dict__
        return (source, module) 
    
    template._compile_text = _compile_text

try:
    if not os.environ.get('SERVER_SOFTWARE','').lower().startswith("dev"):
        patch_beaker()
        mako_patch()
except:
    pass

def main(): pass;

