# -*- coding: utf-8 -*-

__author__  = 'Atsushi Shibata <shibata@webcore.co.jp>'
__docformat__ = 'plaintext'
__licence__ = 'BSD'


class Config:
    """ The singleton of configuration """

    class __impl:
        def __init__(self):
            self.template_dir = ''
            self.session_store = 'memcache'
            self.version = '0.3'
            self.app_name = ''

    __instance = None

    def __init__(self):
        if Config.__instance is None:
            Config.__instance = Config.__impl()

        self.__dict__['_Config__instance'] = Config.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)



