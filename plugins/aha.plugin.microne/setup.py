from setuptools import setup, find_packages
import sys, os

version = '0.62b'

setup(name='aha.plugin.microne',
      version=version,
      description=("Yet another microframework"
                   " on the top of the full stack framework aha"),
      long_description="""\
A plugin that makes aha framework work as microframework.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='web aha plugin microframework',
      author='Atsushi Shibata',
      author_email='shibata@webcore.co.jp',
      url='http://coreblog.org/aha',
      license='BSD',
      packages = [
        'microne',
      ],
      include_package_data=True,
      zip_safe=False,
      install_requires = [
          'aha',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
