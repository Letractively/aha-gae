"""
aha
======
aha is a web application framework specialized for Google App Engine.
It provides the finest way to propagate your 'aha !' into cruld :-).

"""

from setuptools import setup, find_packages
import sys, os

version = '0.81a'

setup(name='aha',
      version=version,
      description=("aha is a web application framework specialized for"
                   " Google App Engine."),
      long_description = __doc__,
      keywords= 'web appengine framework',
      author = 'Atsushi Shibata',
      author_email = 'shibata@webcore.co.jp',
      url = 'http://coreblog.org/aha',
      license = 'BSD',
      platforms = 'any',
      include_package_data = True,
      packages = [
        'aha',
        'aha.auth',
        'aha.controller',
        'aha.dispatch',
        'aha.i18n',
        'aha.model',
        'aha.modelcontroller',
        'aha.session',
        'aha.widget',
        'aha.wsgi',
      ],
      namespace_packages = [
        'aha',
        'aha.controller',
        'aha.widget',
        'aha.wsgi',
      ],
      zip_safe = True,
      install_requires = [
          # -*- Extra requirements: -*-
          'formencode',
          'mako',
          'baker',
          'werkzeug',
      ],
      classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      )
