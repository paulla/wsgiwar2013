wsgi2013
========

Running the project for development
-----------------------------------

- you should have couchdb installed and running

- clone the repository. E.g., if you do not fork : ``git clone https://github.com/paulla/wsgiwar2013.git``

- run ``python bootstrap.py`` in the clone directory

- run ``bin/buildout``

- to launch the app, run ``bin/pserve development.ini --reload``

- you should be able to open the app on your browser using http://127.0.0.1:6543


Developer lifecycle
-------------------

- when pulling new commits or if you change it yourself, you may need to run ``bin/buildout -n`` if file ``__init__.py`` changes

- when modifying a file, you should kill the running pserve and launch it again with ``bin/pserve development.ini --reload``


