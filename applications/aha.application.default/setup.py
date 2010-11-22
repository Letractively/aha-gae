from setuptools import setup, find_packages
import sys, os

version = '0.82b'

setup(name='aha.application.default',
      version=version,
      description="An default application for aha framework.",
      long_description="""\
A default appliction for aha framework. It has only simple controller and say 'aha :-)' .""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='web aha appengine web',
      author='Atsushi Shibata',
      author_email='shibata@webcore.co.jp',
      url='http://coreblog.org/aha',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      packages = [
        'application',
        'application.controller',
        'application.model',
        'application.template',
        'application.tests',
        'application.util',
      ],
      install_requires = [
          'aha',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
