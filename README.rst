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

 - ``-m``, ``--settings-module``: the Python module for Django to import.
 - ``-d``, ``--database-name``: the database schema name if not set as `NAME` in the Django settings.
 - ``--statsd-send``: Optional string to send with statsd checks (defaults to a conn-check specific metric).
 - ``--statsd-expect``: Optional response string to expect from a statsd check.
 - ``-f``, ``output-file``: Optionally output to a file rather than ``STDOUT``.

 Followed by a path to the generated YAML file, for example::

     $ conn-check-django -m myapp.settings -f /tmp/myapp-conncheck.yaml
     $ conn-check /tmp/myapp-conncheck.yaml


Extending configuration generation
----------------------------------

You may want to extend the generated checks with custom (or unsupported) settings,
this can be done by creating your own script and importing all the functions/variables
from the relevant `conn_check_configs` submodule (e.g. `django`), and then extending
the ``EXTRA_CHECK_MAKERS`` list with your own check making functions, which must take
2 arguments: the Django settings module and the options from the CLI (usually a ``argparse.Namespace`` instance).


Building wheels
---------------

To allow for easier/more portable distribution of this tool you can build
conn-check-configs and all it's dependencies as `Python wheels <http://legacy.python.org/dev/peps/pep-0427/>`_::

    make clean-wheels
    make build-wheels

The `build-wheels` make target will build conn-check-configs and it's base dependencies.

By default all the wheels will be placed in `./wheels`.
