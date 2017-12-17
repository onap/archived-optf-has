# Homing API v1

*Updated: 4 April 2017*

This document describes the Homing API, used by the Conductor service. It is a work in progress and subject to frequent revision.

# General API Information

Authenticated calls that target a known URI but that use an HTTP method the implementation does not support return a 405 Method Not Allowed status. In addition, the HTTP OPTIONS method is supported for each known URI. In both cases, the Allow response header indicates the supported HTTP methods. See the API Errors section for more information about the error response structure.

# API versions

## List all Homing API versions

**GET** ``/``F

**Normal response codes:** 200

```json
{
  "versions": [
    {
      "status": "EXPERIMENTAL",
      "id": "v1",
      "updated": "2016-11-01T00:00:00Z",
      "media-types": [
        {
          "base": "application/json",
          "type": "application/vnd.ecomp.homing-v1+json"
        }
      ],
      "links": [
        {
          "href": "http://135.197.226.83:8091/v1",
          "rel": "self"
        },
        {
          "href": "http://conductor.research.att.com/",
          "type": "text/html",
          "rel": "describedby"
        }
      ]
    }
  ]
}
```

This operation does not accept a request body.

# Plans

## Create a plan

**POST** ``/v1/plans``

* **Normal response codes:** 201
* **Error response codes:** badRequest (400), unauthorized (401), internalServerError (500)

Request an inventory plan for one or more related service demands.

The request includes or references a declarative **template**, consisting of:

* **Parameters** that can be referenced like macros
* **Demands** for service made against inventory
* **Locations** that are common to the overall plan
* **Constraints** made against demands, resulting in a set of inventory candidates
* **Optimizations** to further narrow down the remaining candidates

The response contains an inventory **plan**, consisting of one or more sets of recommended pairings of demands with an inventory candidate's attributes and region.

### Request Parameters

| Parameter | Style | Type | Description |
|-----------|-------|------|-------------|
| ``name`` (Optional) | plain | xsd:string | A name for the new plan. If a name is not provided, it will be auto-generated based on the homing template. This name must be unique within a given Conductor environment. When deleting a plan, its name will not become available for reuse until the deletion completes successfully. Must only contain letters, numbers, hypens, full stops, underscores, and tildes (RFC 3986, Section 2.3). This parameter is immutable. |
| ``id`` (Optional) | plain | csapi:UUID | The UUID of the plan. UUID is assigned by Conductor if no id is provided in the request. |
| ``transaction_id`` | plain | csapi:UUID | The transaction id assigned by MSO. The logs should have this transaction id for tracking purposes. |
| ``files`` (Optional) | plain | xsd:dict | Supplies the contents of files referenced in the template. Conductor templates can explicitly reference files by using the ``get_file`` intrinsic function. The value is a JSON object, where each key is a relative or absolute URI which serves as the name of a file, and the associated value provides the contents of the file. Additionally, some template authors encode their user data in a local file. The Homing client (e.g., a CLI) can examine the template for the ``get_file`` intrinsic function (e.g., ``{get_file: file.yaml}``) and add an entry to the ``files`` map with the path to the file as the name and the file contents as the value. Do not use this parameter to provide the content of the template located at the ``template_url`` address. Instead, use the ``template`` parameter to supply the template content as part of the request. |
| ``template_url`` (Optional) | plain | xsd:string | A URI to the location containing the template on which to perform the operation. See the description of the ``template`` parameter for information about the expected template content located at the URI. This parameter is only required when you omit the ``template`` parameter. If you specify both parameters, this parameter is ignored. |
| ``template``| plain | xsd:string or xsd:dict | The template on which to perform the operation. See the [Conductor Template Guide](/doc/template/README.md) for complete information on the format. This parameter is either provided as a ``string`` or ``dict`` in the JSON request body. For ``string`` content it may be a JSON- or YAML-formatted Conductor template. For ``dict`` content it must be a direct JSON representation of the Conductor template. This parameter is required only when you omit the ``template_url`` parameter. If you specify both parameters, this value overrides the ``template_url`` parameter value. |
| ``timeout`` (Optional) | plain | xsd:number | The timeout for plan creation in minutes. Default is 1. |
| ``limit`` (Optional) | plain | xsd:number | The maximum number of recommendations to return. Default is 1. |

**NOTE**: ``files``, ``template_url``, and ``timeout`` are not yet supported.

### Response Parameters

| Parameter | Style | Type | Description |
|-----------|-------|------|-------------|
| ``plan`` | plain | xsd:dict | The ``plan`` object. |
| ``id`` | plain | csapi:UUID | The UUID of the plan. |
| ``transaction_id`` | plain | csapi:UUID | The transaction id assigned by the MSO. |
| ``name`` | plain | xsd:string | The plan name. |
| ``status`` | plain | xsd:string | The plan status. One of ``template``, ``translated``, ``solving``, ``solved``, or ``error``. See **Plan Status** table for descriptions of each value. |
| ``message`` | plain | xsd:string | Additional context, if any, around the message status. If the status is ``error``, this may include a reason and suggested remediation, if available. |
| ``links`` | plain | xsd:list | A list of URLs for the plan. Each URL is a JSON object with an ``href`` key indicating the URL and a ``rel`` key indicating its relationship to the plan in question. There may be multiple links returned. The ``self`` relationship identifies the URL of the plan itself. |
| ``recommendations`` | plain | xsd:list | A list of one or more recommendations. A recommendation pairs each requested demand with an inventory provider, a single candidate, and an opaque dictionary of attributes. Refer to the Demand candidate schema in the [Conductor Template Guide](/doc/template/README.md) for further details. (Note that, when ``inventory_type`` is ``cloud`` the candidate's ``candidate_id`` field is redundant and thus omitted.) |

### Plan Status

| Status | Description |
|--------|-------------|
| ``template`` | Plan request and homing template have been received. Awaiting translation. |
| ``translated`` | Homing template has been translated, and candidates have been obtained from inventory providers. Awaiting solving. |
| ``solving`` | Search for a solution is in progress. This may incorporate requests to service controllers for additional information. |
| ``solved`` | Search is complete. A solution with one or more recommendations was found. |
| ``not found`` | Search is complete. No recommendations were found. |
| ``error`` | An error was encountered. |

#### State Diagram

```text
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
```
**NOTE**: When Conductor's solver service is started in non-concurrent mode (the default), it will reset any plans found waiting and stuck in the ``solving`` state back to ``translated``.

```json
{
  "name": "PLAN_NAME",
  "template": "CONDUCTOR_TEMPLATE",
  "limit": 3
}
```

```json
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
```

## Show plan details

**GET** ``/v1/plans/{plan_id}``

* **Normal response codes:** 200
* **Error response codes:** unauthorized (401), itemNotFound (404)

### Request parameters

| Parameter   | Style | Type       | Description                                       |
|-------------|-------|------------|---------------------------------------------------|
| ``plan_id`` | plain | csapi:UUID | The UUID of the plan. |

### Response Parameters

See the Response Parameters for **Create a plan**.

## Delete a plan

**DELETE** ``/v1/plans/{plan_id}``

* **Normal response codes:** 204
* **Error response codes:** badRequest (400), unauthorized (401), itemNotFound (404)

### Request parameters

| Parameter   | Style | Type       | Description                                       |
|-------------|-------|------------|---------------------------------------------------|
| ``plan_id`` | plain | csapi:UUID | The UUID of the plan.  |

This operation does not accept a request body and does not return a response body.

## API Errors

In the event of an error with a status other than unauthorized (401), a detailed repsonse body is returned.

### Response parameters

| Parameter   | Style | Type       | Description                                       |
|-------------|-------|------------|---------------------------------------------------|
| ``title``   | plain | xsd:string | Human-readable name.                              |
| ``explanation`` | plain | xsd:string | Detailed explanation with remediation (if any).   |
| ``code``    | plain | xsd:int    | HTTP Status Code.                                 |
| ``error``   | plain | xsd:dict   | Error dictionary. Keys include **message**, **traceback**, and **type**. |
| ``message`` | plain | xsd:string | Internal error message.                           |
| ``traceback`` | plain | xsd:string | Python traceback (if available).                  |
| ``type``    | plain | xsd:string | HTTP Status class name (from python-webob)        |

#### Examples

A plan with the name "pl an" is considered a bad request because the name contains a space.

```json
{
  "title": "Bad Request",
  "explanation": "-> name -> pl an did not pass validation against callable: plan_name_type (must contain only uppercase and lowercase letters, decimal digits, hyphens, periods, underscores, and tildes [RFC 3986, Section 2.3])",
  "code": 400,
  "error": {
    "message": "The server could not comply with the request since it is either malformed or otherwise incorrect.",
    "type": "HTTPBadRequest"
  }
}
```

The HTTP COPY method was attempted but is not allowed.

```json
{
  "title": "Method Not Allowed",
  "explanation": "The COPY method is not allowed.",
  "code": 405,
  "error": {
    "message": "The server could not comply with the request since it is either malformed or otherwise incorrect.",
    "type": "HTTPMethodNotAllowed"
  }
}
```

## Contact ##

Shankar Narayanan <shankarpnsn@gmail.com>
