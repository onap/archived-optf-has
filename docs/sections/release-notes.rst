..
 This work is licensed under a Creative Commons Attribution 4.0
 International License.

=============
Release Notes
=============

Version: 5.0.1
--------------

:Release Date: 2019-09-30 (El Alto Release)

The El Alto release is the fourth release for ONAP Optimization Framework (OOF).

Artifacts released:

optf-has:1.3.3

**New Features**

No new features were added in the release. However, the HAS-Music interface was enhanced from HAS to enable HTTPS based communication.
Since MUSIC wasnt ready to expose HTTPS in El Alto, using HTTPS was made into an optional flag through config.

    * [OPTFRA-330] security: HTTPS support for HAS-MUSIC interface

* Platform Maturity Level 1
    * ~56.2%+ unit test coverage


**Bug Fixes**

The El Alto release for OOF fixed the following Bugs.

    * [OPTFRA-579] Json error in homing solution
    * [OPTFRA-521] oof-has-api exposes plain text HTTP endpoint using port 30275
    * [OPTFRA-409] Template example : purpose to be explained


**Known Issues**

**Security Notes**

*Fixed Security Issues*

    * [OPTFRA-521] oof-has-api exposes plain text HTTP endpoint using port 30275

*Known Security Issues*

*Known Vulnerabilities in Used Modules*

**Upgrade Notes**


**Deprecation Notes**


**Other**


Version: 4.0.0
--------------

:Release Date: 2019-06-06 (Dublin Release)

**New Features**

A summary of features includes:

* Extend OOF to support traffic distribution optimization
* Implement encryption for HAS internal and external communication

* Platform Maturity Level 1
    * ~56.2%+ unit test coverage

The Dublin release for OOF delivered the following Epics.

    * [OPTFRA-424]	Extend OOF to support traffic distribution optimization
    * [OPTFRA-422]	Move OOF projects' CSIT to run on OOM
    * [OPTFRA-270]	This epic captures stories related to maintaining current S3P levels of the project as new functional requirements are supported

**Bug Fixes**
    * OPTFRA-515	Pod oof-has-controller is in CrashLoopBackOff after ONAP deployment
    * OPTFRA-513	OOF-HAS pods fail to come up in ONAP deployment
    * OPTFRA-492	HAS API pod failure
    * OPTFRA-487	OOF HAS CSIT failing with HTTPS changes
    * OPTFRA-475	Remove Casablanca jobs in preparation for Dublin branch
    * OPTFRA-467	Remove aai simulator code from HAS solver
    * OPTFRA-465	Fix data code smells
    * OPTFRA-461	Enable HTTPS and TLS for HAS API
    * OPTFRA-452	Remove misleading reservation logic
    * OPTFRA-449	Create OOM based CSIT for HAS
    * OPTFRA-448	Multiple Sonar Issues
    * OPTFRA-445	Modify HAS Data component to support new A&AI requests required by Distribute Traffic functionality
    * OPTFRA-444	Implement Distribute Traffic API exposure in HAS
    * OPTFRA-412	Got 'NoneType' error when there's no flavor info inside vim
    * OPTFRA-411	latency_country_rules_loader.py - Remove the unused local variable "ctx".
    * OPTFRA-302	Enhance coverage of existing HAS code to 55%


**Known Issues**

These are all issues with fix version: Dublin Release and status: open, in-progress, reopened

    * OPTFRA-494	HAS request 'limit' argument is ignored.

**Security Issues**

*Fixed Security Issues*

*Known Security Issues*

    * [`OJSI-137 <https://jira.onap.org/browse/OJSI-137>`_] In default deployment OPTFRA (oof-has-api) exposes HTTP port 30275 outside of cluster.

*Known Vulnerabilities in Used Modules*

OPTFRA code has been formally scanned during build time using NexusIQ and no Critical vulnerability was found. `project <https://wiki.onap.org/pages/viewpage.action?pageId=64005463>`_.

**Quick Links**:
    - `OPTFRA project page <https://wiki.onap.org/display/DW/Optimization+Framework+Project>`_
    - `Passing Badge information for OPTFRA <https://bestpractices.coreinfrastructure.org/en/projects/1720>`_
    - `Project Vulnerability Review Table for OPTF <https://wiki.onap.org/pages/viewpage.action?pageId=64005463>`_
**Upgrade Notes**
To upgrade, run docker container or install from source, See Distribution page

**Deprecation Notes**
No features deprecated in this release

**Other**
None


Version: 3.0.1
--------------

:Release Date: 2019-01-31 (Casablanca Maintenance Release)

The following items were deployed with the Casablanca Maintenance Release:


**New Features**

None.

**Bug Fixes**

* [OPTFRA-401] - 	Need flavor id while launching vm.



Version: 3.0.0
--------------

:Release Date: 2018-11-30 (R3 Casablanca Release)

**New Features**

A summary of features includes:

* Security enhancements, including integration with AAF to implement access controls on
    OSDF and HAS northbound interfaces
* Integration with SMS
* Platform Maturity Level 1
    * ~50%+ unit test coverage
* Hardware Platform Awareness Enhancements
    1) Added support for SRIOV-NIC and directives to assist the orchestrator
    2) Select the best candidate across all cloud region based on HPA score.
    3) HPA metrics using prometheus

The Casablanca release for OOF delivered the following Epics.

    * OPTFRA-106 - OOF Functional Testing Related User Stories and Tasks
    * OPTFRA-266 - Integrate OOF with Certificate and Secret Management Service (CSM)
    * OPTFRA-267 - OOF - HPA Enhancements
    * OPTFRA-269 - This epic covers the work to get the OOF development platform ready for Casablanca development
    * OPTFRA-270 - This epic captures stories related to maintaining current S3P levels of the project as new functional requirements are supported
    * OPTFRA-271 - This epic spans the work to progress further from the current security level
    * OPTFRA-272 - This epic spans the work to progress further from the current Performance level
    * OPTFRA-273 - This epic spans the work to progress further from the current Manageability level
    * OPTFRA-274 - This epic spans the work to progress further from the current Usability level
    * OPTFRA-275 - This epic spans the stories to improve deployability of services
    * OPTFRA-276 - Implementing a POC for 5G SON Optimization
    * OPTFRA-298 - Should be able to orchestrate Cross Domain and Cross Layer VPN

**Bug Fixes**

    * OPTFRA-205 - Generated conductor.conf missing configurations
    * OPTFRA-210 - Onboarding to Music error
    * OPTFRA-211 - Error solution for HPA
    * OPTFRA-249 - OOF does not return serviceResourceId in homing solution
    * OPTFRA-259 - Fix intermittent failure of HAS CSIT job
    * OPTFRA-264 - oof-has-zookeeper image pull error
    * OPTFRA-305 - Analyze OOM health check failure
    * OPTFRA-306 - OOF-Homing fails health check in HEAT deployment
    * OPTFRA-321 - Fix osdf functional tests script to fix builder failures
    * OPTFRA-323 - Cannot resolve multiple policies with the same 'hpa-feature' name
    * OPTFRA-325 - spelling mistake
    * OPTFRA-326 - hyperlink links are missing
    * OPTFRA-335 - Making flavors an optional field in HAS candidate object
    * OPTFRA-336 - OOM oof deployment failure on missing image - optf-osdf:1.2.0
    * OPTFRA-338 - Create authentication key for OOF-VFC integration
    * OPTFRA-341 - Cannot support multiple candidates for one feature in one flavor
    * OPTFRA-344 - Fix broken HPA CSIT test
    * OPTFRA-354 - Generalize the logic to process Optimization policy
    * OPTFRA-358 - Tox fails with the AttributeError: 'module' object has no attribute 'MUSIC_API'
    * OPTFRA-359 - Create index on plans table for HAS
    * OPTFRA-362 - AAF Authentication CSIT issues
    * OPTFRA-365 - Fix Jenkins jobs for CMSO
    * OPTFRA-366 - HAS CSIT issues
    * OPTFRA-370 - Update the version of the OSDF and HAS images
    * OPTFRA-374 - 'ModelCustomizationName' should be optional for the request
    * OPTFRA-375 - SO-OSDF request is failing without modelCustomizationName value
    * OPTFRA-384 - Generate and Validate Policy for vFW testing
    * OPTFRA-385 - resourceModelName is sent in place of resourceModuleName
    * OPTFRA-388 - Fix OOF to handle sdnr/configdb api changes
    * OPTFRA-395 - CMSO - Fix security violations and increment version


**Known Issues**

These are all issues with fix version: Casablanca Release and status: open, in-progress, reopened

    * OPTFRA-401 - Need flavor id while launching vm
    * OPTFRA-398 - Add documentation for OOF-VFC interaction
    * OPTFRA-393 - CMSO Implement code coverage
    * OPTFRA-383 - OOF 7 of 8 pods are not starting in a clean master 20181029
    * OPTFRA-368 - Remove Beijing repositories from CLM jenkins
    * OPTFRA-337 - Document new transitions in HAS states
    * OPTFRA-331 - Role-based access controls to OOF
    * OPTFRA-329 - role based access control for OSDF-Policy interface
    * OPTFRA-316 - Clean up hard-coded references to south bound dependencies
    * OPTFRA-314 - Create user stories for documenting new APIs defined for OOF
    * OPTFRA-304 - Code cleaning
    * OPTFRA-300 - Fix Heat deployment scripts for OOF
    * OPTFRA-298 - Should be able to orchestrate Cross Domain and Cross Layer VPN
    * OPTFRA-297 - OOF Should support Cross Domain and Cross Layer VPN
    * OPTFRA-296 - Support SON (PCI) optimization using OSDF
    * OPTFRA-293 - Implement encryption for all OSDF internal and external communication
    * OPTFRA-292 - Implement encryption for all HAS internal and external communication
    * OPTFRA-279 - Policy-based capacity check enhancements
    * OPTFRA-276 - Implementing a POC for 5G SON Optimization
    * OPTFRA-274 - This epic spans the work to progress further from the current Usability level
    * OPTFRA-273 - This epic spans the work to progress further from the current Manageability level
    * OPTFRA-272 - This epic spans the work to progress further from the current Performance level
    * OPTFRA-271 - This epic spans the work to progress further from the current security level
    * OPTFRA-270 - This epic captures stories related to maintaining current S3P levels of the project as new functional requirements are supported
    * OPTFRA-269 - This epic covers the work to get the OOF development platform ready for Casablanca development
    * OPTFRA-268 - OOF - project specific enhancements
    * OPTFRA-266 - Integrate OOF with Certificate and Secret Management Service (CSM)
    * OPTFRA-262 - ReadTheDoc - update for R3
    * OPTFRA-260 - Testing vCPE flows with multiple clouds
    * OPTFRA-240 - Driving Superior Isolation for Tiered Services using Resource Reservation -- Optimization Policies for Residential vCPE
    * OPTFRA-223 - On boarding and testing AAF certificates for OSDF

**Security Issues**

OPTFRA code has been formally scanned during build time using NexusIQ and no Critical vulnerability was found.

**Quick Links**:
 	- `OPTFRA project page <https://wiki.onap.org/display/DW/Optimization+Framework+Project>`_

 	- `Passing Badge information for OPTFRA <https://bestpractices.coreinfrastructure.org/en/projects/1720>`_

**Upgrade Notes**
To upgrade, run docker container or install from source, See Distribution page

**Deprecation Notes**
No features deprecated in this release

**Other**
None

Version: 2.0.0
--------------

:Release Date: 2018-06-07 (Beijing Release)

**New Features**

The ONAP Optimization Framework (OOF) is new in Beijing. A summary of features incldues:

* Baseline HAS functionality
    * support for VCPE use case
    * support for HPA (Hardware Platform Awareness)
* Integration with OOF OSDF, SO, Policy, AAI, and Multi-Cloud
* Platform Maturity Level 1
    * ~50%+ unit test coverage

The Beijing release for OOF delivered the following Epics.

    * [OPTFRA-2] - On-boarding and Stabilization of the OOF seed code

    * [OPTFRA-6] - Integrate OOF with other ONAP components

    * [OPTFRA-7] - Integration with R2 Use Cases [HPA, Change Management, Scaling]

    * [OPTFRA-20] - OOF Adapters for Retrieving and Resolving Policies

    * [OPTFRA-21] - OOF Packaging

    * [OPTFRA-28] - OOF Adapters for Beijing Release (Policy, SDC, A&AI, Multi Cloud, etc.)

    * [OPTFRA-29] - Policies and Specifications for Initial Applications [Change Management, HPA]

    * [OPTFRA-32] - Platform Maturity Requirements for Beijing release

    * [OPTFRA-33] - OOF Support for HPA

    * [OPTFRA-105] - All Documentation Related User Stories and Tasks


**Bug Fixes**

None. Initial release R2 Beijing. No previous versions

**Known Issues**

    * [OPTFRA-179] - Error solution for HPA

    * [OPTFRA-205] - Onboarding to Music error

    * [OPTFRA-210] - Generated conductor.conf missing configurations

    * [OPTFRA-211] - Remove Extraneous Flavor Information from cloud-region cache


**Security Issues**

OPTFRA code has been formally scanned during build time using NexusIQ and no Critical vulnerability was found.

Quick Links:
 	- `OPTFRA project page <https://wiki.onap.org/display/DW/Optimization+Framework+Project>`_

 	- `Passing Badge information for OPTFRA <https://bestpractices.coreinfrastructure.org/en/projects/1720>`_

**Upgrade Notes**
None. Initial release R2 Beijing. No previous versions

**Deprecation Notes**
None. Initial release R2 Beijing. No previous versions

**Other**
None
