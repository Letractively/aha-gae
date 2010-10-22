## -*- coding: utf-8 -*-
#
# lazyloadingmodels.py
# The collection of classes, that load property lazily.
#
# Copyright 2010 Atsushi Shibata
#

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'


from google.appengine.ext import db

KEY_PREFIX = 'lazykey_'

class LazyPropertyBase(db.Model):
    """
    A base class of lazy property,
        which loads data only when the attribute accessed
    """
    parent_keyname = db.StringProperty(required = False, default = '')

    def get_data(self, key):
        """
        A method to obtain data itself.
        """
        if key:
            try:
                d = self.get(key)
                return d.data
            except db.datastore_errors.BadKeyError, e:
                pass
        return None

    def set_data(self, model, key, data):
        """
        A method to put data to the datastore.
        """
        d = None
        if key:
            try:
                d = self.get(key)
                d.data = data
            except db.datastore_errors.BadKeyError, e:
                pass
        if not d:
            d = self.__class__(data = data)
        try:
            key = model.key()
            d.parent_keyname = str(key)
        except db.NotSavedError, e:
            pass
        d.put()
        return str(d.key())

    def get_parent(self, key):
        """
        A method to obtain parent model.
        """
        d = self.get(key)
        if not d.parent_keyname:
            raise ValueError('Parent has not been set yet.')
        return db.get(d.parent_keyname)


class LazyLoadingMetaclass(db.PropertiedClass):
    """
    A metaclass which adds property(s) to store key information of
        lazily loading property.
    """

    def __new__(cls, name, bases, attrs):
        """
        A method to create new class dynamically
        """
        keys = attrs.keys()
        lazyprops = []
        for n in keys:
            if isinstance(attrs[n], LazyPropertyBase):
                # adding property for key of lazy property
                attrs[KEY_PREFIX+n] = db.StringProperty(required = False,
                                                         default = '')
                lazyprops.append(n)
        attrs['lazy_properties'] = lazyprops
        new_class = super(LazyLoadingMetaclass, cls).__new__(cls, name,
                                                              bases, attrs)
        return new_class


class LazyModelBase(db.Model):
    """
    A base class to hold lazy property.
    """
    __metaclass__ = LazyLoadingMetaclass


    def __getattribute__(self, key):
        """
        A method to set attribute.
        """
        attr = db.Model.__getattribute__(self, key)
        if isinstance(attr, LazyPropertyBase):
            ds_key = db.Model.__getattribute__(self, KEY_PREFIX+key)
            value = attr.get_data(ds_key)
            return value
        else:
            return attr

    def __setattr__(self, key, value):
        """
        A method to set attribute.
        """
        ds_key_id = KEY_PREFIX+key
        if hasattr(self, ds_key_id):
            attr = db.Model.__getattribute__(self, key)
            ds_key = db.Model.__getattribute__(self, KEY_PREFIX+key)
            origv = attr.get_data(ds_key)
            new_key = attr.set_data(self, ds_key, value)
            if not origv:
                db.Model.__setattr__(self, KEY_PREFIX+key, new_key)
        else:
            db.Model.__setattr__(self, key, value)




class LazyStringProperty(LazyPropertyBase):
    """
    A lazy property which store string data.
    """
    MODEL = db.StringProperty
    data = db.StringProperty(required = False)

'''
class LazyListProperty(LazyPropertyBase):
    """
    A lazy property which store list data.
    """
    MODEL = db.ListProperty
    data = db.ListProperty(required = False)
'''

class LazyStringListProperty(LazyPropertyBase):
    """
    A lazy property which store string list data.
    """
    MODEL = db.StringListProperty
    data = db.StringListProperty()

class LazyTextProperty(LazyPropertyBase):
    """
    A lazy property which store text data.
    """
    MODEL = db.TextProperty
    data = db.TextProperty(required = False)

class LazyBlobProperty(LazyPropertyBase):
    """
    A lazy property which store blob data.
    """
    MODEL = db.BlobProperty
    data = db.BlobProperty(required = False)

