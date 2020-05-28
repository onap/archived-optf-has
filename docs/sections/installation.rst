Python/Linux Distribution Notes
===============================

*Updated: 10 Nov 2017 23:30 GMT*

This document exists to help bridge the gap between the Conductor python
package and any downstream distribution. The steps outlined herein may
be taken into consideration when creating an AT&T SWM package,
Ubuntu/Debian package, Chef cookbook, or Ansible playbook.

Components
----------

Conductor consists of five services that work together:

-  **``conductor-api``**: An HTTP REST API
-  **``conductor-controller``**: Validation, translation, and
   status/results
-  **``conductor-data``**: Inventory provider and service controller
   gateway
-  **``conductor-solver``**: Processing and solution calculation
-  **``conductor-reservation``**: Reserves the suggested solution solved
   by Solver component.

Workflow
--------

-  Deployment **plans** are created, viewed, and deleted via
   ``conductor-api`` and its `REST API <doc/api/README.md>`__.
-  Included within each ``conductor-api`` plan request is a `Homing
   Template <doc/template/README.md>`__.
-  Homing Templates describe a set of inventory demands and constraints
   to be solved against.
-  ``conductor-api`` hands off all API requests to
   ``conductor-controller`` for handling.
-  All deployment plans are assigned a unique identifier (UUID-4), which
   can be used to check for solution status asynchronously. (Conductor
   does not support callbacks at this time.)
-  ``conductor-controller`` ensures templates are well-formed and valid.
   Errors and remediation are made visible through ``conductor-api``.
   When running in debug mode, the API will also include a python
   traceback in the response body, if available.
-  ``conductor-controller`` uses ``conductor-data`` to resolve demands
   against a particular **inventory provider** (e.g., A&AI).
-  ``conductor-controller`` translates the template into a format
   suitable for solving.
-  As each template is translated, ``conductor-solver`` begins working
   on it.
-  ``conductor-solver`` uses ``conductor-data`` to resolve constraints
   against a particular **service controller** (e.g., SDN-C).
-  ``conductor-solver`` determines the most suitable inventory to
   recommend.
-  ``conductor-reservation`` attempts to reserve the solved solution in
   SDN-GC

**NOTE**: There is no Command Line Interface or Python API Library at
this time.

Pre-Flight and Pre-Installation Considerations
----------------------------------------------

AT&T Application Identifiers and Roles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  App/Tool Name: ECOMP Conductor
-  MOTS Application ID: 26213
-  MechID: m04308
-  ECOMP Feature ID: F13704
-  PMT: 461306
-  UAM Role Name: Conductor Production Support
-  UAM Role id: 0000025248

Root
~~~~

Be aware that some commands may require ``sudo``, depending on the
account being used to perform the installation.

Proxy
~~~~~

If line-of-sight to internet-facing repositories is permitted and
available, set the following shell environment variables if AT&T proxy
services are required:

.. code:: bash

    $ export http_proxy="http://one.proxy.att.com:8080/"
    $ export https_proxy="http://one.proxy.att.com:8080/"

Requirements
~~~~~~~~~~~~

Conductor is officially supported on `Ubuntu 14.04 LTS (Trusty
Tahr) <http://releases.ubuntu.com/14.04/>`__, though it should also work
on newer releases.

Ensure the following Ubuntu packages are present, as they may not be
included by default:

-  `libffi-dev <http://packages.ubuntu.com/trusty/libffi-dev>`__
-  `postgresql-server-dev-9.3 <http://packages.ubuntu.com/trusty/postgresql-server-dev-9.3>`__
-  `python2.7 <http://packages.ubuntu.com/trusty/python2.7>`__

``conductor-api`` may be run as-is for development and test purposes.
When used in a production environment, it is recommended that
``conductor-api`` run under a multithreaded httpd service supporting
`WSGI <https://www.wikipedia.org/wiki/Web_Server_Gateway_Interface>`__,
tuned as appropriate.

Configuration instructions for **apache2 httpd** and **nginx** are
included herein. Respective package requirements are:

-  `apache2 <http://packages.ubuntu.com/trusty/apache2>`__ and
   `libapache2-mod-wsgi <http://packages.ubuntu.com/trusty/libapache2-mod-wsgi>`__
-  `nginx <http://packages.ubuntu.com/trusty/nginx>`__ and
   `uwsgi <http://packages.ubuntu.com/trusty/uwsgi>`__

All Conductor services use AT&T `Music <https://github.com/att/music>`__
for data storage/persistence and/or as a RPC transport mechanism.
Consult the `Music Local Installation
Guide <https://github.com/att/music/blob/master/README.md>`__ for
installation/configuration steps.

Networking
~~~~~~~~~~

All conductor services require line-of-sight access to all Music
servers/ports.

The ``conductor-api`` service uses TCP port 8091.

Security
~~~~~~~~

``conductor-api`` is accessed via HTTP. SSL/TLS certificates and
AuthN/AuthZ (e.g., AAF) are not supported at this time.

Conductor makes use of plugins that act as gateways to *inventory
providers* and *service controllers*. At present, two plugins are
supported out-of-the-box: **A&AI** and **SDN-C**, respectively.

A&AI requires two-way SSL/TLS. Certificates must be registered and
whitelisted with A&AI. SDN-C uses HTTP Basic Authentication. Consult
with each respective service for official information on how to obtain
access.

Storage
~~~~~~~

For a cloud environment in particular, it may be desirable to use a
separate block storage device (e.g., an OpenStack Cinder volume) for
logs, configuration, and other data persistence. In this way, it becomes
a trivial matter to replace the entire VM if necessary, followed by
reinstallation of the app and any supplemental configuration. Take this
into consideration when setting various Conductor config options.

Python Virtual Environments
~~~~~~~~~~~~~~~~~~~~~~~~~~~

At present, Conductor installation is only supported at the (upstream)
python package level and not the (downstream) Ubuntu distribution or SWM
package levels.

To mitigate/eliminate the risk of introducing conflicts with other
python applications or Ubuntu/SWM package dependencies, consider
installing Conductor in a `python virtual
environment <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`__
(or *venv* for short).

Example venv-aware WSGI app configurations, sysvinit scripts, and
upstart scripts can be found in the Conductor repository under
`examples </examples/>`__.

Python Package Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Conductor is installed using the python ``pip`` command. ``pip`` uses a
python project's `requirements manifest </requirements.txt>`__ to
install all python module dependencies.

**NOTE**: When line-of-sight access to a PyPI-compatible package index
is not available, advance installation of Conductor's python package
dependencies is required *before* installation.

Other Production Environment Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TBD. ``:)``

Over time, considerations may include services such as:

-  AAF
-  AppMetrics
-  Introscope
-  Nagios
-  Splunk
-  UAM

Installation and Configuration
------------------------------

**IMPORTANT**: Perform the steps in this section after *optionally*
configuring and activating a python virtual environment.

Installing From a PyPI Repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In ONAP, the ``conductor`` package can be found on \`\`\`\`.

Installation is via the ``pip`` command. Here is an example ``pip.conf``
file that uses both the internet and intranet-facing PyPI repositories:

.. code:: ini

    [global]
    index = https://pypi.python.org/pypi
    index-url = https://pypi.python.org/simple
    extra-index-url = 
    trusted-host = 

Once the configuration is in place, installation is simple:

.. code:: bash

    $ pip install --no-cache-dir of-has

To upgrade or downgrade, simply re-run ``pip install --no-cache-dir`` using the
appropriate ``pip`` command line options.

**NOTE**: Be sure proxy settings are in place if they're required to
access ``pypi.python.org``.

Installing From Source
~~~~~~~~~~~~~~~~~~~~~~

Conductor source in ONAP is maintained in
https://gerrit.onap.org/r/optf/has.

Clone the git repository, and then install from within the ``conductor``
directory:

.. code:: bash

    $ git clone --depth 1 https://gerrit.onap.org/r/optf/has
    Cloning into 'conductor'...
    remote: Counting objects: 2291, done.
    remote: Compressing objects:  88% (1918/2179)   
    remote: Compressing objects: 100% (2179/2179), done.
    remote: Total 2291 (delta 1422), reused 0 (delta 0)
    Receiving objects: 100% (2291/2291), 477.59 KiB | 0 bytes/s, done.
    Resolving deltas: 100% (1422/1422), done.
    $ cd conductor
    $ pip install --no-cache-dir .

The latest source can be pulled from ONAP at any time and reinstalled:

.. code:: bash

    $ git pull
    $ pip install --no-cache-dir .

Verifying Installation
~~~~~~~~~~~~~~~~~~~~~~

Each of the five Conductor services may be invoked with the ``--help``
option:

.. code:: bash

    $ conductor-api -- --help
    $ conductor-controller --help
    $ conductor-data --help
    $ conductor-solver --help
    $ conductor-reservation --help

**NOTE**: The ``conductor-api`` command is deliberate. ``--`` is used as
as separator between the arguments used to start the WSGI server and the
arguments passed to the WSGI application.

Post-Flight and Post-Installation Considerations
------------------------------------------------

User and Group
~~~~~~~~~~~~~~

It's good practice to create an unprivileged account (e.g., a user/group
named ``conductor``) and run all Conductor services as that user:

.. code:: bash

    $ sudo addgroup --system conductor 
    $ sudo adduser --system --home /var/lib/conductor --ingroup conductor --no-create-home --shell /bin/false conductor

SSL/TLS Certificates
~~~~~~~~~~~~~~~~~~~~

The A&AI Inventory Provider Plugin requiries two-way SSL/TLS. After
provisioning a certificate per A&AI guidelines, it will be necessary to
securely install the certificate, key, and certificate authority bundle.

When running conductor services as ``conductor:conductor``
(recommended), consider co-locating all of these files under the
configuration directory. For example, when using ``/etc/conductor``:

.. code:: bash

    $ # Certificate files (crt extension, 644 permissions)
    $ sudo mkdir /etc/conductor/ssl/certs
    $ # Private Certificate Key files (key extension, 640 permissions)
    $ sudo mkdir /etc/conductor/ssl/private
    $ # Certificate Authority (CA) Bundles (crt extension, 644 permissions)
    $ sudo mkdir /etc/conductor/ssl/ca-certificates
    $ # Add files to newly created directories, then set ownership
    $ sudo chmod -R conductor:conductor /etc/conductor/ssl

For a hypothetical domain name ``imacculate.client.research.att.com``,
example filenames could be as follows:

.. code:: bash

    $ find ssl -type f -printf '%M %u:%g %f\n'
    -rw-r----- conductor:conductor imacculate.client.research.att.com.key
    -rw-r--r-- conductor:conductor Symantec_Class_3_Secure_Server_CA.crt
    -rw-r--r-- conductor:conductor imacculate.client.research.att.com.crt

When running conductor services as ``root``, consider these existing
Ubuntu filesystem locations for SSL/TLS files:

**Certificate** files (``crt`` extension) are typically stored in
``/etc/ssl/certs`` with ``root:root`` ownership and 644 permissions.

**Private Certificate Key** files (``key`` extension) are typically
stored in ``/etc/ssl/private`` with ``root:root`` ownership and 640
permissions.

**Certificate Authority (CA) Bundles** (``crt`` extension) are typically
stored in ``/usr/share/ca-certificates/conductor`` with ``root:root``
ownership, and 644 permissions. These Bundle files are then symlinked
within ``/etc/ssl/certs`` using equivalent filenames, a ``pem``
extension, and ``root:root`` ownership.

**NOTE**: LUKS (Linux Unified Key Setup) is not supported by Conductor
at this time.

Configuration
~~~~~~~~~~~~~

Configuration files are located in ``etc/conductor`` relative to the
python environment Conductor is installed in.

To generate a sample configuration file, change to the directory just
above where ``etc/conductor`` is located (e.g., ``/`` for the default
environment, or the virtual environment root directory). Then:

.. code:: bash

    $ oslo-config-generator --config-file=etc/conductor/conductor-config-generator.conf

This will generate ``etc/conductor/conductor.conf.sample``.

Because the configuration directory and files will include credentials,
consider removing world permissions:

.. code:: bash

    $ find etc/conductor -type f -exec chmod 640 {} +
    $ find etc/conductor -type d -exec chmod 750 {} +

The sample config may then be copied and edited. Be sure to backup any
previous ``conductor.conf`` if necessary.

.. code:: bash

    $ cd etc/conductor
    $ cp -p conductor.conf.sample conductor.conf

``conductor.conf`` is fully annotated with descriptions of all options.
Defaults are included, with all options commented out. Conductor will
use defaults even if an option is not present in the file. To change an
option, simply uncomment it and edit its value.

With the exception of the ``DEFAULT`` section, it's best to restart the
Conductor services after making any config changes. In some cases, only
one particular service actually needs to be restarted. When in doubt,
however, it's best to restart all of them.

A few options in particular warrant special attention:

::

    [DEFAULT]

    # If set to true, the logging level will be set to DEBUG instead of the default
    # INFO level. (boolean value)
    # Note: This option can be changed without restarting.
    #debug = false

For more verbose logging across all Conductor services, set ``debug`` to
true.

::

    [aai]
                        
    # Base URL for A&AI, up to and not including the version, and without a
    # trailing slash. (string value)
    #server_url = https://controller:8443/aai

    # SSL/TLS certificate file in pem format. This certificate must be registered
    # with the A&AI endpoint. (string value)
    #certificate_file = certificate.pem

    # Private Certificate Key file in pem format. (string value)
    #certificate_key_file = certificate_key.pem

    # Certificate Authority Bundle file in pem format. Must contain the appropriate
    # trust chain for the Certificate file. (string value)
    #certificate_authority_bundle_file = certificate_authority_bundle.pem

Set ``server_url`` to the A&AI server URL, to but not including the
version, omitting any trailing slash. Conductor supports A&AI API v9 at
a minimum.

Set the ``certificate`` prefixed keys to the appropriate SSL/TLS-related
files.

**IMPORTANT**: The A&AI server may have a mismatched host/domain name
and SSL/TLS certificate. In such cases, certificate verification will
fail. To mitigate this, ``certificate_authority_bundle_file`` may be set
to an empty value. While Conductor normally requires a CA Bundle
(otherwise why bother using SSL/TLS), this requirement has been
temporarily relaxed so that development and testing may continue.

::

    [messaging_server]

    # Log debug messages. Default value is False. (boolean value)
    #debug = false

When the ``DEFAULT`` section's ``debug`` option is ``true``, set this
section's ``debug`` option to ``true`` to enable detailed Conductor-side
RPC-over-Music debug messages.

Be aware, it is voluminous. "You have been warned." ``:)``

::

    [music_api]

    # List of hostnames (round-robin access) (list value)
    #hostnames = localhost

    # Log debug messages. Default value is False. (boolean value)
    #debug = false

Set ``hostnames`` to match wherever the Music REST API is being hosted
(wherever Apache Tomcat and ``MUSIC.war`` are located).

When the ``DEFAULT`` section's ``debug`` option is ``true``, set this
section's ``debug`` option to ``true`` to enable detailed Conductor-side
MUSIC API debug messages.

The previous comment around the volume of log lines applies even more so
here. (Srsly. We're not kidding.)

**IMPORTANT**: Conductor does not presently use Music's atomic
consistency features due to concern around lock creation/acquisition.
Instead, Conductor uses eventual consistency. For this reason,
consistency issues may occur when using Music in a multi-server, High
Availability configuration.

::

    [sdnc]

    # Base URL for SDN-C. (string value)
    #server_url = https://controller:8443/restconf

    # Basic Authentication Username (string value)
    #username = <None>

    # Basic Authentication Password (string value)
    #password = <None>

Set ``server_url`` to the SDN-C server URL, omitting any trailing slash.

Set ``username`` and ``password`` to the appropriate values as directed
by SDN-C.

Running for the First Time
~~~~~~~~~~~~~~~~~~~~~~~~~~

Each Conductor component may be run interactively. In this case, the
user does not necessarily matter.

When running interactively, it is suggested to run each command in a
separate terminal session and in the following order:

.. code:: bash

    conductor-data --config-file=/etc/conductor/conductor.conf
    conductor-controller --config-file=/etc/conductor/conductor.conf
    conductor-solver --config-file=/etc/conductor/conductor.conf
    conductor-reservation --config-file=/etc/conductor/conductor.conf
    conductor-api --port=8091 -- --config-file=/etc/conductor/conductor.conf

Optionally, use an application like
`screen <http://packages.ubuntu.com/trusty/screen>`__ to nest all five
terminal sessions within one detachable session. (This is also the same
package used by
`DevStack <https://docs.openstack.org/developer/devstack/>`__.)

To verify that ``conductor-api`` can be reached, browse to
``http://HOST:8091/``, where HOST is the hostname ``conductor-api`` is
running on. No AuthN/AuthZ is required at this time. Depending on
network considerations, it may be necessary to use a command like
``wget`` instead of a desktop browser.

The response should look similar to:

.. code:: json

    {
      "versions": {
        "values": [
          {
            "status": "development",
            "updated": "2016-11-01T00:00:00Z",
            "media-types": [
              {
                "base": "application/json",
                "type": "application/vnd.ecomp.homing-v1+json"
              }
            ],
            "id": "v1",
            "links": [
              {
                "href": "http://127.0.0.1:8091/v1",
                "rel": "self"
              },
              {
                "href": "http://conductor.research.att.com/",
                "type": "text/html",
                "rel": "describedby"
              }
            ]
          }
        ]
      }
    }

Sample API Calls and Homing Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A `Postman <http://getpostman.com/>`__ collection illustrating sample
requests is available upon request. The collection will also be added in
a future revision.

`Sample homing templates </doc/examples/README.md>`__ are also
available.

Ubuntu Service Scripts
~~~~~~~~~~~~~~~~~~~~~~

Ubuntu sysvinit (init.d) and upstart (init) scripts are typically
installed at the Ubuntu package level. Since there is no such packaging
at this time, example scripts have been provided in the repository.

To install, place all Conductor `sysvinit
scripts </examples/distribution/ubuntu/init.d>`__ in ``/etc/init.d``,
and all `upstart scripts </examples/distribution/ubuntu/init>`__ in
``/etc/init``.

Set file permissions:

.. code:: bash

    $ sudo chmod 644 /etc/init/conductor*
    $ sudo chmod 755 /etc/init.d/conductor*

If a python virtual environment is being used, edit each
``/etc/init/conductor*`` and ``/etc/init.d/conductor*`` prefixed file so
that ``PYTHON_HOME`` is set to the python virtual environment root
directory.

Next, enable the scripts:

.. code:: bash

    $ sudo update-rc.d conductor-api defaults
    $ sudo update-rc.d conductor-controller defaults
    $ sudo update-rc.d conductor-data defaults
    $ sudo update-rc.d conductor-solver defaults
    $ sudo update-rc.d conductor-reservation defaults
    $ sudo initctl reload-configuration

Conductor components may now be started/stopped like any other Ubuntu
service, for example:

.. code:: bash

    $ sudo service conductor-api start
    $ sudo service conductor-api status
    $ sudo service conductor-api restart
    $ sudo service conductor-api stop

Conductor service scripts automatically create directories for ``log``,
``lock``, ``run``, ``lib``, and ``log`` files, e.g.,
``/var/log/conductor`` and so on.

Log File Rotation
~~~~~~~~~~~~~~~~~

Sample ``logrotate.d`` configuration files have been provided in the
repository.

To install, place all Conductor `logrotate
files </examples/distribution/ubuntu/logrotate.d>`__ in
``/etc/logrotate.d``.

Set file ownership and permissions:

.. code:: bash

    $ sudo chown root:root /etc/logrotate.d/conductor*
    $ sudo chmod 644 /etc/logrotate.d/conductor*

``logrotate.d`` automatically recognizes new files at the next log
rotation opportunity and does not require restarting.

Running conductor-api Under apache2 httpd and mod\_wsgi
-------------------------------------------------------

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

Uninstallation
--------------

Activate a virtual environment (venv) first, if necessary, then
uninstall with:

.. code:: bash

    $ pip uninstall ecomp-conductor

Remove any previously made configuration file changes, user accounts,
Ubuntu/SWM packages, and other settings as needed.

Bug Reporting and Feedback
--------------------------

... is encouraged. Please raise an issue at:
https://jira.onap.org/projects/OPTFRA/summary
