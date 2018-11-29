..
 This work is licensed under a Creative Commons Attribution 4.0
 International License.

=============
Release Notes
=============


Version: 1.2.4
--------------

:Release Date: 2018-11-30 (R3 Casablanca Release)

**New Features**

A summary of features includes: 

* Security enhancements, including integration with AAF to implement access controls on 
    OSDF and HAS northbound interfaces
* Integration with SMS
* Platform Maturity Level 1
    * ~50%+ unit test coverage
    
The Casablanca release for OOF delivered the following Epics. 

    * OPTFRA-106 - OOF Functional Testing Related User Stories and Tasks
    * OPTFRA-266 - Integrate OOF with Certificate and Secret Management Service (CSM)
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

Version: 1.1.1
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