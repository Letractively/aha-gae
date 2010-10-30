from setuptools import setup, find_packages
import sys, os

version = '0.91b'

setup(name='aha.plugin.twitteroauth',
      version=version,
      description="A twitter auth plugin for aha",
      long_description="""\
A plugin that ssupplies authentication support of twitter oauth.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='web aha twitter authentication plugin',
      author='Atsushi Shibata',
      author_email='shibata@webcore.co.jp',
      url='http://coreblog.org/aha',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires = [
          'aha',
      ],
      packages = [
        'twitteroauth',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
