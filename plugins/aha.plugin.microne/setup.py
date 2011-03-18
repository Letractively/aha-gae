from setuptools import setup, find_packages
import sys, os

version = '0.6b'

setup(name='aha.plugin.microne',
      version=version,
      description="A microframework plugin for aha",
      long_description="""\
A plugin that makes aha framework working as microframework.""",
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
