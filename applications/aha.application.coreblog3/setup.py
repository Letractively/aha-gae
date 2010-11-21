"""
coreblog3
==================

coreblog3 is a blog hosting software developed at the top of Aha framework, which is a framework made specially for Google App Engine.
Here are some quick instruction to get started with coreblog3 and make your own blog site on Google App Engine. For more details, visit our website :-).

  http://coreblog.org/coreblog3

Or you can get source code from the repository.

  http://code.google.com/p/aha-gae/

What is coreblog3
-----------------------
coreblog3 is blog hosting software. You can make your own blog site on Google App Engine. coreblog3 also has features of CMS. You can make not only blog site, but put page, folder, file and so on.

Quickstart
-----------------------
To start making your own blog site, just download zipped project file.

  http://aha-gae.googlecode.com/files/project.zip

After extracting the archive, move to the folder you'll get and just type

  python bootstrap.py

Next step is to modify the setting file named 'buildout.cfg'. Find a section starting with '[app_lib]'. You will see 'aha.application.default'. Fix this line to 'aha.application.coreblog3' .

After that, launch buildout command. Make sure that you have internet connection, because it will download libraries via the internet.

  bin/buildout

Before launching application, fix app.yaml file refering 'app.yaml.sample' in application directory. Just move it to app directory and remove '.sample' from the filename. It works fine in most cases.
And fix config.py located in application file. At least you have to add 'config.initial_user' and 'config.site_root'.

Finnaly, launch app in local development environment. All the stuff required to run application are under app directory. So you may give 'app' argument to the command.

  bin/dev_appserver app

Now it's time to visit admin form. Type http://127.0.0.1:8080/_edit_site_data to edit your site data.

Enjoy :-).

"""

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
      url='http://coreblog.org/coreblog3',
      license='BSD',
      packages = [
        'application',
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
