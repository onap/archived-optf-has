# Example Conductor Templates

*Updated: 10 Oct 2017*

## Example 1

```yaml

# Homing Specification Version
homing_template_version: 2017-10-10

# Runtime order Parameters
parameters:
  service_name: Residential vCPE
  service_id: vcpe_service_id
  customer_lat: 32.897480
  customer_long: -97.040443

# List of geographical locations
locations:
  customer_loc:
    latitude: {get_param: customer_lat}
    longitude: {get_param: customer_long}

# List of VNFs (demands) to be homed
demands:
  vGMuxInfra:
  - inventory_provider: aai
    inventory_type: service
    attributes:
      equipment_type: vG_Mux
      customer_id: some_company
    excluded_candidates:
      - candidate_id:
        1ac71fb8-ad43-4e16-9459-c3f372b8236d
    existing_placement:
        - candidate_id: 21d5f3e8-e714-4383-8f99-cc480144505a
  vG:
  - inventory_provider: aai
    inventory_type: service
    attributes:
      equipment_type: vG
      modelId: vG_model_id
      customer_id: some_company
    excluded_candidates:
      - candidate_id: 1ac71fb8-ad43-4e16-9459-c3f372b8236d
    existing_placement:
      - candidate_id: 21d5f3e8-e714-4383-8f99-cc480144505a
  - inventory_provider: aai
    inventory_type: cloud

# List of homing policies (constraints)
constraints:
    # distance constraint
    - constraint_vgmux_customer:
      	type: distance_to_location
        demands: [vGMuxInfra]
        properties:
        	distance: < 100 km
          location: customer_loc
    # cloud region co-location constraint
    - colocation:
    		type: zone
        demands: [vGMuxInfra, vG]
        properties:
        	qualifier: same
          category: region
    # platform capability constraint
    - numa_cpu_pin_capabilities:
    		type: attribute
        demands: [vG]
        properties:
        	evaluate:
            vcpu_pinning: True
            numa_topology: numa_spanning
    # cloud provider constraint
    - cloud_version_capabilities:
    		type: attribute
        demands: [vGMuxInfra]
        properties:
        	evaluate:
          	cloud_version: 1.11.84
            cloud_provider: AWS

# Objective function to minimize
optimization:
  minimize:
    sum:
    - {distance_between: [customer_loc, vGMuxInfra]}
    - {distance_between: [customer_loc, vG]}

```

## Contact ##

Shankar Narayanan <shankarpnsn@gmail.com>
