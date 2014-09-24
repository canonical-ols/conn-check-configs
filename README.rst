conn-check-configs
==================

This is a set of Python modules and utilities for generating `conn-check <https://launchpad.net/conn-check>`_
config YAML from other sources, such as Django settings modules.


Supported sources
-----------------

 - Django settings modules


Usage
-----

Django
``````
You can export common settings from a Django application using the `conn-check-django` command line
utility, which takes the following arguments:

 - `-m`, `--settings-module`: the Python module for Django to import.
 - `-d`, `--database-name`: the database schema name if not set as `NAME` in the Django settings.

 Followed by a path to the generated YAML file, for example::

     $ conn-check-django -m myapp.settings /tmp/myapp-conncheck.yaml
     $ conn-check /tmp/myapp-conncheck.yaml

Building wheels
---------------

To allow for easier/more portable distribution of this tool you can build
conn-check-configs and all it's dependencies as `Python wheels <http://legacy.python.org/dev/peps/pep-0427/>`_::

    make clean-wheels
    make build-wheels

The `build-wheels` make target will build conn-check-configs and it's base dependencies.

By default all the wheels will be placed in `./wheels`.
