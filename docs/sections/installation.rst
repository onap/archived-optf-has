Installation
============

OOF-HAS OOM Charts
------------------

HAS charts are located in the `OOM repository <https://git.onap.org/oom/>`__

Please refer OOM documentation for deploying/undeploying the OOF compoenents
via helm charts in the k8s environment.

Local Installation
------------------

HAS components can be deployed in two ways in a local environment for development
and testing.

Docker Installation
-------------------

Building Docker Images
~~~~~~~~~~~~~~~~~~~~~~

Build the HAS docker images using the maven build from the root of the project

.. code:: bash

    git clone --depth 1 https://gerrit.onap.org/r/optf/has
    cd has
    mvn clean install

Installing the components and simulators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HAS docker containers can be installed using the shell scripts in the CSIT directory
which includes the script to deploy the startup dependencies(SMS, ETCD) and a
few simulators.

.. code:: bash

    export WORKSPACE=$(pwd)/csit
    ./csit/plans/default/setup.sh

Similarly the installed components can be deleted using the teardown script.

.. code:: bash

    export WORKSPACE=$(pwd)/csit
    ./csit/plans/default/teardown.sh

Note: The simulator setup can be disabled by the commenting out the commands from
the setup scripts.

Installation from the source
----------------------------

HAS components can be installed locally by directly in a linux based environment.
This will be significant for testing and debugging during developme

Requirements
~~~~~~~~~~~~

Conductor is officially supported on most of the linux based environment, but of
the development and testing were done on Ubuntu based machines.

Ensure the following packages are present, as they may not be
included by default:

-  libffi-dev
-  python3.8

Installing Dependent Components(AAF-SMS, ETCD/MUSIC)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The scripts to install and uninstall the components are present in the
CSIT directory.

**Note**: For setting up SMS, ETCD and MUSIC, docker must be present in
the machine.

For installing/uninstalling AAF-SMS,

.. code:: bash

    cd csit/scripts
    # install SMS
    source setup-sms.sh
    # uninstall SMS
    docker stop sms
    docker stop vault
    docker rm sms
    docker rm vault

For installing/uninstalling ETCD

.. code:: bash

    cd csit/scripts
    # install etcd
    source etcd_Script.sh
    # uninstall etcd
    source etcd_teardown_script.sh

Installing From Source
~~~~~~~~~~~~~~~~~~~~~~

**IMPORTANT**: Perform the steps in this section after *optionally*
configuring and activating a python virtual environment.

Conductor source in ONAP is maintained in
https://gerrit.onap.org/r/optf/has.

Clone the git repository, and then install from within the ``conductor``
directory:

.. code:: bash

    git clone --depth 1 https://gerrit.onap.org/r/optf/has
    cd conductor
    pip install --no-cache-dir -e .

Verifying Installation
~~~~~~~~~~~~~~~~~~~~~~

Each of the five Conductor services may be invoked with the ``--help``
option:

.. code:: bash

    conductor-api -- --help
    conductor-controller --help
    conductor-data --help
    conductor-solver --help
    conductor-reservation --help

**NOTE**: The ``conductor-api`` command is deliberate. ``--`` is used as
as separator between the arguments used to start the WSGI server and the
arguments passed to the WSGI application.

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

Sample API Calls and Homing Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A `Postman <http://getpostman.com/>`__ collection illustrating sample
requests is available upon request. The collection will also be added in
a future revision.

`Sample homing templates <example.html>`__ are also
available.
