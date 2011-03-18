# -*- coding: utf-8 -*-

__all__ = ['get_router', 'get_fallback_router', 'rebuild_router']

from routes.mapper import Mapper

router = Mapper()
fallback_router = Mapper()

def get_router():
    """
    A function to obtain mapper object, which is used as a singleton.
    """
    #global router
    return router

def get_fallback_router():
    """
    A function to obtain mapper object, which is used as a singleton.
    """
    #global fallback_router
    return fallback_router

def rebuild_router():
    global router, fallback_router
    router = Mapper()
    fallback_router = Mapper()
