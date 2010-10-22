# -*- coding: utf-8 -*-
#
# This code is derived from helper.py on App Engine Oil
#
# Copyright 2008 Lin-Chieh Shangkuan & Liang-Heng Chen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
""" helper module """

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'


import re
import new


# making helper functions
# don't remove following codes.

class helpers(object):
    @classmethod
    def extend(cls, name, func):
        """
        A method to extend helper function
        """
        if name not in cls.__dict__:
            setattr(cls, name, staticmethod(func))

def get_helpers():
    return helpers

hlps = dir()
for h in hlps:
    if not re.match('^__', h):
        method = eval('%s' % h)
        if callable(method):
            helpers.extend(h, method)

