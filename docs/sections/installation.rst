.. This work is licensed under a Creative Commons Attribution 4.0 International License.

Installation
=============================================

Installing from the Source Code
------------------------------------
Get HAS seed code from the Linux Foundation Projects page

.. code-block:: bash

    $ git clone https://gerrit.onap.org/r/optf/has

Use python virtual environment (https://virtualenv.pypa.io/en/stable/) to create and manage libraries and dependencies for HAS project.
    $ virtualenv {virtual_environment_location}
    
    $ source {virtual_environemtn_location}/bin/activate

Inside of /has/conductor folder, run the following commands:
    $ python setup.py install
    
    $ pip install -e .

In {virtual_environment_location}/bin folder, you should see the five components of HAS/Conductor project
conductor-api,conductor-controller, conductor-solver, conductor-reservation, conductor-data
