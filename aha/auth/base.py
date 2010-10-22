# -*- coding: utf-8 -*-

##############################################################################
#
# base.py
# A module to provide base class of authentication plugin.
#
# Copyright (c) 2010 Webcore Corp. All Rights Reserved.
#
##############################################################################
""" appengine.py - A module to provide base class of authentication plugin.

$Id: appengine.py 638 2010-08-10 04:05:57Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'



class BaseAuth(object):
    """
    A base class of authentication plugin
    """

    def auth(self, ins, *param, **kws):
        """
        A method to perform authentication, or
            to check if the authentication has been performed.
        It returns true on success, false on failure.
        """
        raise NotImplementedError('You must override auth() method')


    def auth_redirect(self, ins, *param, **kws):
        """
        A method to perform redirection
            when the authentication fails, user doesn't have privileges, etc.
        """
        raise NotImplementedError('You must override auth_redirect() method')


    def get_user(self, ins, *param, **kws):
        """
        A method to return current login user.
        It returns user dict if the user is logging in,
            None if doesn't.
        A returned dictionary should have following data
                   {'type':'type of authentication'
                    'nickname':'a nickname',
                    'email':'an email',
                    'userid':'a userid',
                    'realname':'a realname',
                    }
        """
        raise NotImplementedError('You must override do_auth() method')


    def logout(self, ins, *param, **kws):
        """
        A method to perform logout action
        """
        raise NotImplementedError('You must override logout() method')


def main(): pass;

