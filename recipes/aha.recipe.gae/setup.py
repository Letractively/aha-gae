from setuptools import setup, find_packages
import sys, os

version = '0.71b'

setup(name='aha.recipe.gae',
      version=version,
      description="a buildout recipe for web application framework aha",
      long_description="""\
a buildout recipe for web application framework aha""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='buildout recipe appengine',
      author='Atsushi Shibata',
      author_email='shibata@webcore.co.jp',
      url='http://coreblog.org/ats',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'appfy.recipe.gae'
      ],
    entry_points={
        'zc.buildout': [
            'app_lib = aha.recipe.gae.app_lib:Recipe',
        ],
      }
      )
