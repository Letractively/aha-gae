# -*- coding: utf-8 -*-


import os

from lib.aha.wsgi.appinit import initConfig, initPlugins, run
from application.config import appConfig

def main():
    # setting up global config object
    config = initConfig(os.path.dirname(__file__))
    
    # setting application specific configurations
    appConfig()
    
    # initializing plugins
    initPlugins(os.path.dirname(__file__))

    # run wsgi server
    run(config.debug, config.useappstatus)

if __name__ == '__main__':
    main()
