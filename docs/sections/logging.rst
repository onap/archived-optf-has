.. This work is licensed under a Creative Commons Attribution 4.0 International License.

Logging
=============================================

HAS uses a single logger, oslo, across all the components. The logging format is compliant with the EELF recommendations, 
including having the following logs:
error, audit, metric, application.

The log statements follow the following format (values default to preset values when missing):

Timestamp|RequestId|ServiceInstanceId|ThreadId|Virtual Server Name|ServiceName|InstanceUUID|Log Level|Alarm Severity Level|Server IP Address|HOST NAME|Remote IP Address|Class name|Timer|Detailed Message

The logger util module can be found at: 

<>/has/conductor/conductor/common/utils/conductor_logging_util.py

Log File Rotation
-----------------

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
