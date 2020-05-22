.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. Copyright (C) 2017-2018 AT&T Intellectual Property. All rights reserved.
.. Copyright (C) 2020 Wipro Limited. All rights reserved.

Homing Specification Guide
==========================


This document describes the Homing Template format, used by the Homing
service. It is a work in progress and subject to frequent revision.

Template Structure
------------------

Homing templates are defined in YAML and follow the structure outlined
below.

.. code:: yaml

    homing_template_version: 2017-10-10
    parameters:
      PARAMETER_DICT
    locations:
      LOCATION_DICT
    demands:
      DEMAND_DICT
    constraints:
      CONSTRAINT_DICT
    reservations:
      RESERVATION_DICT
    optimization:
      OPTIMIZATION

-  ``homing_template_version``: This key with value 2017-10-10 (or a
   later date) indicates that the YAML document is a Homing template of
   the specified version.
-  ``parameters``: This section allows for specifying input parameters
   that have to be provided when instantiating the homing template.
   Typically, this section is used for providing runtime parameters
   (like SLA thresholds), which in turn is used in the existing homing
   policies. The section is optional and can be omitted when no input is
   required.
-  ``locations``: This section contains the declaration of geographic
   locations. This section is optional and can be omitted when no input
   is required.
-  ``demands``: This section contains the declaration of demands. This
   section with at least one demand should be defined in any Homing
   template, or the template would not really do anything when being
   instantiated.
-  ``constraints``: This section contains the declaration of
   constraints. The section is optional and can be omitted when no input
   is required.
-  ``reservations``: This section contains the declaration of required
   reservations. This section is optional and can be omitted when
   reservations are not required.
-  ``optimization``: This section allows the declaration of an
   optimization. This section is optional and can be omitted when no
   input is required.

Homing Template Version
-----------------------

The value of ``homing_template_version`` tells HAS not only the format
of the template but also features that will be validated and supported.
Only one value is supported: ``2017-10-10`` in the initial release of
HAS.

.. code:: yaml

    homing_template_version: 2017-10-10

Parameters
----------

The **parameters** section allows for specifying input parameters that
have to be provided when instantiating the template. Such parameters are
typically used for providing runtime inputs (like SLA thresholds), which
in turn is used in the existing homing policies. This also helps build
reusable homing constraints where these parameters can be embedded
design time, and it corresponding values can be supplied during runtime.

Each parameter is specified with the name followed by its value. Values
can be strings, lists, or dictionaries.

Example
~~~~~~~

In this example, ``provider_name`` is a string and ``service_info`` is a
dictionary containing both a string and a list (keyed by ``base_url``
and ``nod_config``, respectively).

.. code:: yaml

    parameters:
      provider_name: multicloud
      service_info:
        base_url: http://serviceprovider.sdngc.com/
        nod_config:
        - http://nod/config_a.yaml
        - http://nod/config_b.yaml
        - http://nod/config_c.yaml
        - http://nod/config_d.yaml

A parameter can be referenced in place of any value. See the **Intrinsic
Functions** section for more details.

Locations
---------

One or more **locations** may be declared. A location may be referenced
by one or more ``constraints``. Locations may be defined in any of the
following ways:

Coordinate
~~~~~~~~~~

A geographic coordinate expressed as a latitude and longitude.

+---------------+----------------------------+
| Key           | Value                      |
+===============+============================+
| ``latitude``  | Latitude of the location.  |
+---------------+----------------------------+
| ``longitude`` | Longitude of the location. |
+---------------+----------------------------+

Host Name
~~~~~~~~~

An opaque host name that can be translated to a coordinate via an
inventory provider (e.g., A&AI).

+---------------+-----------------------------------+
| Key           | Value                             |
+===============+===================================+
| ``host_name`` | Host name identifying a location. |
+---------------+-----------------------------------+

CLLI
~~~~

Common Language Location Identification (CLLI)
code(https://en.wikipedia.org/wiki/CLLI_code).

+---------------+-------------------+
| Key           | Value             |
+===============+===================+
| ``clli_code`` | 8 character CLLI. |
+---------------+-------------------+

**Questions**

-  Do we need functions that can convert one of these to the other?
   E.g., CLLI Codes to a latitude/longitude

Placemark
~~~~~~~~~

An address expressed in geographic region-agnostic terms (referred to as
a *placemark*).

*This is an example as of Frankfurt release. Support for this schema is
 deferred to subsequent release.*

+-----------------------------------+----------------------------------+
| Key                               | Value                            |
+===================================+==================================+
| ``iso_country_code``              | The abbreviated country name     |
|                                   | associated with the placemark.   |
+-----------------------------------+----------------------------------+
| ``postal_code``                   | The postal code associated with  |
|                                   | the placemark.                   |
+-----------------------------------+----------------------------------+
| ``administrative_area``           | The state or province associated |
|                                   | with the placemark.              |
+-----------------------------------+----------------------------------+
| ``sub_administrative_area``       | Additional administrative area   |
|                                   | information for the placemark.   |
+-----------------------------------+----------------------------------+
| ``locality``                      | The city associated with the     |
|                                   | placemark.                       |
+-----------------------------------+----------------------------------+
| ``sub_locality``                  | Additional city-level            |
|                                   | information for the placemark.   |
+-----------------------------------+----------------------------------+
| ``thoroughfare``                  | The street address associated    |
|                                   | with the placemark.              |
+-----------------------------------+----------------------------------+
| ``sub_thoroughfare``              | Additional street-level          |
|                                   | information for the placemark.   |
+-----------------------------------+----------------------------------+

**Note:**

-  A geocoder could be used to convert placemarks to a
   latitude/longitude

Examples
~~~~~~~~

The following examples illustrate a location expressed in coordinate,
host_name, CLLI, and placemark, respectively.

.. code:: yaml

    locations:
      location_using_coordinates:
        latitude: 32.897480
        longitude: -97.040443

      host_location_using_host_name:
        host_name: USESTCDLLSTX55ANZ123

      location_using_clli:
        clli_code: DLLSTX55

      location_using_placemark:
        sub_thoroughfare: 1
        thoroughfare: ATT Way
        locality: Bedminster
        administrative_area: NJ
        postal_code: 07921-2694

Demands
-------

A **demand** can be satisfied by using candidates drawn from
inventories. Each demand is uniquely named. Inventory is considered to
be opaque and can represent anything from which candidates can be drawn.

A demand’s resource requirements are determined by asking an **inventory
provider** for one or more sets of **inventory candidates** against
which the demand will be made. An explicit set of candidates may also be
declared, for example, if the only candidates for a demand are
predetermined.

Demand criteria is dependent upon the inventory provider in use.

**Provider-agnostic Schema**

+-----------------------------+------------------------------------+
| Key                         | Value                              |
+=============================+====================================+
| ``inventory_provider``      | A HAS-supported inventory          |
|                             | provider.                          |
+-----------------------------+------------------------------------+
| ``inventory_type``          | The reserved words ``cloud``       |
|                             | (cloud regions), ``service`` (for  |
|                             | existing service instances),       |
|                             | ``vfmodule`` (for vf instances),   |
|                             | ``nssi`` (for slice subnet         |
|                             | instances). Exactly one inventory  |
|                             | type may be specified.             |
+-----------------------------+------------------------------------+
| ``filtering_attributes``    | A list of key-value pairs, that is |
| (Optional)                  | used to select inventory           |
|                             | candidates that match *all* the    |
|                             | specified attributes. The key      |
|                             | should be a uniquely identifiable  |
|                             | attribute at the inventory         |
|                             | provider.                          |
+-----------------------------+------------------------------------+
| ``passthrough_attributes``  | A list of key-value pairs, that    |
| (Optional)                  | will be added to the candidate's   |
|                             | attribute directly from template.  |
+-----------------------------+------------------------------------+
| ``service_type`` (Optional) | If ``inventory_type`` is           |
|                             | ``service``, a list of one or more |
|                             | provider-defined service types. If |
|                             | only one service type is           |
|                             | specified, it may appear without   |
|                             | list markers (``[]``).             |
+-----------------------------+------------------------------------+
| ``service_id`` (Optional)   | If ``inventory_type`` is           |
|                             | ``service``, a list of one or more |
|                             | provider-defined service ids. If   |
|                             | only one service id is specified,  |
|                             | it may appear without list markers |
|                             | (``[]``).                          |
+-----------------------------+------------------------------------+
| ``default_cost`` (Optional) | The default cost of an inventory   |
|                             | candidate, expressed as currency.  |
|                             | This must be specified if the      |
|                             | inventory provider may not always  |
|                             | return a cost.                     |
+-----------------------------+------------------------------------+
| ``required_candidates``     | A list of one or more candidates   |
| (Optional)                  | from which a solution will be      |
|                             | explored. Must be a valid          |
|                             | candidate as described in the      |
|                             | **candidate schema**.              |
+-----------------------------+------------------------------------+
| ``excluded_candidates``     | A list of one or more candidates   |
| (Optional)                  | that should be excluded from the   |
|                             | search space. Must be a valid      |
|                             | candidate as described in the      |
|                             | **candidate schema**.              |
+-----------------------------+------------------------------------+
| ``existing_placement``      | The current placement for the      |
| (Optional)                  | demand. Must be a valid candidate  |
|                             | as described in the **candidate    |
|                             | schema**.                          |
+-----------------------------+------------------------------------+

**Note**

- The demand attributes in the template come from either policy or from
  a northbound request scope.

.. _examples-1:

Examples
~~~~~~~~

The following example helps understand a demand specification using
Active & Available Inventory (A&AI), the inventory provider-of-record
for ONAP.

**Inventory Provider Criteria**

+-----------------------------+------------------------------------+
| Key                         | Value                              |
+=============================+====================================+
| ``inventory_provider``      | Examples: ``aai``, ``multicloud``. |
+-----------------------------+------------------------------------+
| ``inventory_type``          | The reserved words ``cloud``       |
|                             | (cloud regions), ``service`` (for  |
|                             | existing service instances),       |
|                             | ``vfmodule`` (for vf instances),   |
|                             | ``nssi`` (for slice subnet         |
|                             | instances). Exactly one inventory  |
|                             | type may be specified.             |
+-----------------------------+------------------------------------+
| ``filtering attributes``    | A list of key-value pairs to match |
|  (Optional)                 | against inventory when drawing     |
|                             | candidates.                        |
+-----------------------------+------------------------------------+
| ``passthrough_attributes``  | A list of key-value pairs, that    |
| (Optional)                  | will be added to the candidate's   |
|                             | attribute directly from template.  |
+-----------------------------+------------------------------------+
| ``service_type`` (Optional) | Examples may include ``vG``,       |
|                             | ``vG_MuxInfra``, etc.              |
+-----------------------------+------------------------------------+
| ``service_id`` (Optional)   | Must be a valid service id.        |
|                             | Examples may include ``vCPE``,     |
|                             | ``VoLTE``, etc.                    |
+-----------------------------+------------------------------------+
| ``default_cost`` (Optional) | The default cost of an inventory   |
|                             | candidate, expressed as a unitless |
|                             | number.                            |
+-----------------------------+------------------------------------+
| ``required_candidates``     | A list of one or more valid        |
| (Optional)                  | candidates. See **Candidate        |
|                             | Schema** for details.              |
+-----------------------------+------------------------------------+
| ``excluded_candidates``     | A list of one or more valid        |
| (Optional)                  | candidates. See **Candidate        |
|                             | Schema** for details.              |
+-----------------------------+------------------------------------+
| ``existing_placement``      | A single valid candidate,          |
| (Optional)                  | representing the current placement |
|                             | for the demand. See **candidate    |
|                             | schema** for details.              |
+-----------------------------+------------------------------------+

**Candidate Schema**

The following is the schema for a valid ``candidate``:

- ``candidate_id`` uniquely identifies a candidate. Currently, it is
  either a Service Instance ID or Cloud Region ID.
- ``candidate_type`` identifies the type of the candidate. Currently, it
  is either ``cloud`` or ``service``. \* ``inventory_type`` is defined
  as described in **Inventory Provider Criteria** (above).
- ``inventory_provider`` identifies the inventory from which the
  candidate was drawn. \*
- ``host_id`` is an ID of a specific host (used only when referring to
  service/existing inventory).
- ``cost`` is expressed as a unitless number.
- ``location_id`` is always a location ID of the specified location type
  (e.g., for a type of ``cloud`` this will be an Cloud Region ID).
- ``location_type`` is an inventory provider supported location type.
- ``latitude`` is a valid latitude corresponding to the *location_id*.
- ``longitude`` is a valid longitude corresponding to the *location_id*.
- ``city`` (Optional) city corresponding to the *location_id*.
- ``state`` (Optional) state corresponding to the *location_id*.
- ``country`` (Optional) country corresponding to the *location_id*.
- ``region`` (Optional) geographic region corresponding to the
  *location_id*.
- ``complex_name`` (Optional) Name of the complex corresponding to the
  *location_id*.
- ``cloud_owner`` (Optional) refers to the *cloud owner*
  (e.g., ``azure``, ``aws``, ``att``, etc.).
- ``cloud_region_version`` (Optional) is an inventory provider supported
  version of the cloud region.
- ``physical_location_id`` (Optional) is an inventory provider supported
  CLLI code corresponding to the cloud region.

**Examples**

**Service Candidate**

.. code-block:: json

    {
        "candidate_id": "1ac71fb8-ad43-4e16-9459-c3f372b8236d",
        "candidate_type": "service",
        "inventory_type": "service",
        "inventory_provider": "aai",
        "host_id": "vnf_123456",
        "cost": "100",
        "location_id": "DLLSTX9A",
        "location_type": "azure",
        "latitude": "32.897480",
        "longitude": "-97.040443",
        "city": "Dallas",
        "state": "TX",
        "country": "USA",
        "region": "US",
        "complex_name": "dalls_one",
        "cloud_owner": "att-aic",
        "cloud_region_version": "1.1",
        "physical_location_id": "DLLSTX9A"
    }

**Cloud Candidate**

.. code-block:: json

    {
        "candidate_id": "NYCNY55",
        "candidate_type": "cloud",
        "inventory_type": "cloud",
        "inventory_provider": "aai",
        "cost": "100",
        "location_id": "NYCNY55",
        "location_type": "azure",
        "latitude": "40.7128",
        "longitude": "-74.0060",
        "city": "New York",
        "state": "NY",
        "country": "USA",
        "region": "US",
        "complex_name": "ny_one",
        "cloud_owner": "att-aic",
        "cloud_region_version": "1.1",
        "physical_location_id": "NYCNY55",
        "flavors": {
           "flavor":[
              {
                 "flavor-id":"9cf8220b-4d96-4c30-a426-2e9382f3fff2",
                 "flavor-name":"flavor-numa-cpu-topology-instruction-set",
                 "flavor-vcpus":64,
                 "flavor-ram":65536,
                 "flavor-disk":1048576,
                 "flavor-ephemeral":128,
                 "flavor-swap":"0",
                 "flavor-is-public":false,
                 "flavor-selflink":"pXtX",
                 "flavor-disabled":false,
                 "hpa-capabilities":{
                    "hpa-capability":[
                       {
                          "hpa-capability-id":"01a4bfe1-1993-4fda-bd1c-ef333b4f76a9",
                          "hpa-feature":"cpuInstructionSetExtensions",
                          "hpa-version":"v1",
                          "architecture":"Intel64",
                          "resource-version":"1521306560982",
                          "hpa-feature-attributes":[
                             {
                                "hpa-attribute-key":"instructionSetExtensions",
                                "hpa-attribute-value":"{\"value\":{['AAA', 'BBB', 'CCC', 'DDD']}}",
                                "resource-version":"1521306560989"
                             }
                          ]
                       },
                       {
                          "hpa-capability-id":"167ad6a2-7d9c-4bf2-9a1b-30e5311b8c66",
                          "hpa-feature":"numa",
                          "hpa-version":"v1",
                          "architecture":"generic",
                          "resource-version":"1521306561020",
                          "hpa-feature-attributes":[
                             {
                                "hpa-attribute-key":"numaCpu-1",
                                "hpa-attribute-value":"{\"value\":4}",
                                "resource-version":"1521306561060"
                             },
                             {
                                "hpa-attribute-key":"numaNodes",
                                "hpa-attribute-value":"{\"value\":2}",
                                "resource-version":"1521306561088"
                             },
                             {
                                "hpa-attribute-key":"numaCpu-0",
                                "hpa-attribute-value":"{\"value\":2}",
                                "resource-version":"1521306561028"
                             },
                             {
                                "hpa-attribute-key":"numaMem-0",
                                "hpa-attribute-value":"{\"value\":2, \"unit\":\"GB\" }",
                                "resource-version":"1521306561044"
                             },
                             {
                                "hpa-attribute-key":"numaMem-1",
                                "hpa-attribute-value":"{\"value\":4, \"unit\":\"GB\" }",
                                "resource-version":"1521306561074"
                             }
                          ]
                       },
                       {
                          "hpa-capability-id":"13ec6d4d-7fee-48d8-9e4a-c598feb101ed",
                          "hpa-feature":"basicCapabilities",
                          "hpa-version":"v1",
                          "architecture":"generic",
                          "resource-version":"1521306560909",
                          "hpa-feature-attributes":[
                             {
                                "hpa-attribute-key":"numVirtualCpu",
                                "hpa-attribute-value":"{\"value\":64}",
                                "resource-version":"1521306560932"
                             },
                             {
                                "hpa-attribute-key":"virtualMemSize",
                                "hpa-attribute-value":"{\"value\":65536, \"unit\":\"MB\" }",
                                "resource-version":"1521306560954"
                             }
                          ]
                       },
                       {
                          "hpa-capability-id":"8fa22e64-41b4-471f-96ad-6c4708635e4c",
                          "hpa-feature":"cpuTopology",
                          "hpa-version":"v1",
                          "architecture":"generic",
                          "resource-version":"1521306561109",
                          "hpa-feature-attributes":[
                             {
                                "hpa-attribute-key":"numCpuCores",
                                "hpa-attribute-value":"{\"value\":8}",
                                "resource-version":"1521306561114"
                             },
                             {
                                "hpa-attribute-key":"numCpuThreads",
                                "hpa-attribute-value":"{\"value\":8}",
                                "resource-version":"1521306561138"
                             },
                             {
                                "hpa-attribute-key":"numCpuSockets",
                                "hpa-attribute-value":"{\"value\":6}",
                                "resource-version":"1521306561126"
                             }
                          ]
                       }
                    ]
                 },
                 "resource-version":"1521306560203"
              },
              {
                 "flavor-id":"f5aa2b2e-3206-41b6-80d5-cf041b098c43",
                 "flavor-name":"flavor-cpu-pinning-ovsdpdk-instruction-set",
                 "flavor-vcpus":32,
                 "flavor-ram":131072,
                 "flavor-disk":2097152,
                 "flavor-ephemeral":128,
                 "flavor-swap":"0",
                 "flavor-is-public":false,
                 "flavor-selflink":"pXtX",
                 "flavor-disabled":false,
                 "hpa-capabilities":{
                    "hpa-capability":[
                       {
                          "hpa-capability-id":"4d04f4d8-e257-4442-8417-19a525e56096",
                          "hpa-feature":"cpuInstructionSetExtensions",
                          "hpa-version":"v1",
                          "architecture":"generic",
                          "resource-version":"1521306561223",
                          "hpa-feature-attributes":[
                             {
                                "hpa-attribute-key":"instructionSetExtensions",
                                "hpa-attribute-value":"{\"value\":{['A11', 'B22']}}",
                                "resource-version":"1521306561228"
                             }
                          ]
                       },
                       {
                          "hpa-capability-id":"8d36a8fe-bfee-446a-bbcb-881ee66c8f78",
                          "hpa-feature":"ovsDpdk",
                          "hpa-version":"v1",
                          "architecture":"generic",
                          "resource-version":"1521306561170",
                          "hpa-feature-attributes":[
                             {
                                "hpa-attribute-key":"dataProcessingAccelerationLibrary",
                                "hpa-attribute-value":"{\"value\":\"v18.02\"}",
                                "resource-version":"1521306561175"
                             }
                          ]
                       },
                       {
                          "hpa-capability-id":"c140c945-1532-4908-86c9-d7f71416f1dd",
                          "hpa-feature":"cpuPinning",
                          "hpa-version":"v1",
                          "architecture":"generic",
                          "resource-version":"1521306561191",
                          "hpa-feature-attributes":[
                             {
                                "hpa-attribute-key":"logicalCpuPinningPolicy",
                                "hpa-attribute-value":"{\"value\":\"dedicated\"}",
                                "resource-version":"1521306561196"
                             },
                             {
                                "hpa-attribute-key":"logicalCpuThreadPinningPolicy",
                                "hpa-attribute-value":"{value:\"prefer\"}",
                                "resource-version":"1521306561206"
                             }
                          ]
                       },
                       {
                          "hpa-capability-id":"4565615b-1077-4bb5-a340-c5be48db2aaa",
                          "hpa-feature":"basicCapabilities",
                          "hpa-version":"v1",
                          "architecture":"generic",
                          "resource-version":"1521306561244",
                          "hpa-feature-attributes":[
                             {
                                "hpa-attribute-key":"numVirtualCpu",
                                "hpa-attribute-value":"{\"value\":32}",
                                "resource-version":"1521306561259"
                             },
                             {
                                "hpa-attribute-key":"virtualMemSize",
                                "hpa-attribute-value":"{\"value\":131072, \"unit\":\"MB\" }",
                                "resource-version":"1521306561248"
                             }
                          ]
                       }
                    ]
                 },
                 "resource-version":"1521306561164"
              }
           ]
        }
    }

**vfmodule candidate**

.. code-block:: json

    {
        "candidate_id": "d187d743-5932-4fb9-a42d-db0a5be5ba7e",
        "city": "example-city-val-27150",
        "cloud_owner": "CloudOwner",
        "cloud_region_version": "1",
        "complex_name": "clli1",
        "cost": 1.0,
        "country": "example-country-val-94173",
        "existing_placement": "false",
        "host_id": "vFW-PKG-MC",
        "inventory_provider": "aai",
        "inventory_type": "vfmodule",
        "ipv4-oam-address": "oam_network_zb4J",
        "ipv6-oam-address": "",
        "latitude": "example-latitude-val-89101",
        "location_id": "RegionOne",
        "location_type": "att_aic",
        "longitude": "32.89948",
        "nf-id": "fcbff633-47cc-4f38-a98d-4ba8285bd8b6",
        "nf-name": "vFW-PKG-MC",
        "nf-type": "vnf",
        "passthrough_attributes": {
            "td-role": "anchor"
        },
        "physical_location_id": "clli1",
        "port_key": "vlan_port",
        "region": "example-region-val-13893",
        "service_instance_id": "3e8d118c-10ca-4b4b-b3db-089b5e9e6a1c",
        "service_resource_id": "vPGN-XX",
        "sriov_automation": "false",
        "state": "example-state-val-59487",
        "uniqueness": "false",
        "vf-module-id": "d187d743-5932-4fb9-a42d-db0a5be5ba7e",
        "vf-module-name": "vnf-pkg-r1-t2-mc",
        "vim-id": "CloudOwner_RegionOne",
        "vlan_key": "vlan_key",
        "vnf-type": "5G_EVE_Demo/5G_EVE_PKG 0",
        "vservers": [
            {
                "l-interfaces": [
                    {
                        "interface-id": "4b333af1-90d6-42ae-8389-d440e6ff0e93",
                        "interface-name": "vnf-pkg-r1-t2-mc-vpg_private_2_port-mf7lu55usq7i",
                        "ipv4-addresses": [
                            "10.100.100.2"
                        ],
                        "ipv6-addresses": [],
                        "macaddr": "fa:16:3e:c4:07:7f",
                        "network-id": "59763a33-3296-4dc8-9ee6-2bdcd63322fc",
                        "network-name": ""
                    },
                    {
                        "interface-id": "85dd57e9-6e3a-48d0-a784-4598d627e798",
                        "interface-name": "vnf-pkg-r1-t2-mc-vpg_private_1_port-734xxixicw6r",
                        "ipv4-addresses": [
                            "10.0.110.2"
                        ],
                        "ipv6-addresses": [],
                        "macaddr": "fa:16:3e:b5:86:38",
                        "network-id": "cdb4bc25-2412-4b77-bbd5-791a02f8776d",
                        "network-name": ""
                    },
                    {
                        "interface-id": "edaff25a-878e-4706-ad52-4e3d51cf6a82",
                        "interface-name": "vnf-pkg-r1-t2-mc-vpg_private_0_port-e5qdm3p5ijhe",
                        "ipv4-addresses": [
                            "192.168.10.200"
                        ],
                        "ipv6-addresses": [],
                        "macaddr": "fa:16:3e:ff:d8:6f",
                        "network-id": "932ac514-639a-45b2-b1a3-4c5bb708b5c1",
                        "network-name": ""
                    }
                ],
                "vserver-id": "00bddefc-126e-4e4f-a18d-99b94d8d9a30",
                "vserver-name": "zdfw1fwl01pgn01"
            }
        ]
    }

**nssi candidate**

.. code-block:: json

    {
        "candidate_id": "1a636c4d-5e76-427e-bfd6-241a947224b0",
        "candidate_type": "nssi",
        "conn_density": 0,
        "cost": 1.0,
        "domain": "cn",
        "e2e_latency": 0,
        "exp_data_rate": 0,
        "exp_data_rate_dl": 100,
        "exp_data_rate_ul": 100,
        "instance_name": "nssi_test_0211",
        "inventory_provider": "aai",
        "inventory_type": "nssi",
        "jitter": 0,
        "latency": 20,
        "max_number_of_ues": 0,
        "nsi_id": "4115d3c8-dd59-45d6-b09d-e756dee9b518",
        "nsi_model_invariant_id": "39b10fe6-efcc-40bc-8184-c38414b80771",
        "nsi_model_version_id": "8b664b11-6646-4776-9f59-5c3de46da2d6",
        "nsi_name": "nsi_test_0211",
        "payload_size": 0,
        "reliability": 99.99,
        "resource_sharing_level": "0",
        "survival_time": 0,
        "traffic_density": 0,
        "ue_mobility_level": "stationary",
        "uniqueness": "true"
    }

**Examples**

The following examples illustrate two demands:

-  ``vGMuxInfra``: A vGMuxInfra service, drawing candidates of type
   *service* from the inventory. Only candidates that match the
   customer_id and orchestration-status will be included in the search
   space.
-  ``vG``: A vG, drawing candidates of type *service* and *cloud* from
   the inventory. Only candidates that match the customer_id and
   provisioning-status will be included in the search space.

.. code:: yaml

    demands:
      vGMuxInfra:
      - inventory_provider: aai
        inventory_type: service
        attributes:
          equipment_type: vG_Mux
          customer_id: some_company
          orchestration-status: Activated
          model-id: 174e371e-f514-4913-a93d-ed7e7f8fbdca
          model-version: 2.0
      vG:
      - inventory_provider: aai
        inventory_type: service
        attributes:
          equipment_type: vG
          customer_id: some_company
          provisioning-status: provisioned
      - inventory_provider: aai
        inventory_type: cloud

**Note**

- Cost could be used to specify the cost of choosing a specific
  candidate. For example, choosing an existing VNF instance can be less
  costlier than creating a new instance.

Constraints
-----------

A **Constraint** is used to *eliminate* inventory candidates from one or
more demands that do not meet the requirements specified by the
constraint. Since reusability is one of the cornerstones of HAS,
Constraints are designed to be service-agnostic, and is parameterized
such that it can be reused across a wide range of services. Further, HAS
is designed with a plug-in architecture that facilitates easy addition
of new constraint types.

Constraints are denoted by a ``constraints`` key. Each constraint is
uniquely named and set to a dictionary containing a constraint type, a
list of demands to apply the constraint to, and a dictionary of
constraint properties.

**Considerations while using multiple constraints** \* Constraints
should be treated as a unordered list, and no assumptions should be made
as regards to the order in which the constraints are evaluated for any
given demand. \* All constraints are effectively AND-ed together.
Constructs such as “Constraint X OR Y” are unsupported. \* Constraints
are reducing in nature, and does not increase the available candidates
at any point during the constraint evaluations.

**Schema**

+-------------------------------------------+--------------------------+
| Key                                       | Value                    |
+===========================================+==========================+
| ``CONSTRAINT_NAME``                       | Key is a unique name.    |
+-------------------------------------------+--------------------------+
| ``type``                                  | The type of constraint.  |
|                                           | See **Constraint Types** |
|                                           | for a list of currently  |
|                                           | supported values.        |
+-------------------------------------------+--------------------------+
| ``demands``                               | One or more previously   |
|                                           | declared demands. If     |
|                                           | only one demand is       |
|                                           | specified, it may appear |
|                                           | without list markers     |
|                                           | (``[]``).                |
+-------------------------------------------+--------------------------+
| ``properties`` (Optional)                 | Properties particular to |
|                                           | the specified constraint |
|                                           | type. Use if required by |
|                                           | the constraint.          |
+-------------------------------------------+--------------------------+

.. code:: yaml

    constraints:
      CONSTRAINT_NAME_1:
        type: CONSTRAINT_TYPE
        demands: DEMAND_NAME | [DEMAND_NAME_1, DEMAND_NAME_2, ...]
        properties: PROPERTY_DICT

      CONSTRAINT_NAME_2:
        type: CONSTRAINT_TYPE
        demands: DEMAND_NAME | [DEMAND_NAME_1, DEMAND_NAME_2, ...]
        properties: PROPERTY_DICT

      ...

Constraint Types
~~~~~~~~~~~~~~~~

+-------------------------------------------+--------------------------+
| Type                                      | Description              |
+===========================================+==========================+
| ``attribute``                             | Constraint that matches  |
|                                           | the specified list of    |
|                                           | Attributes.              |
+-------------------------------------------+--------------------------+
| ``distance_between_demands``              | Geographic distance      |
|                                           | constraint between each  |
|                                           | pair of a list of        |
|                                           | demands.                 |
+-------------------------------------------+--------------------------+
| ``distance_to_location``                  | Geographic distance      |
|                                           | constraint between each  |
|                                           | of a list of demands and |
|                                           | a specific location.     |
+-------------------------------------------+--------------------------+
| ``instance_fit``                          | Constraint that ensures  |
|                                           | available capacity in an |
|                                           | existing service         |
|                                           | instance for an incoming |
|                                           | demand.                  |
+-------------------------------------------+--------------------------+
| ``inventory_group``                       | Constraint that enforces |
|                                           | two or more demands are  |
|                                           | satisfied using          |
|                                           | candidates from a        |
|                                           | pre-established group in |
|                                           | the inventory.           |
+-------------------------------------------+--------------------------+
| ``region_fit``                            | Constraint that ensures  |
|                                           | available capacity in an |
|                                           | existing cloud region    |
|                                           | for an incoming demand.  |
+-------------------------------------------+--------------------------+
| ``zone``                                  | Constraint that enforces |
|                                           | co-location/diversity at |
|                                           | the granularities of     |
|                                           | clouds/regions/availabil |
|                                           | ity-zones.               |
+-------------------------------------------+--------------------------+
| ``hpa``                                   | Constraint that          |
|                                           | recommends cloud region  |
|                                           | with an optimal flavor   |
|                                           | based on required HPA    |
|                                           | capabilities for an      |
|                                           | incoming demand.         |
+-------------------------------------------+--------------------------+
| ``vim_fit``                               | Constraint that checks if|
|                                           | the incoming demand fits |
|                                           | the VIM instance.        |
+-------------------------------------------+--------------------------+
| ``license`` (Deferred)                    | License availability     |
|                                           | constraint.              |
+-------------------------------------------+--------------------------+
| ``network_between_demands`` (Deferred)    | Network constraint       |
|                                           | between each pair of a   |
|                                           | list of demands.         |
+-------------------------------------------+--------------------------+
| ``network_to_location`` (Deferred)        | Network constraint       |
|                                           | between each of a list   |
|                                           | of demands and a         |
|                                           | specific                 |
|                                           | location/address.        |
+-------------------------------------------+--------------------------+
| ``threshold``                             | Constraint that checks if|
|                                           | an attribute is within   |
|                                           | the threshold.           |
+-------------------------------------------+--------------------------+

*Note: Constraint names marked “Deferred” **will not** be supported in
the current release of HAS.*

Threshold Values
~~~~~~~~~~~~~~~~

Constraint property values representing a threshold may be an integer or
floating point number, optionally prefixed with a comparison operator:
``=``, ``<``, ``>``, ``<=``, or ``>=``. The default is ``=`` and
optionally suffixed with a unit.

Whitespace may appear between the comparison operator and value, and
between the value and units. When a range values is specified (e.g.,
``10-20 km``), the comparison operator is omitted.

Each property is documented with a default unit. The following units are
supported:

+------------+------------------------------+----------+
| Unit       | Values                       | Default  |
+============+==============================+==========+
| Currency   | ``USD``                      | ``USD``  |
+------------+------------------------------+----------+
| Time       | ``ms``, ``sec``              | ``ms``   |
+------------+------------------------------+----------+
| Distance   | ``km``, ``mi``               | ``km``   |
+------------+------------------------------+----------+
| Throughput | ``Kbps``, ``Mbps``, ``Gbps`` | ``Mbps`` |
+------------+------------------------------+----------+

Attribute
~~~~~~~~~

Constrain one or more demands by one or more attributes, expressed as
properties. Attributes are mapped to the **inventory provider**
specified properties, referenced by the demands. For example, properties
could be hardware capabilities provided by the platform (flavor,
CPU-Pinning, NUMA), features supported by the services, etc.

**Schema**

+--------------+---------------------------------------------------------+
| Property     | Value                                                   |
+==============+=========================================================+
| ``evaluate`` | Opaque dictionary of attribute name and value pairs.    |
|              | Values must be strings or numbers. Encoded and sent to  |
|              | the service provider via a plugin.                      |
+--------------+---------------------------------------------------------+

*Note: Attribute values are not detected/parsed as thresholds by the
Homing framework. Such interpretations and evaluations are inventory
provider-specific and delegated to the corresponding plugin*

.. code:: yaml

    constraints:
      sriov_nj:
        type: attribute
        demands: [my_vnf_demand, my_other_vnf_demand]
        properties:
          evaluate:
            cloud_version: 1.1
            flavor: SRIOV
            subdivision: US-TX
            vcpu_pinning: True
            numa_topology: numa_spanning

Proposal: Evaluation Operators
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To assist in evaluating attributes, the following operators and notation
are proposed:

+-----------+-----------+------------------------------------------------+
| Operator  | Name      | Operand                                        |
+===========+===========+================================================+
| ``eq``    | ``==``    | Any object (string, number, list, dict)        |
+-----------+-----------+------------------------------------------------+
| ``ne``    | ``!=``    |                                                |
+-----------+-----------+------------------------------------------------+
| ``lt``    | ``<``     | A number (strings are converted to float)      |
+-----------+-----------+------------------------------------------------+
| ``gt``    | ``>``     |                                                |
+-----------+-----------+------------------------------------------------+
| ``lte``   | ``<=``    |                                                |
+-----------+-----------+------------------------------------------------+
| ``gte``   | ``>=``    |                                                |
+-----------+-----------+------------------------------------------------+
| ``any``   | ``Any``   | A list of objects (string, number, list, dict) |
+-----------+-----------+------------------------------------------------+
| ``all``   | ``All``   |                                                |
+-----------+-----------+------------------------------------------------+
| ``regex`` | ``RegEx`` | A regular expression pattern                   |
+-----------+-----------+------------------------------------------------+

Example usage:

.. code:: yaml

    constraints:
      sriov_nj:
        type: attribute
        demands: [my_vnf_demand, my_other_vnf_demand]
        properties:
          evaluate:
            cloud_version: {gt: 1.0}
            flavor: {regex: /^SRIOV$/i}
            subdivision: {any: [US-TX, US-NY, US-CA]}

Distance Between Demands
~~~~~~~~~~~~~~~~~~~~~~~~

Constrain each pairwise combination of two or more demands by distance
requirements.

**Schema**

+--------------+------------------------------------------------------------+
| Name         | Value                                                      |
+==============+============================================================+
| ``distance`` | Distance between demands, measured by the geographic path. |
+--------------+------------------------------------------------------------+

The constraint is applied between each pairwise combination of demands.
For this reason, at least two demands must be specified, implicitly or
explicitly.

.. code:: yaml

    constraints:
      distance_vnf1_vnf2:
        type: distance_between_demands
        demands: [my_vnf_demand, my_other_vnf_demand]
        properties:
          distance: < 250 km

Distance To Location
~~~~~~~~~~~~~~~~~~~~

Constrain one or more demands by distance requirements relative to a
specific location.

**Schema**

+--------------+------------------------------------------------------------+
| Property     | Value                                                      |
+==============+============================================================+
| ``distance`` | Distance between demands, measured by the geographic path. |
+--------------+------------------------------------------------------------+
| ``location`` | A previously declared location.                            |
+--------------+------------------------------------------------------------+

The constraint is applied between each demand and the referenced
location, not across all pairwise combinations of Demands.

.. code:: yaml

    constraints:
      distance_vnf1_loc:
        type: distance_to_location
        demands: [my_vnf_demand, my_other_vnf_demand, another_vnf_demand]
        properties:
          distance: < 250 km
          location: LOCATION_ID

Instance Fit
~~~~~~~~~~~~

Constrain each demand by its service requirements.

Requirements are sent as a request to a **service controller**. Service
controllers are defined by plugins in Homing (e.g., ``sdn-c``).

A service controller plugin knows how to communicate with a particular
endpoint (via HTTP/REST, DMaaP, etc.), obtain necessary information, and
make a decision. The endpoint and credentials can be configured through
plugin settings.

**Schema**

+---------------------+------------------------------------------------+
| Property            | Description                                    |
+=====================+================================================+
| ``controller``      | Name of a service controller.                  |
+---------------------+------------------------------------------------+
| ``request``         | Opaque dictionary of key/value pairs. Values   |
|                     | must be strings or numbers. Encoded and sent   |
|                     | to the service provider via a plugin.          |
+---------------------+------------------------------------------------+

.. code:: yaml

    constraints:
      check_for_availability:
        type: instance_fit
        demands: [my_vnf_demand, my_other_vnf_demand]
        properties:
          controller: sdn-c
          request: REQUEST_DICT

Region Fit
~~~~~~~~~~

Constrain each demand’s inventory candidates based on inventory provider
membership.

Requirements are sent as a request to a **service controller**. Service
controllers are defined by plugins in Homing (e.g., ``sdn-c``).

A service controller plugin knows how to communicate with a particular
endpoint (via HTTP/REST, DMaaP, etc.), obtain necessary information, and
make a decision. The endpoint and credentials can be configured through
plugin settings.

**Schema**

+---------------------+------------------------------------------------+
| Property            | Description                                    |
+=====================+================================================+
| ``controller``      | Name of a service controller.                  |
+---------------------+------------------------------------------------+
| ``request``         | Opaque dictionary of key/value pairs. Values   |
|                     | must be strings or numbers. Encoded and sent   |
|                     | to the service provider via a plugin.          |
+---------------------+------------------------------------------------+

.. code:: yaml

    constraints:
      check_for_membership:
        type: region_fit
        demands: [my_vnf_demand, my_other_vnf_demand]
        properties:
          controller: sdn-c
          request: REQUEST_DICT

Zone
~~~~

Constrain two or more demands such that each is located in the same or
different zone category.

Zone categories are inventory provider-defined, based on the demands
being constrained.

**Schema**

+---------------+--------------------------------------------------------+
| Property      | Value                                                  |
+===============+========================================================+
| ``qualifier`` | Zone qualifier. One of ``same`` or ``different``.      |
|               |                                                        |
+---------------+--------------------------------------------------------+
| ``category``  | Zone category. One of ``disaster``, ``region``,        |
|               | ``complex``, ``time``, or ``maintenance``.             |
+---------------+--------------------------------------------------------+

For example, to place two demands in different disaster zones:

.. code:: yaml

    constraints:
      vnf_diversity:
        type: zone
        demands: [my_vnf_demand, my_other_vnf_demand]
        properties:
          qualifier: different
          category: disaster

Or, to place two demands in the same region:

.. code:: yaml

    constraints:
      vnf_affinity:
        type: zone
        demands: [my_vnf_demand, my_other_vnf_demand]
        properties:
          qualifier: same
          category: region

**Notes**

-  These categories could be any of the following: ``disaster_zone``,
   ``region``, ``complex``, ``time_zone``, and ``maintenance_zone``.
   Really, we are talking affinity/anti-affinity at the level of DCs,
   but these terms may cause confusion with affinity/anti-affinity in
   OpenStack.

HPA & Cloud Agnostic Intent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Constrain each demand's inventory candidates based on cloud regions' Hardware
platform capabilities (HPA) and also intent support. Note that currently HPA
the cloud agnostic constraints will use the same schema.

Requirements mapped to the inventory provider specified properties, referenced
by the demands. For eg, properties could be hardware capabilities provided by
the platform through flavors or cloud-region eg:(CPU-Pinning, NUMA), features
supported by the services, etc.


**Schema**

+---------------+--------------------------------------------------------+
| Property      | Value                                                  |
+===============+========================================================+
| ``evaluate``  | List of id, type, directives and flavorProperties of   |
|               | each VM of the VNF demand.                             |
+---------------+--------------------------------------------------------+

+-------------------------+--------------------------------------------------------+
| Property for evaluation | Value                                                  |
+=========================+========================================================+
| ``id``                  | Name of VFC                                            |
+-------------------------+--------------------------------------------------------+
| ``type``                | Type of VFC. Could be ``vnfc`` or ``tocsa.nodes.nfv.   |
|                         | Vdu.Compute`` according to different models            |
+-------------------------+--------------------------------------------------------+
| ``directives``          | Directives for one VFC. Now we only have flavor        |
|                         | directives inside. Each VFC must have one directive    |
+-------------------------+--------------------------------------------------------+
| ``flavorProperties``    | Flavor properties for one VFC. Contains detailed       |
|                         | HPA requirements                                       |
+-------------------------+--------------------------------------------------------+

+--------------------------+-------------------------------------------+
| Property for directives  | Value                                     |
+==========================+===========================================+
| ``type``                 | Type of directive                         |
+--------------------------+-------------------------------------------+
| ``attributes``           | Attributes inside directive               |
+--------------------------+-------------------------------------------+

+--------------------------+-------------------------------------------+
| Property for attributes  | Value                                     |
+==========================+===========================================+
| ``attribute_name``       | Attribute name/label                      |
+--------------------------+-------------------------------------------+
| ``attributes_value``     | Attributes value                          |
+--------------------------+-------------------------------------------+

*Note*: Each VFC must have one directive with type 'flavor_directives' to put the
flavors inside. The ``attribute_name`` is the place to put flavor label and the
``attribute_value`` will first left blank. After getting the proper flavor, OOF will
merge the flavor name into the ``attribute_value`` inside flavor directives. Also,
all the directives coming from one VFC inside the same request will be merged
together in ``directives``, as they are using the same structure as 'directives'.

.. code:: yaml

    constraints:
      hpa_constraint:
        type: hpa
        demands: [my_vnf_demand, my_other_vnf_demand]
        properties:
          evaluate:
            - [ List of {id: {vdu Name},
                        type: {type of VF },
                        directives: DIRECTIVES LIST,
                        flavorProperties: HPACapability DICT} ]

    HPACapability DICT :
      hpa-feature: basicCapabilities
      hpa-version: v1
      architecture: generic
      directives:
        - DIRECTIVES LIST
      hpa-feature-attributes:
        - HPAFEATUREATTRIBUTES LIST

    DIRECTIVES LIST:
      type: String
      attributes:
        - ATTRIBUTES LIST

    ATTRIBUTES LIST:
      attribute_name: String,
      attribute_value: String

    HPAFEATUREATTRIBUTES LIST:
      hpa-attribute-key: String
      hpa-attribute-value: String
      operator: One of OPERATOR
      unit: String
    OPERATOR : ['=', '<', '>', '<=', '>=', 'ALL']

**Example**

Example for HEAT request(SO)

*Note*: Where "attributes":[{"attribute_name":" oof_returned_flavor_label_for_vgw_1 ",
    Admin needs to ensure that this value is same as flavor parameter in HOT

.. code-block:: json

    {
        "hpa_constraint":{
            "type":"hpa",
            "demands":[
               "vG"
            ],
            "properties":{
               "evaluate":[
                  {
                     "id": "vgw_0",
                     "type": "vnfc",
                     "directives": [
                        {
                         "type":"flavor_directives",
                         "attributes":[
                            {
                             "attribute_name":" oof_returned_flavor_label_for_vgw_0 ", 
                             "attribute_value": "<Blank>"
                            }
                         ]
                        }
                     ],
                     "flavorProperties":[
                        {
                           "hpa-feature":"basicCapabilities",
                           "hpa-version":"v1",
                           "architecture":"generic",
                           "mandatory": "True",
                           "directives": [],
                           "hpa-feature-attributes":[
                              {
                                 "hpa-attribute-key":"numVirtualCpu",
                                 "hpa-attribute-value":"32",
                                 "operator":"="
                              }
                           ]
                        },
                        {
                           "hpa-feature":"basicCapabilities",
                           "hpa-version":"v1",
                           "architecture":"generic",
                           "mandatory": "True",
                           "directives": [],
                           "hpa-feature-attributes":[
                              {
                                 "hpa-attribute-key":"virtualMemSize",
                                 "hpa-attribute-value":"64",
                                 "operator":"=",
                                 "unit":"GB"
                              }
                           ]
                        },
                        {
                           "hpa-feature":"ovsDpdk",
                           "hpa-version":"v1",
                           "architecture":"generic",
                           "mandatory": "False",
                           "score": "10",
                           "directives": [],
                           "hpa-feature-attributes":[
                              {
                                 "hpa-attribute-key":"dataProcessingAccelerationLibrary",
                                 "hpa-attribute-value":"v18.02",
                                 "operator":"="
                              }
                           ]
                        },
                        {
                           "hpa-feature": "qosIntentCapabilities",
                           "mandatory": "True",
                           "architecture": "generic",
                           "hpa-version": "v1",
                           "directives": [],
                           "hpa-feature-attributes": [
                              {
                                 "hpa-attribute-key":"Infrastructure Resource Isolation for VNF",
                                 "hpa-attribute-value": "Burstable QoS",
                                 "operator": "=",
                                 "unit": ""
                              },
                              {  "hpa-attribute-key":"Burstable QoS Oversubscription Percentage",
                                 "hpa-attribute-value": "25",
                                 "operator": "=",
                                 "unit": ""
                              }
                           ]
                        }
                     ]
                  },
                  {
                     "id": "vgw_1",
                     "type": "vnfc",
                     "directives": [
                        {
                         "type":"flavor_directives",
                         "attributes":[
                            {
                             "attribute_name":" oof_returned_flavor_label_for_vgw_1 ", 
                             "attribute_value": "<Blank>"
                            }
                         ]
                        }
                     ],
                     "flavorProperties":[
                        {
                           "hpa-feature":"basicCapabilities",
                           "hpa-version":"v1",
                           "architecture":"generic",
                           "mandatory": "False",
                           "score": "5",
                           "directives": [],
                           "hpa-feature-attributes":[
                              {
                                 "hpa-attribute-key":"numVirtualCpu",
                                 "hpa-attribute-value":"8",
                                 "operator":">="
                              }
                           ]
                        },
                        {
                           "hpa-feature":"basicCapabilities",
                           "hpa-version":"v1",
                           "architecture":"generic",
                           "mandatory": "False",
                           "score": "5",
                           "directives": [],
                           "hpa-feature-attributes":[
                              {
                                 "hpa-attribute-key":"virtualMemSize",
                                 "hpa-attribute-value":"16",
                                 "operator":">=",
                                 "unit":"GB"
                              }
                           ]
                        },
                        {
                           "hpa-feature":"sriovNICNetwork",
                           "hpa-version":"v1",
                           "architecture":"generic",
                           "mandatory": "True",
                           "directives": [
                              {
                                "type": "sriovNICNetwork_directives",
                                "attributes": [
                                   { "attribute_name": "oof_returned_vnic_type_for_vgw_1",
                                     "attribute_value": "direct"
                                   },
                                   { "attribute_name": "oof_returned_provider_network_for_vgw_1",
                                     "attribute_value": "physnet2"
                                   }
                                ]
                              }
                           ],
                           "hpa-feature-attributes":[
                              {
                                 "hpa-attribute-key":"pciVendorId",
                                 "hpa-attribute-value":"8086",
                                 "operator":"=",
                                 "unit":""
                              },
                              {
                                 "hpa-attribute-key":"pciDeviceId",
                                 "hpa-attribute-value":"0443",
                                 "operator":"=",
                                 "unit":""
                              },
                              {
                                 "hpa-attribute-key":"pciCount",
                                 "hpa-attribute-value":"1",
                                 "operator":"=",
                                 "unit":""
                              },
                              {
                                 "hpa-attribute-key":"physicalNetwork",
                                 "hpa-attribute-value":"physnet2",
                                 "operator":"=",
                                 "unit":""
                              }
                           ]
                        }
                     ]
                  }
               ]
            }
         }
      }
      
Example for Pure TOSCA request(VF-C)

.. code-block:: json

    {
        "hpa_constraint":{
            "type":"hpa",
            "demands":[
               "vG"
            ],
            "properties":{
               "evaluate":[
                  {
                     "id": "vgw_0",
                     "type": "tocsa.nodes.nfv.Vdu.Compute",
                     "directives": [
                        {
                         "type":"flavor_directives",
                         "attributes":[
                            {
                             "attribute_name":" flavor_name ",
                             "attribute_value": "<Blank>"
                            }
                         ]
                        }
                     ],
                     "flavorProperties":[
                        {
                           "hpa-feature":"basicCapabilities",
                           "hpa-version":"v1",
                           "architecture":"generic",
                           "mandatory": "True",
                           "directives": [],
                           "hpa-feature-attributes":[
                              {
                                 "hpa-attribute-key":"numVirtualCpu",
                                 "hpa-attribute-value":"32",
                                 "operator":"="
                              }
                           ]
                        },
                        {
                           "hpa-feature":"basicCapabilities",
                           "hpa-version":"v1",
                           "architecture":"generic",
                           "mandatory": "True",
                           "directives": [],
                           "hpa-feature-attributes":[
                              {
                                 "hpa-attribute-key":"virtualMemSize",
                                 "hpa-attribute-value":"64",
                                 "operator":"=",
                                 "unit":"GB"
                              }
                           ]
                        },
                        {
                           "hpa-feature":"ovsDpdk",
                           "hpa-version":"v1",
                           "architecture":"generic",
                           "mandatory": "False",
                           "score": "10",
                           "directives": [],
                           "hpa-feature-attributes":[
                              {
                                 "hpa-attribute-key":"dataProcessingAccelerationLibrary",
                                 "hpa-attribute-value":"v18.02",
                                 "operator":"="
                              }
                           ]
                        },
                        {
                           "hpa-feature": "qosIntentCapabilities",
                           "mandatory": "True",
                           "architecture": "generic",
                           "hpa-version": "v1",
                           "directives": [],
                           "hpa-feature-attributes": [
                              {
                                 "hpa-attribute-key":"Infrastructure Resource Isolation for VNF",
                                 "hpa-attribute-value": "Burstable QoS",
                                 "operator": "=",
                                 "unit": ""
                              },
                              {  "hpa-attribute-key":"Burstable QoS Oversubscription Percentage",
                                 "hpa-attribute-value": "25",
                                 "operator": "=",
                                 "unit": ""
                              }
                           ]
                        }
                     ]
                  },
                  {
                     "id": "vgw_1",
                     "type": "tosca.nodes.nfv.Vdu.Compute",
                     "directives": [
                        {
                         "type":"flavor_directives",
                         "attributes":[
                            {
                             "attribute_name":" flavor_name ",
                             "attribute_value": "<Blank>"
                            }
                         ]
                        }
                     ],
                     "flavorProperties":[
                        {
                           "hpa-feature":"basicCapabilities",
                           "hpa-version":"v1",
                           "architecture":"generic",
                           "mandatory": "False",
                           "score": "5",
                           "directives": [],
                           "hpa-feature-attributes":[
                              {
                                 "hpa-attribute-key":"numVirtualCpu",
                                 "hpa-attribute-value":"8",
                                 "operator":">="
                              }
                           ]
                        },
                        {
                           "hpa-feature":"basicCapabilities",
                           "hpa-version":"v1",
                           "architecture":"generic",
                           "mandatory": "False",
                           "score": "5",
                           "directives": [],
                           "hpa-feature-attributes":[
                              {
                                 "hpa-attribute-key":"virtualMemSize",
                                 "hpa-attribute-value":"16",
                                 "operator":">=",
                                 "unit":"GB"
                              }
                           ]
                        },
                        {
                           "hpa-feature":"sriovNICNetwork",
                           "hpa-version":"v1",
                           "architecture":"generic",
                           "mandatory": "True",
                           "directives": [],
                           "hpa-feature-attributes":[
                              {
                                 "hpa-attribute-key":"pciVendorId",
                                 "hpa-attribute-value":"8086",
                                 "operator":"=",
                                 "unit":""
                              },
                              {
                                 "hpa-attribute-key":"pciDeviceId",
                                 "hpa-attribute-value":"0443",
                                 "operator":"=",
                                 "unit":""
                              },
                              {
                                 "hpa-attribute-key":"pciCount",
                                 "hpa-attribute-value":"1",
                                 "operator":"=",
                                 "unit":""
                              },
                           ]
                        }
                     ]
                  }
               ]
            }
         }
      }

VIM Fit
~~~~~~~

Constrain each demand's inventory candidates based on capacity check for
available capacity at the VIM instances.

Requirements are sent as an opaque request object understood by the VIM
controllers or MultiCloud. Each controller is defined and implemented as a
plugin in Conductor.

A vim controller plugin knows how to communicate with a particular endpoint
(via HTTP/REST, DMaaP, etc.), obtain necessary information, and make a
decision. The endpoint and credentials can be configured through plugin
settings.


**Schema**

+----------------+--------------------------------------------------------+
| Property       | Value                                                  |
+================+========================================================+
| ``controller`` | Name of a vim controller. (e.g., multicloud)           |
+----------------+--------------------------------------------------------+
| ``request``    | Opaque dictionary of key/value pairs. Values           |
|                | must be strings or numbers. Encoded and sent           |
|                | to the vim controller via a plugin.                    |
+----------------+--------------------------------------------------------+

.. code:: yaml

    constraints:
      check_cloud_capacity:
        type: vim_fit
        demands: [my_vnf_demand, my_other_vnf_demand]
        properties:
          controller: multicloud
          request: REQUEST_DICT

**Notes**

-  For the current release the REQUEST_DICT is of the following format as
   defined by the policy for vim_fit. The REQUEST_DICT is an opaque request
   object defined through policy, so it is not restricted to this format. In
   the current release MultiCloud supports the check_vim_capacity using the
   following grammar.

   .. code-block:: json

       {
         "request":{
           "vCPU":10,
           "Memory":{
             "quantity":{
               "get_param":"REQUIRED_MEM"
             },
             "unit":"GB"
           },
           "Storage":{
             "quantity":{
               "get_param":"REQUIRED_DISK"
             },
             "unit":"GB"
           }
         }
       }

Inventory Group
~~~~~~~~~~~~~~~

Constrain demands such that inventory items are grouped across two
demands.

This constraint has no properties.

.. code:: yaml

    constraints:
      my_group:
        type: inventory_group
        demands: [demand_1, demand_2]

*Note: Only pair-wise groups are supported at this time. The list must
have only two demands.*

License
~~~~~~~

Constrain demands according to license availability.

*Support for this constraint is deferred to a later release.*

**Schema**

+----------+----------------------------------------------------------+
| Property | Value                                                    |
+==========+==========================================================+
| ``id``   | Unique license identifier                                |
+----------+----------------------------------------------------------+
| ``key``  | Opaque license key, particular to the license identifier |
+----------+----------------------------------------------------------+

.. code:: yaml

    constraints:
      my_software:
        type: license
        demands: [demand_1, demand_2, ...]
        properties:
          id: SOFTWARE_ID
          key: LICENSE_KEY

Network Between Demands
~~~~~~~~~~~~~~~~~~~~~~~

Constrain each pairwise combination of two or more demands by network
requirements.

*Support for this constraint is deferred to a later release.*

**Schema**

+-------------------+--------------------------------------------------+
| Property          | Value                                            |
+===================+==================================================+
| ``bandwidth``     | Desired network bandwidth.                       |
| (Optional)        |                                                  |
+-------------------+--------------------------------------------------+
| ``distance``      | Desired distance between demands, measured by    |
| (Optional)        | the network path.                                |
+-------------------+--------------------------------------------------+
| ``latency``       | Desired network latency.                         |
| (Optional)        |                                                  |
+-------------------+--------------------------------------------------+

Any combination of ``bandwidth``, ``distance``, or ``latency`` must be
specified. If none of these properties are used, it is treated as a
malformed request.

The constraint is applied between each pairwise combination of demands.
For this reason, at least two demands must be specified, implicitly or
explicitly.

.. code:: yaml

    constraints:
      network_requirements:
        type: network_between_demands
        demands: [my_vnf_demand, my_other_vnf_demand]
        properties:
          bandwidth: >= 1000 Mbps
          distance: < 250 km
          latency: < 50 ms

Network To Location
~~~~~~~~~~~~~~~~~~~

Constrain one or more demands by network requirements relative to a
specific location.

*Support for this constraint is deferred to a later release.*

**Schema**

+-----------------------------------+-----------------------------------+
| Property                          | Value                             |
+===================================+===================================+
| ``bandwidth``                     | Desired network bandwidth.        |
+-----------------------------------+-----------------------------------+
| ``distance``                      | Desired distance between demands, |
|                                   | measured by the network path.     |
+-----------------------------------+-----------------------------------+
| ``latency``                       | Desired network latency.          |
+-----------------------------------+-----------------------------------+
| ``location``                      | A previously declared location.   |
+-----------------------------------+-----------------------------------+

Any combination of ``bandwidth``, ``distance``, or ``latency`` must be
specified. If none of these properties are used, it is treated as a
malformed request.

The constraint is applied between each demand and the referenced
location, not across all pairwise combinations of Demands.

.. code:: yaml

    constraints:
      my_access_network_constraint:
        type: network_to_location
        demands: [my_vnf_demand, my_other_vnf_demand]
        properties:
          bandwidth: >= 1000 Mbps
          distance: < 250 km
          latency: < 50 ms
          location: LOCATION_ID

Capabilities
~~~~~~~~~~~~

Constrain each demand by its cluster capability requirements. For
example, as described by an OpenStack Heat template and operational
environment.

*Support for this constraint is deferred to a later release.*

**Schema**

+-------------------+---------------------------------------------------------+
| Property          | Value                                                   |
+===================+=========================================================+
| ``specification`` | Indicates the kind of specification being provided in   |
|                   | the properties. Must be ``heat``. Future values may     |
|                   | include ``tosca``, ``Homing``, etc.                     |
+-------------------+---------------------------------------------------------+
| ``template``      | For specifications of type ``heat``, a single stack in  |
|                   | OpenStack Heat Orchestration Template (HOT) format.     |
|                   | Stacks may be expressed as a URI reference or a string  |
|                   | of well-formed YAML/JSON. Templates are validated by    |
|                   | the Heat service configured for use by HAS. Nested      |
|                   | stack references are unsupported.                       |
+-------------------+---------------------------------------------------------+
| ``environment``   | For specifications of type ``heat``, an optional Heat   |
|                   | environment. Environments may be expressed as a URI     |
| (Optional)        | reference or a string of well-formed YAML/JSON.         |
|                   | Environments are validated by the Heat service          |
|                   | configured for use by Homing.                           |
+-------------------+---------------------------------------------------------+

.. code:: yaml

    constraints:
      check_for_fit:
        type: capability
        demands: [my_vnf_demand, my_other_vnf_demand]
        properties:
          specification: heat
          template: http://repository/my/stack_template
          environment: http://repository/my/stack_environment

Threshold
~~~~~~~~~

Constrain each demand by an attribute which is within a certain
threshold.

**Schema**

+---------------+--------------------------------------------------------+
| Property      | Value                                                  |
+===============+========================================================+
| ``evaluate``  | List of  attributes and its threshold                  |
+---------------+--------------------------------------------------------+

+-------------------------+------------------------------------------+
| Property for evaluation | Value                                    |
+=========================+==========================================+
| ``attribute``           | Attribute of a candidate                 |
+-------------------------+------------------------------------------+
| ``threshold``           | Threshold Value                          |
+-------------------------+------------------------------------------+
| ``operator``            | Condition to check. Supported Values are |
|                         | ``gte``, ``lte``, ``lt``, ``gt``, ``eq`` |
+-------------------------+------------------------------------------+
| ``unit`` (optional)     | Attribute's unit of measurement          |
+-------------------------+------------------------------------------+

.. code:: yaml

    urllc_threshold:
      type: threshold
      demands: ['URLLC']
      properties:
        evaluate:
        - attribute: latency
          operator: lte
          threshold: 50
          unit: ms
        - attribute: reliability
          operator: gte
          threshold: 99.99

**Note:**

- The status of the constraint support is of Frankfurt release.

Reservations
------------

A **Reservation** allows reservation of resources associated with
candidate that satisfies one or more demands.

Similar to the *instance_fit* constraint, requirements are sent as a
request to a **service controller** that handles the reservation.
Service controllers are defined by plugins in Homing (e.g., ``sdn-c``).

The service controller plugin knows how to make a reservation (and
initiate rollback on a failure) with a particular endpoint (via
HTTP/REST, DMaaP, etc.) of the service controller. The endpoint and
credentials can be configured through plugin settings.

**Schema**

+---------------------+------------------------------------------------+
| Property            | Description                                    |
+=====================+================================================+
| ``controller``      | Name of a service controller.                  |
+---------------------+------------------------------------------------+
| ``request``         | Opaque dictionary of key/value pairs. Values   |
|                     | must be strings or numbers. Encoded and sent   |
|                     | to the service provider via a plugin.          |
+---------------------+------------------------------------------------+

.. code:: yaml

    resource_reservation:
      type: instance_reservation
      demands: [my_vnf_demand, my_other_vnf_demand]
      properties:
        controller: sdn-c
        request: REQUEST_DICT

Optimizations
-------------

An **Optimization** allows specification of a objective function, which
aims to maximize or minimize a certain value that varies based on the
choice of candidates for one or more demands that are a part of the
objective function. For example, an objective function may be to find
the *closest* cloud-region to a customer to home a demand.

Optimization Components
~~~~~~~~~~~~~~~~~~~~~~~

Optimization definitions can be broken down into three components:

+-------+----------------+--------------------------------------------+
| Compo | Key            | Value                                      |
| nent  |                |                                            |
+=======+================+============================================+
| Goal  | ``minimize``   | A single Operand (usually ``sum``) or      |
|       |                | Function                                   |
+-------+----------------+--------------------------------------------+
| Opera | ``sum``,       | Two or more Operands (Numbers, Operators,  |
| tor   | ``product``    | Functions)                                 |
+-------+----------------+--------------------------------------------+
| Funct | ``distance_bet | A two-element list consisting of a         |
| ion   | ween``         | location and demand.                       |
+-------+----------------+--------------------------------------------+

.. _example-1:

Example
~~~~~~~

Given a customer location ``cl``, two demands ``vG1`` and ``vG2``, and
weights ``w1`` and ``w2``, the optimization criteria can be expressed
as:

``minimize(weight1 * distance_between(cl, vG1) + weight2 * distance_between(cl, vG2))``

This can be read as: “Minimize the sum of weighted distances from cl to
vG1 and from cl to vG2.”

Such optimizations may be expressed in a template as follows:

.. code:: yaml

    parameters:
      w1: 10
      w2: 20

    optimization:
      minimize:
        sum:
        - product:
          - {get_param: w1}
          - {distance_between: [cl, vG1]}
        - product:
          - {get_param: w2}
          - {distance_between: [cl, vG2]}

Or without the weights as:

.. code:: yaml

    optimization:
      minimize:
        sum:
        - {distance_between: [cl, vG1]}
        - {distance_between: [cl, vG2]}

**Template Restriction**

While the template format supports any number of arrangements of
numbers, operators, and functions, HAS’s solver presently expects a very
specific arrangement.

-  Optimizations must conform to a single goal of ``minimize`` followed
   by a ``sum`` operator.
-  The sum can consist of two ``distance_between`` function calls, or
   two ``product`` operators.
-  If a ``product`` operator is present, it must contain at least a
   ``distance_between`` function call, plus one optional number to be
   used for weighting.
-  Numbers may be referenced via ``get_param``.
-  The objective function has to be written in the sum-of-product
   format. In the future, HAS can convert product-of-sum into
   sum-of-product automatically.

The first two examples in this section illustrate both of these use
cases.

**Inline Operations**

If desired, operations can be rewritten inline. For example, the two
``product`` operations from the previous example can also be expressed
as:

.. code:: yaml

    parameters:
      w1: 10
      w2: 20

    optimization:
      minimize:
        sum:
        - {product: [{get_param: w1}, {distance_between: [cl, vG1]}]}
        - {product: [{get_param: w2}, {distance_between: [cl, vG2]}]}

In turn, even the ``sum`` operation can be rewritten inline, however
there is a point of diminishing returns in terms of readability!

**Notes**

-  We do not support more than one dimension in the optimization
   (e.g., Minimize distance and cost). For supporting multiple
   dimensions we would need a function the normalize the unit across
   dimensions.

Intrinsic Functions
-------------------

Homing provides a set of intrinsic functions that can be used inside
templates to perform specific tasks. The following section describes the
role and syntax of the intrinsic functions.

Functions are written as a dictionary with one key/value pair. The key
is the function name. The value is a list of arguments. If only one
argument is provided, a string may be used instead.

.. code:: yaml

    a_property: {FUNCTION_NAME: [ARGUMENT_LIST]}

    a_property: {FUNCTION_NAME: ARGUMENT_STRING}

*Note: These functions can only be used within “properties” sections.*

get_file
~~~~~~~~

The ``get_file`` function inserts the content of a file into the
template. It is generally used as a file inclusion mechanism for files
containing templates from other services (e.g., Heat).

The syntax of the ``get_file`` function is:

.. code:: yaml

    {get_file: <content key>}

The ``content`` key is used to look up the ``files`` dictionary that is
provided in the REST API call. The Homing client command (``Homing``) is
``get_file`` aware and populates the ``files`` dictionary with the
actual content of fetched paths and URLs. The Homing client command
supports relative paths and transforms these to the absolute URLs
required by the Homing API.

**Note**: The ``get_file`` argument must be a static path or URL and not
rely on intrinsic functions like ``get_param``. The Homing client does
not process intrinsic functions. They are only processed by the Homing
engine.

The example below demonstrates the ``get_file`` function usage with both
relative and absolute URLs:

.. code:: yaml

    constraints:
      check_for_fit:
        type: capacity
        demands: [my_vnf_demand, my_other_vnf_demand]
        properties:
          template: {get_file: stack_template.yaml}
          environment: {get_file: http://hostname/environment.yaml}

The ``files`` dictionary generated by the Homing client during
instantiation of the plan would contain the following keys. Each value
would be of that file’s contents.

-  ``file:///path/to/stack_template.yaml``
-  ``http://hostname/environment.yaml``

**Note**

-  If Homing will only be accessed over DMaaP, files will need to be
   embedded using the Homing API request format. This will be a
   consideration when DMaaP integration happens.

get_param
~~~~~~~~~

The ``get_param`` function references an input parameter of a template.
It resolves to the value provided for this input parameter at runtime.

The syntax of the ``get_param`` function is:

.. code:: yaml

    {get_param: <parameter name>}

    {get_param: [<parameter name>, <key/index1> (optional), <key/index2> (optional), ...]}

**parameter name** is the parameter name to be resolved. If the
parameters returns a complex data structure such as a list or a dict,
then subsequent keys or indices can be specified. These additional
parameters are used to navigate the data structure to return the desired
value. Indices are zero-based.

The following example demonstrates how the ``get_param`` function is
used:

.. code:: yaml

    parameters:
      software_id: SOFTWARE_ID
      license_key: LICENSE_KEY
      service_info:
        provider: dmaap:///full.topic.name
        costs: [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    constraints:
      my_software:
        type: license
        demands: [demand_1, demand_2, ...]
        properties:
          id: {get_param: software_id}
          key: {get_param: license_key}

      check_for_availability:
        type: service
        demands: [my_vnf_demand, my_other_vnf_demand]
        properties:
          provider_url: {get_param: [service_info, provider]}
          request: REQUEST_DICT
          cost: {get_param: [service_info, costs, 4]}

In this example, properties would be set as follows:

+------------------+--------------------------+
| Key              | Value                    |
+==================+==========================+
| ``id``           | SOFTWARE_ID              |
+------------------+--------------------------+
| ``key``          | LICENSE_KEY              |
+------------------+--------------------------+
| ``provider_url`` | dmaap:///full.topic.name |
+------------------+--------------------------+
| ``cost``         | 50                       |
+------------------+--------------------------+

Contact
-------

Shankar Narayanan shankarpnsn@gmail.com
