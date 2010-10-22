# -*- coding: utf-8 -*-

##############################################################################
#
# translation.py
# Module defining bunch of function to be used for i18n transration
#
# Copyright (c) 2010 Webcore Corp. All Rights Reserved.
#
##############################################################################
""" translation.py - Module defining bunch of function to be used for i18n
                                                                 transration.

$Id: translation.py 629 2010-06-28 07:57:53Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'

import os
import gettext

__all__ = ['get_i18ndir', 'get_gettextobject', 'get_languages']


def get_i18ndir():
    """
    A function to obtain i18n directory
    """
    udir = os.path.dirname(os.path.split(__file__)[0])
    dir = os.path.join(udir, 'i18n')
    return dir

def get_gettextobject(dimain = 'aha', languages = None):
    """
    A function to obtain gettext object
    """
    dir = get_i18ndir()
    t = gettext.translation(domain = dimain,
                          languages = languages,
                          localedir = dir, fallback = True)
    return t

def get_languages(s):
    """
    A function to obtain language settings via Accept-Language header.
    """
    langs = [''.join(x.split(';')[:1]) for x in s]
    return langs

def main(): pass;

