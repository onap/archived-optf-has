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