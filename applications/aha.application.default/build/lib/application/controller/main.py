# -*- coding: utf-8 -*-
#
# main.py
# The main controller for sample application.
#
# Copyright 2010 Atsushi Shibata
#

"""
The main controller for sample application.

$Id: main.py 650 2010-08-16 07:45:11Z ats $
"""

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'

from aha.controller.basecontroller import BaseController
from aha.controller.decorator import expose

class MainController(BaseController):
    """
    The Main Controller.
    """

    @expose
    def index(self):
        """
        A method to say 'Aha :-).'.
        """
        self.render('Aha :-).')
