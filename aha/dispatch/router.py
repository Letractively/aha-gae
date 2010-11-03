# -*- coding: utf-8 -*-

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
