Installation - Advanced Options
===============================

Running conductor-api Under apache2 httpd and mod\_wsgi
-------------------------------------------------------

``conductor-api`` may be run as-is for development and test purposes.
When used in a production environment, it is recommended that
``conductor-api`` run under a multithreaded httpd service supporting
`WSGI <https://www.wikipedia.org/wiki/Web_Server_Gateway_Interface>`__,
tuned as appropriate.

Configuration instructions for **apache2 httpd** and **nginx** are
included herein. Respective package requirements are:

-  `apache2 <http://packages.ubuntu.com/focal/apache2>`__ and
   `libapache2-mod-wsgi <http://packages.ubuntu.com/focal/libapache2-mod-wsgi>`__
-  `nginx <http://packages.ubuntu.com/focal/nginx>`__ and
   `uwsgi <http://packages.ubuntu.com/focal/uwsgi>`__


Sample configuration files have been provided in the repository.

These instructions presume a ``conductor`` user exists. See the
**Service Scripts** section for details.

First, set up a few directories:

.. code:: bash

    $ sudo mkdir -p /var/www/conductor
    $ sudo mkdir /var/log/apache2/conductor

To install, place the Conductor `WSGI application
file </conductor/api/app.wsgi>`__ in ``/var/www/conductor``.

Set the owner/group of both directories/files to ``conductor``:

.. code:: bash

    $ sudo chown -R conductor:conductor /var/log/apache2/conductor /var/www/conductor

Next, place the Conductor `apache2 httpd site config
file </examples/apache2/conductor.conf>`__ in
``/etc/apache2/sites-available``.

Set the owner/group to ``root``:

.. code:: bash

    $ sudo chown -R root:root /etc/apache2/sites-available/conductor.conf

If Conductor was installed in a python virtual environment, append
``python-home=VENV`` to ``WSGIDaemonProcess``, where ``VENV`` is the
python virtual environment root directory.

**IMPORTANT**: Before proceeding, disable the ``conductor-api`` sysvinit
and upstart services, as the REST API will now be handled by apache2
httpd. Otherwise there will be a port conflict, and you will be sad.

Enable the Conductor site, ensure the configuration syntax is valid, and
gracefully restart apache2 httpd.

.. code:: bash

    $ sudo a2ensite conductor
    $ sudo apachectl -t
    Syntax OK
    $ sudo apachectl graceful

To disable the Conductor site, run ``sudo a2dissite conductor``, then
gracefully restart once again. Optionally, re-enable the
``conductor-api`` sysvinit and upstart services.

Running conductor-api Under nginx and uWSGI
-------------------------------------------

Sample configuration files have been provided in the repository.

These instructions presume a ``conductor`` user exists. See the
**Service Scripts** section for details.

To install, place the Conductor `nginx config
files </examples/nginx/>`__ and `WSGI application
file </conductor/api/app.wsgi>`__ in ``/etc/nginx`` (taking care to
backup any prior configuration files). It may be desirable to
incorporate Conductor's ``nginx.conf`` into the existing config.

Rename ``app.wsgi`` to ``conductor.wsgi``:

.. code:: bash

    $ cd /etc/nginx
    $ sudo mv app.wsgi conductor.wsgi

In ``nginx.conf``, set ``CONDUCTOR_API_FQDN`` to the server name.

**IMPORTANT**: Before proceeding, disable the ``conductor-api`` sysvinit
and upstart services, as the REST API will now be handled by nginx.
Otherwise there will be a port conflict, and you will be sad.

Restart nginx:

.. code:: bash

    $ sudo service nginx restart

Then, run ``conductor-api`` under nginx using uWSGI:

.. code:: bash

    $ sudo uwsgi -s /tmp/uwsgi.sock --chmod-socket=777 --wsgi-file /etc/nginx/conductor.wsgi --callable application --set port=8091

To use a python virtual environment, add ``--venv VENV`` to the
``uwsgi`` command, where ``VENV`` is the python virtual environment root
directory.

Networking
----------

All conductor services require line-of-sight access to all Music/ETCD
servers/ports.

The ``conductor-api`` service uses TCP port 8091.

Security
--------

``conductor-api`` is accessed via HTTP. SSL/TLS certificates and
AuthN/AuthZ (e.g., AAF) are supported at this time in kubernetes
environment.

Conductor makes use of plugins that act as gateways to *inventory
providers* and *service controllers*. At present, two plugins are
supported out-of-the-box: **A&AI** and **SDN-C**, respectively.

A&AI requires two-way SSL/TLS. Certificates must be registered and
whitelisted with A&AI. SDN-C uses HTTP Basic Authentication. Consult
with each respective service for official information on how to obtain
access.

Storage
-------

For a cloud environment in particular, it may be desirable to use a
separate block storage device (e.g., an OpenStack Cinder volume) for
logs, configuration, and other data persistence. In this way, it becomes
a trivial matter to replace the entire VM if necessary, followed by
reinstallation of the app and any supplemental configuration. Take this
into consideration when setting various Conductor config options.
