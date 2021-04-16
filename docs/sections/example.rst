Example Conductor Templates
===========================

Example 1
---------

.. code:: json

    {
      "name": "yyy-yyy-yyyy",
      "files": {},
      "timeout": 600,
      "limit": 1,
      "num_solutions": 10,
      "template": {
        "homing_template_version": "2018-02-01",
        "parameters": {
          "service_name": "",
          "service_id": "d61b2543-5914-4b8f-8e81-81e38575b8ec",
          "customer_lat": 32.89748,
          "customer_long": -97.040443
        },
        "locations": {
          "customer_loc": {
            "latitude": {
              "get_param": "customer_lat"
            },
            "longitude": {
              "get_param": "customer_long"
            }
          }
        },
        "demands": {
          "vGMuxInfra": [
            {
              "inventory_provider": "aai",
              "inventory_type": "service",
              "service_type": "vGMuxInfra-xx",
              "attributes": {
                "customer-id": "",
                "orchestration-status": "",
                "model-invariant-id": "b3dc6465-942c-42af-8464-2bf85b6e504b",
                "model-version-id": "ba3b8981-9a9c-4945-92aa-486234ec321f",
                "service-type": "vGMuxInfra-xx",
                "equipment-role": "",
                "global-customer-id": "SDN-ETHERNET-INTERNET"
              }
            }
          ],
          "vG": [
            {
              "inventory_provider": "aai",
              "inventory_type": "cloud",
              "service_type": "71d563e8-e714-4393-8f99-cc480144a05e"
            }
          ]
        },
        "constraints": {
          "affinity_vCPE": {
            "type": "zone",
            "demands": [
              "vGMuxInfra",
              "vG"
            ],
            "properties": {
              "category": "complex",
              "qualifier": "same"
            }
          }
        },
        "optimization": {
          "minimize": {
            "sum": [
              {
                "product": [
                  "1",
                  {
                    "distance_between": [
                      "customer_loc",
                      "vGMuxInfra"
                    ]
                  }
                ]
              },
              {
                "product": [
                  "1",
                  {
                    "distance_between": [
                      "customer_loc",
                      "vG"
                    ]
                  }
                ]
              }
            ]
          }
        }
      }
    }

The example template is for the placement of vG and vGMuxInfra. It has
an affinity constraint which specifies that both the vnfs must be in
the same complex. The optimiation here is to minimize the sum of the
distances of the vnfs from the customer location.

Example 2
---------

.. code:: json

    {
      "files": {},
      "limit": 1,
      "num_solutions": 10,
      "name": "a2e3e0cc-3a97-44fc-8a08-1b86143fbdd3",
      "template": {
        "constraints": {
          "affinity_vCPE": {
            "demands": [
              "vgMuxAR",
              "vGW"
            ],
            "properties": {
              "category": "complex",
              "qualifier": "same"
            },
            "type": "zone"
          },
          "distance-vGMuxAR": {
            "demands": [
              "vgMuxAR"
            ],
            "properties": {
              "distance": "< 500 km",
              "location": "customer_loc"
            },
            "type": "distance_to_location"
          },
          "distance-vGW": {
            "demands": [
              "vGW"
            ],
            "properties": {
              "distance": "< 1500 km",
              "location": "customer_loc"
            },
            "type": "distance_to_location"
          }
        },
        "demands": {
          "vGW": [
            {
              "attributes": {
                "model-invariant-id": "782c87a6-b712-47d1-9c5b-1ea2cd9a2dd5",
                "model-version-id": "9877dbbe-8ada-40a2-8adb-f6f26f1ad9ab"
              },
              "inventory_provider": "aai",
              "inventory_type": "cloud",
              "service_type": "c3e0e82b-3367-48ce-ab00-27dc2e91a34a"
            }
          ],
          "vgMuxAR": [
            {
              "attributes": {
                "global-customer-id": "SDN-ETHERNET-INTERNET",
                "model-invariant-id": "565d5b75-11b8-41be-9991-ee03a0049159",
                "model-version-id": "61414c6c-6082-4e03-9824-bf53c3582b78"
              },
              "inventory_provider": "aai",
              "inventory_type": "service",
              "service_type": "46b29078-8442-4ea3-bea6-9199a7d514d4"
            }
          ]
        },
        "homing_template_version": "2017-10-10",
        "locations": {
          "customer_loc": {
            "latitude": {
              "get_param": "customer_lat"
            },
            "longitude": {
              "get_param": "customer_long"
            }
          }
        },
        "optimization": {
          "minimize": {
            "sum": [
              {
                "product": [
                  "1",
                  {
                    "distance_between": [
                      "customer_loc",
                      "vgMuxAR"
                    ]
                  }
                ]
              },
              {
                "product": [
                  "1",
                  {
                    "distance_between": [
                      "customer_loc",
                      "vGW"
                    ]
                  }
                ]
              }
            ]
          }
        },
        "parameters": {
          "customer_lat": 32.89748,
          "customer_long": 97.040443,
          "service_id": "0dbb9d5f-27d9-429b-bc36-293e9fab7731",
          "service_name": ""
        }
      },
      "timeout": 600
    }

This is similar to the first example except that it has an additional distance
constraint which specifies that the distance of each vnf from the customer
location must be less than 500km.

Example 3
---------

.. code:: json

    {
        "files": {},
        "limit": 10,
        "name": "urllc_sample",
        "num_solution": "10",
        "template": {
            "constraints": {
                "URLLC_core_Threshold": {
                    "demands": [
                        "URLLC_core"
                    ],
                    "properties": {
                        "evaluate": [
                            {
                                "attribute": "latency",
                                "operator": "lte",
                                "threshold": 30,
                                "unit": "ms"
                            }
                        ]
                    },
                    "type": "threshold"
                },
                "URLLC_ran_Threshold": {
                    "demands": [
                        "URLLC_ran"
                    ],
                    "properties": {
                        "evaluate": [
                            {
                                "attribute": "latency",
                                "operator": "lte",
                                "threshold": 30,
                                "unit": "ms"
                            }
                        ]
                    },
                    "type": "threshold"
                }
            },
            "demands": {
                "URLLC_core": [
                    {
                        "filtering_attributes": {
                            "model-invariant-id": "21d57d4b-52ad-4d3c-a798-248b5bb9124a",
                            "model-version-id": "bfba363e-e39c-4bd9-a9d5-1371c28f4d22",
                            "orchestration-status": "active",
                            "service-role": "nssi"
                        },
                        "inventory_provider": "aai",
                        "inventory_type": "nssi",
                        "region": "RegionOne",
                        "unique": "true"
                    }
                ],
                "URLLC_ran": [
                    {
                        "filtering_attributes": {
                            "model-invariant-id": "aa2d56ea-773d-11ea-bc55-0242ac130003",
                            "model-version-id": "d6296806-773d-11ea-bc55-0242ac130003",
                            "orchestration-status": "active",
                            "service-role": "nssi"
                        },
                        "inventory_provider": "aai",
                        "inventory_type": "nssi",
                        "region": "RegionOne",
                        "unique": "true"
                    }
                ]
            },
            "homing_template_version": "2018-02-01"
        },
        "timeout": 1200
    }

This template is for the selecting the NSSI instances for Network
Slicing use case. The demand here is the Slice subnets and the threshold
constraint specifies that the latency of the the subnets must be less
than a particular threshold.


Example 4
---------

.. code:: json

	{
		"name":"urllc_sample",
		"files":{
 
		},
		"limit":10,
		"num_solution":"1",
		"timeout":1200,
		"template":{
			"homing_template_version":"2020-08-13",
			"demands":{
			"nst_demand":[
				{
               "inventory_provider":"aai",
               "inventory_type":"nst",
               "unique":"true",
               "region":"RegionOne",
               "filtering_attributes":{
                  "model-role":"nst"
					}
				}
			]
		},
		"constraints":{
			"nst_Threshold":{
            "type":"threshold",
            "demands":[
               "nst_demand"
            ],
            "properties":{
               "evaluate":[
                  {
                     "attribute":"latency",
                     "operator":"lte",
                     "threshold":30,
                     "unit":"ms"
                  }
               ]
             }
           }
	    },
		"optimization":{
			"goal": "minimize",
			"operation_function": {
				"operator": "sum",
				"operands": [{
				"function": "attribute",
				"params": {
                  "demand": "nst_demand",
                  "attribute": "latency"
				}
				}]
			}
	    }
	  }
	}

This template is for the selecting the NST templates for Network
Slicing use case. The demand here is the slice templates and the threshold
constraint specifies that the latency of the the templates must be less
than a particular threshold.

Contact
-------

Shankar Narayanan shankarpnsn@gmail.com
