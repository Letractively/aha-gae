from setuptools import setup, find_packages
import sys, os

version = '0.8a'

setup(name='aha',
      version=version,
      description="aha is a weweb application framework specialized for Google App Engine.",
      long_description="""\
aha is a web application framework specialized for Google App Engine. It provides the finest way to propagate your 'aha !' into cruld :-).""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='web appengine framework',
      author='Atsushi Shibata',
      author_email='shibata@webcore.co.jp',
      url='http://coreblog.org/aha',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          'formencode',
          'mako',
          'baker',
          'werkzeug',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
