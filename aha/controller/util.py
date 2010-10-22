## -*- coding: utf-8 -*-

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'

import logging
from google.appengine.api import mail


def get_controller_class(cnt, plugin = ''):
    """
    A function to obtain controller associated to given content object.
    When the argument plugin given,
        the controller will be read via given plugin directory.
    """
    try:
        # At first, trying to import a controller class via controller dir.
        exec('from application.controller import %s' % cnt.lower()) in globals()
        ctrl_clz = eval('%s.%sController' % (cnt.lower(), cnt.capitalize()) )
        return ctrl_clz
    except ImportError:
        # In case ImportError occurs, tying to import one via plugin dir.
        if not plugin: plugin = cnt;
        exec('from plugin.%s import %s' % (plugin.lower(), cnt.lower()))\
                                                                in globals()
        ctrl_clz = eval('%s.%sController' % (cnt.lower(), cnt.capitalize()) )
        return ctrl_clz

def get_current_user():
    """
    A function to obtain current login user.
    """
    from coregae import Config
    config = Config()
    return config.auth_obj().get_user(None)


