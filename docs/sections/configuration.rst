Configuration
=============

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

    [db_options]

    # db_backend to use
    db_backend = etcd

    # Use music mock api
    music_mock = False

Set ``db_backend`` to the db(music/etcd) which is being deployed. Based on this
options, conductor will decide on using the corresponding client to access the
backend.

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
