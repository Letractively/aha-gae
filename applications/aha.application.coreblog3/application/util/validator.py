# -*- coding: utf-8 -*-

""" additional valudators """
import re
import formencode
FancyValidator = formencode.api.FancyValidator

class ListValidator(FancyValidator):
    """
    A validator that converts CR separated value to list.
    """
    if_empty = []

    def __init__(self, type = str, regex = '', delimiter = '\n', *args, **kw):
        FancyValidator.__init__(self, *args, **kw)
        self.type, self.regex, self.delimiter = type, regex, delimiter


    def _to_python(self, value, state):
        values = []
        for n, i in enumerate(
                [x.strip() for x in value.split(self.delimiter)]):
            try:
                v = self.type(i)
                values.append(v)
            except ValueError:
                m = 'Item No. %s must be type %s, got %s'
                m = m%(n, str(self.type), v, value, state)
                raise formencode.Invalid(m)
        return values


class UserIDValidator(FancyValidator):
    """
    A validator that confirm if the given user id is unique.
    """
    if_empty = []

    def _to_python(self, value, state):
        from model.users import User
        q = User.all()
        q.filter('userid =', value)
        if list(q.fetch(100)):
            m = 'User ID %s already exists' % value
            raise formencode.Invalid(m, value, state)
        return value
