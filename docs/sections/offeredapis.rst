.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. _offeredapis:

Offered APIs
=============================================

This document describes the Homing API, provided by the Homing and Allocation service (Conductor).


To view API documentation in the interactive swagger UI download the following and
paste into the swagger tool here: https://editor.swagger.io

:download:`oof-has-api.json <./swaggerdoc/oof-has-api.json>`

.. swaggerv2doc:: ./swaggerdoc/oof-has-api.json

State Diagram
^^^^^^^^^^^^^

.. code:: text

                      ----------------------------------------
                     |                                        |
                     |                   /---> solved ---> reserving ---> done
                     |                  /                    /
     template -> translated -> solving ------> not found    /
         |         ^               |    \                  / 
         |         | conditionally |     \---> error <----/
         |         |   (see note)  |             ^
         |         \---------------/             |
         \---------------------------------------/

**NOTE**: When Conductor's solver service is started in non-concurrent
mode (the default), it will reset any plans found waiting and stuck in
the ``solving`` state back to ``translated``.

.. code::

    {
      "name": "PLAN_NAME",
      "template": "CONDUCTOR_TEMPLATE",
      "limit": 3
    }

.. code::

    {
      "plan": {
        "name": "PLAN_NAME",
        "id": "ee1c5269-c7f0-492a-8652-f0ceb15ed3bc",
        "transaction_id": "6bca5f2b-ee7e-4637-8b58-1b4b36ed10f9",
        "status": "solved",
        "message", "Plan PLAN_NAME is solved.",
        "links": [
          {
            "href": "http://homing/v1/plans/ee1c5269-c7f0-492a-8652-f0ceb15ed3bc",
            "rel": "self"
          }
        ],
        "recommendations": [
          {
            "DEMAND_NAME_1": {
              "inventory_provider": "aai",
              "service_resource_id": "4feb0545-69e2-424c-b3c4-b270e5f2a15d",
              "candidate": {
                "candidate_id": "99befee8-e8c0-425b-8f36-fb7a8098d9a9",
                "inventory_type": "service",
                "location_type": "aic",
                "location_id": "dal01",
                "host_id" : "vig20002vm001vig001"
              },
              "attributes": {OPAQUE-DICT}
            },
            "DEMAND_NAME_2": {
              "inventory_provider": "aai",
              "service_resource_id": "578eb063-b24a-4654-ba9e-1e5cf7eb9183",
              "candidate": {
                "inventory_type": "cloud",
                "location_type": "aic",
                "location_id": "dal02"
              },
              "attributes": {OPAQUE-DICT}
            }
          },
          {
            "DEMAND_NAME_1": {
              "inventory_provider": "aai",
              "service_resource_id": "4feb0545-69e2-424c-b3c4-b270e5f2a15d",
              "candidate": {
                "candidate_id": "99befee8-e8c0-425b-8f36-fb7a8098d9a9",
                "inventory_type": "service",
                "location_type": "aic",
                "location_id": "dal03",
                "host_id" : "vig20001vm001vig001"
              },
              "attributes": {OPAQUE-DICT}
            },
            "DEMAND_NAME_2": {
              "inventory_provider": "aai",
              "service_resource_id": "578eb063-b24a-4654-ba9e-1e5cf7eb9183",
              "candidate": {
                "inventory_type": "cloud",
                "location_type": "aic",
                "location_id": "dal04"
              },
              "attributes": {OPAQUE-DICT}
            }
          },
          ...
        ]
      }
    }

Show plan details
-----------------

**GET** ``/v1/plans/{plan_id}``

-  **Normal response codes:** 200
-  **Error response codes:** unauthorized (401), itemNotFound (404)

Request parameters
~~~~~~~~~~~~~~~~~~

+---------------+---------+--------------+-------------------------+
| Parameter     | Style   | Type         | Description             |
+===============+=========+==============+=========================+
| ``plan_id``   | plain   | csapi:UUID   | The UUID of the plan.   |
+---------------+---------+--------------+-------------------------+

Response Parameters
~~~~~~~~~~~~~~~~~~~

See the Response Parameters for **Create a plan**.

Delete a plan
-------------

**DELETE** ``/v1/plans/{plan_id}``

-  **Normal response codes:** 204
-  **Error response codes:** badRequest (400), unauthorized (401),
   itemNotFound (404)

Request parameters
~~~~~~~~~~~~~~~~~~

+---------------+---------+--------------+-------------------------+
| Parameter     | Style   | Type         | Description             |
+===============+=========+==============+=========================+
| ``plan_id``   | plain   | csapi:UUID   | The UUID of the plan.   |
+---------------+---------+--------------+-------------------------+

This operation does not accept a request body and does not return a
response body.

API Errors
----------

In the event of an error with a status other than unauthorized (401), a
detailed repsonse body is returned.

Response parameters
~~~~~~~~~~~~~~~~~~~

+-----------------+--------+------------+---------------------------------------------+
| Parameter       | Style  | Type       | Description                                 |
+=================+========+============+=============================================+
| ``title``       | plain  | xsd:string | Human-readable name.                        |
+-----------------+--------+------------+---------------------------------------------+
| ``explanation`` | plain  | xsd:string | Detailed explanation with remediation (if   |
|                 |        |            | any).                                       |
+-----------------+--------+------------+---------------------------------------------+
| ``code``        | plain  | xsd:int    | HTTP Status Code.                           |
+-----------------+--------+------------+---------------------------------------------+
| ``error``       | plain  | xsd:dict   | Error dictionary. Keys include **message**, |
|                 |        |            | **traceback**, and **type**.                |
+-----------------+--------+------------+---------------------------------------------+
| ``message``     | plain  | xsd:string | Internal error message.                     |
+-----------------+--------+------------+---------------------------------------------+
| ``traceback``   | plain  | xsd:string | Python traceback (if available).            |
|                 |        |            |                                             |
+-----------------+--------+------------+---------------------------------------------+
| ``type``        | plain  | xsd:string | HTTP Status class name (from python-webob)  |
+-----------------+--------+------------+---------------------------------------------+

Examples
^^^^^^^^

A plan with the name "pl an" is considered a bad request because the
name contains a space.

.. code:: json

    {
      "title": "Bad Request",
      "explanation": "-> name -> pl an did not pass validation against callable: plan_name_type (must contain only uppercase and lowercase letters, decimal digits, hyphens, periods, underscores, and tildes [RFC 3986, Section 2.3])",
      "code": 400,
      "error": {
        "message": "The server could not comply with the request since it is either malformed or otherwise incorrect.",
        "type": "HTTPBadRequest"
      }
    }

The HTTP COPY method was attempted but is not allowed.

.. code:: json

    {
      "title": "Method Not Allowed",
      "explanation": "The COPY method is not allowed.",
      "code": 405,
      "error": {
        "message": "The server could not comply with the request since it is either malformed or otherwise incorrect.",
        "type": "HTTPMethodNotAllowed"
      }
    }
