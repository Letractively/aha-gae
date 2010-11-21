aha
==================
aha is a framework made specially for Google App Engine.Here are some quick instruction to get started with it. For more details, visit our website :-).

  http://coreblog.org/aha

Or you can get source code from the repository.

  http://code.google.com/p/aha-gae/

What is aha
-----------------------
aha is a web application framework. It has been developed hoping it will be the best way to propagate your 'aha!' into the cloud :-).

aha has following features.

- rails like routing
- class based model
- mako template ( for speed ;-) )
- db / query cache
- form, field generation
- plugins
- development with buildout
- easy to make admin/crud interface
- interactive debug interface using werkzeug
- appstats integration
- easy to use decorator based authentication
- plagable authentication mecanizm
- i18n


Quickstart
-----------------------
To start developing with aha, download bootstrap from url bellow.

  http://aha-gae.googlecode.com/files/project.zip

After extracting the archive, move to the folder you'll get and just type

  python bootstrap.py

Next step is to launch buildout command. Make sure that you have internet connection, because it will download libraries via the internet.

  bin/buildout

Then, launch app in local development environment. All the stuff required to run application are under app directory. So you may give 'app' argument to the command.

  bin/dev_appserver app

Now it's time to visit your fiest aha application's screen :-). Type http://127.0.0.1:8080/ to see initial page of aha's default application.

