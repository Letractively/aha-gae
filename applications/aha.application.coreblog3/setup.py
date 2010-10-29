from setuptools import setup, find_packages
import sys, os

version = '0.6a'

setup(name='aha.application.coreblog3',
      version=version,
      description="A blog application workins on Google App Engine",
      long_description="""\
A blog application works on Google App Engine.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='web blog appengine cms',
      author='Atsushi Shibata',
      author_email='shibata@webcore.co.jp',
      url='http://coreblog.org/',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      packages = [
        'application',
      ],
      install_requires = [
          'aha',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
