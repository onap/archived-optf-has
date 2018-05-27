.. This work is licensed under a Creative Commons Attribution 4.0 International License.

Offered APIs
=============================================

.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. Copyright (C) 2017-2018 AT&T Intellectual Property. All rights reserved.

Homing API v1
------------------

*Updated: 28 Feb 2018*

This document describes the Homing API, provided by the Homing and Allocation service (Conductor).
It is a work in progress and subject to frequent revision.

General API Information
-------------------------

Authenticated calls that target a known URI but that use an HTTP method
the implementation does not support return a 405 Method Not Allowed
status. In addition, the HTTP OPTIONS method is supported for each known
URI. In both cases, the Allow response header indicates the supported
HTTP methods. See the API Errors section for more information about the
error response structure.

API versions
------------------

List all Homing API versions
----------------------------

**GET** ``/``\ F

**Normal response codes:** 200

.. code:: json

    {
      "versions": [
        {
          "status": "EXPERIMENTAL",
          "id": "v1",
          "updated": "2016-11-01T00:00:00Z",
          "media-types": [
            {
              "base": "application/json",
              "type": "application/vnd.onap.homing-v1+json"
            }
          ],
          "links": [
            {
              "href": "http://has.ip/v1",
              "rel": "self"
            },
            {
              "href": "http://has.url/",
              "type": "text/html",
              "rel": "describedby"
            }
          ]
        }
      ]
    }

This operation does not accept a request body.

Plans
------------------

Create a plan
-------------

**POST** ``/v1/plans``

-  **Normal response codes:** 201
-  **Error response codes:** badRequest (400), unauthorized (401),
   internalServerError (500)

Request an inventory plan for one or more related service demands.

The request includes or references a declarative **template**,
consisting of:

-  **Parameters** that can be referenced like macros
-  **Demands** for service made against inventory
-  **Locations** that are common to the overall plan
-  **Constraints** made against demands, resulting in a set of inventory
   candidates
-  **Optimizations** to further narrow down the remaining candidates

The response contains an inventory **plan**, consisting of one or more
sets of recommended pairings of demands with an inventory candidate’s
attributes and region.

Request Parameters
~~~~~~~~~~~~~~~~~~

+--------------------+------------+----------+------------------------+
| Parameter          | Style      | Type     | Description            |
+====================+============+==========+========================+
| ``name``           | plain      | xsd:stri | A name for the new     |
| (Optional)         |            | ng       | plan. If a name is not |
|                    |            |          | provided, it will be   |
|                    |            |          | auto-generated based   |
|                    |            |          | on the homing          |
|                    |            |          | template. This name    |
|                    |            |          | must be unique within  |
|                    |            |          | a given Conductor      |
|                    |            |          | environment. When      |
|                    |            |          | deleting a plan, its   |
|                    |            |          | name will not become   |
|                    |            |          | available for reuse    |
|                    |            |          | until the deletion     |
|                    |            |          | completes              |
|                    |            |          | successfully. Must     |
|                    |            |          | only contain letters,  |
|                    |            |          | numbers, hypens, full  |
|                    |            |          | stops, underscores,    |
|                    |            |          | and tildes (RFC 3986,  |
|                    |            |          | Section 2.3). This     |
|                    |            |          | parameter is           |
|                    |            |          | immutable.             |
+--------------------+------------+----------+------------------------+
| ``id`` (Optional)  | plain      | csapi:UU | The UUID of the plan.  |
|                    |            | ID       | UUID is assigned by    |
|                    |            |          | Conductor if no id is  |
|                    |            |          | provided in the        |
|                    |            |          | request.               |
+--------------------+------------+----------+------------------------+
| ``transaction_id`` | plain      | csapi:UU | The transaction id     |
|                    |            | ID       | assigned by SO. The    |
|                    |            |          | logs should have this  |
|                    |            |          | transaction id for     |
|                    |            |          | tracking purposes.     |
+--------------------+------------+----------+------------------------+
| ``files``          | plain      | xsd:dict | Supplies the contents  |
| (Optional)         |            |          | of files referenced.   |
+--------------------+------------+----------+------------------------+