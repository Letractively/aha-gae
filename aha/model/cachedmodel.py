## -*- coding: utf-8 -*-
#
# cachedmodels.py
# The collection of classes, that cache data in memcache.
#
# Copyright 2010 Atsushi Shibata
#


__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'


from google.appengine.ext import db
from google.appengine.api import memcache
import logging


__all__ = ('CachedModelBase', )
CM_NAMESPACE = 'cachedmodels'

try:
    QUERY_CACHE_EXPIRE = config.query_cache_expire
except:
    QUERY_CACHE_EXPIRE = 2*60*60 # 2 hours


class CachedModelBase(db.Model):
    """
    The base class of cached model, which caches result of query
        returns it when cached data is available.
    """
    EXPIRE = QUERY_CACHE_EXPIRE
    CACHE_PROPS = ()
    ADD_PROPS = ()
    __SAVED_PROPS__ = []

    def __init__(self, d = {}, cache = True, *args, **kws):
        for k in self.ADD_PROPS:
            setattr(self, k, '')
        go = True
        try:
            if self.__SAVED_PROPS__:
                go = False
        except:
            pass
        if go:
            if self.CACHE_PROPS:
                p = self.CACHE_PROPS
            else:
                p = self._properties.keys()
            if self.ADD_PROPS:
                p.extend(self.ADD_PROPS)
            self.__class__.__SAVED_PROPS__ = p
        if not d:
            self.cached = False
            db.Model.__init__(self, *args, **kws)
            if cache:
                try:
                    self.cache(dont_override_add_props = True)
                except db.NotSavedError:
                    pass
        else:
            self._dic = d
            for k in d:
                setattr(self, k, d[k])
            self.cached = True

    @classmethod
    def _get(cls, key):
        """
        A method to obtain data with key,
            using cached result as much as possible.
        """
        d = memcache.get(str(key), namespace = CM_NAMESPACE)
        return d

    def make_dic_from_data(self):
        """
        """
        d = {}
        for k in self.__SAVED_PROPS__:
            d[k] = getattr(self, k)
        d['_internal_key'] = self._internal_key
        return d

    def cache(self, dont_override_add_props = False):
        """
        A method to cache properties in the memcache
        """
        key = str(self.key())
        self._internal_key = str(key)
        od = self._get(key)
        if od:
            cd = self.make_dic_from_data()
            if dont_override_add_props:
                for k in self.ADD_PROPS:
                    cd[k] = od.get(k, None)
            od.update(cd)
        else:
            od = self.make_dic_from_data()
        memcache.set(str(key), od,
                     self.EXPIRE, namespace = CM_NAMESPACE)

    #
    # Emulating methods
    #

    def key(self, cache = True):
        """
        A method to obtain key from thedatastore
        """
        if hasattr(self, '_entity'):
            return db.Model.key(self)
        else:
            return self._internal_key

    def put(self, cache = True):
        """
        A method to put data to datastore, update cache
        """
        if hasattr(self, '_entity'):
            db.Model.put(self)
            if cache:
                self.cache()
        else:
            # try to get new instance from datastore, and put it.
            if hasattr(self, '_internal_key'):
                new = self.__class__.get(self._internal_key, force = True)
                for k in self._properties:
                    setattr(new, k, getattr(self, k))
                new.put(cache = cache)
                if cache:
                    new.cache()

    @classmethod
    def get(cls, key, force = False):
        """
        A method to obtain instance with key, from cache, or datastore.
        """
        if not force:
            d = cls._get(key)
            if d:
                ins = cls(d = d)
                ins._internal_key = key
                return ins
        ins = super(CachedModelBase, cls).get(key)
        ins.cache()
        ins.cached = False
        return ins

    '''
    def __getattribute__(self, key):
        """
        A method to obtain attributes.
             It tries to return values in cache as much as possible.
        """
        if hasattr(self, '_dic'):
            d = db.Model.__getattribute__(self, '_dic')
            if key in d:
                return d[key]
        return db.Model.__getattribute__(self, key)


    def __setattr__(self, key, value):
        """
        A method to put values in attributes.
             It tries to use values in cache as much as possible.
        """
        if hasattr(self, '_dic'):
            d = db.Model.__getattribute__(self, '_dic')
            if key in d:
                d[key] = value
        db.Model.__setattr__(self, key, value)
    '''

    @classmethod
    def all(cls):
        """
        A method to obtain alternative query object,
            that store result in memcache.
        """
        return CachedQuery(cls)

CQ_NAMESPACE = 'cachedquery'

class CachedQuery(object):
    """
    A query class that store result in memcache.
    """

    def __init__(self, cls):
        """
        A initialize method.
        """
        self.cls = cls
        self.query = db.Query(cls)
        self.filters = []

    def filter(self, op, value):
        """
        A method to proxy filter() method.
        It passes argument to the Query.filter() and
            store paramaters in a list.
        """
        self.query.filter(op, value)
        f = op+str(value)
        if f not in self.filters:
            self.filters.append(f)

    def order(self, property):
        """
        A method to proxy order() method.
        It passes argument to the Query.order() and
            store paramaters in a list.
        """
        self.query.order(property)
        if property not in self.filters:
            self.filters.append(property)

    def fetch(self, limit, offset = 0, force = False):
        """
        A method to proxy fetch() method.
        """
        done = False
        tmp_f = self.filters[:]
        tmp_f.sort()
        tmp_f.extend([('limit:%d' % limit), ('offset:%d' % offset)])
        str_f = str(self.cls)+''.join(tmp_f)
        if not force:
            idr = memcache.get(str_f, namespace = CQ_NAMESPACE)
            if idr:
                logging.debug('fetch %s is gotten via cache' % str_f)
                for i in idr.split(','):
                    i = self.cls.get(i)
                    yield i
                done = True
        if not done:
            r = list(self.query.fetch(limit, offset))
            ids = ','.join([str(x.key()) for x in r])
            memcache.set(str_f, ids, self.cls.EXPIRE, namespace = CQ_NAMESPACE)
            kl = memcache.get('keys', namespace = CQ_NAMESPACE)
            if not kl: kl = []
            if str_f not in kl:
                kl.append(str_f)
                kl = memcache.set('keys', kl,
                                self.cls.EXPIRE, namespace = CQ_NAMESPACE)

            for i in r:
                i = self.cls.get_by_id(i.key().id())
                yield i

    def count(self, limit, force = False):
        """
        A method to proxy count() method.
        """
        tmp_f = self.filters[:]
        tmp_f.sort()
        tmp_f.append('limit:%d' % limit)
        str_f = str(self.cls)+':count:'+''.join(tmp_f)
        if not force:
            c = memcache.get(str_f, namespace = CQ_NAMESPACE)
            if c:
                logging.debug('fetch %s is gotten via cache' % str_f)
                return c
        c = self.query.count(limit)
        memcache.set(str_f, ids, self.cls.EXPIRE, namespace = CQ_NAMESPACE)
        kl = memcache.get('keys', namespace = CQ_NAMESPACE)
        if not kl: kl = []
        if str_f not in kl:
            kl.append(str_f)
            kl = memcache.set('keys', kl,
                            self.cls.EXPIRE, namespace = CQ_NAMESPACE)

        return c


    def flush_cache(self, force = False):
        """
        A method to flush cache
        """
        tmp_f = self.filters[:]
        tmp_f.sort()
        str_f = str(self.cls)+''.join(tmp_f)
        kl = memcache.get('keys', namespace = CQ_NAMESPACE)
        logging.debug('clearing caches statt with %s' % str_f)
        if kl:
            for k in kl:
                if k.startswith(str_f):
                    logging.debug('cache %s is cleared' % k)
                    memcache.delete(k, namespace = CQ_NAMESPACE)

