#
# -------------------------------------------------------------------------
#   Copyright (C) 2020 Wipro Limited.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# -------------------------------------------------------------------------
#

VERSIONS = {'BASE': ["2016-11-01", "2017-10-10", "2018-02-01"],
            'GENERIC': ["2020-08-13"]}
LOCATION_KEYS = ['latitude', 'longitude', 'host_name', 'clli_code']
INVENTORY_PROVIDERS = ['aai', 'generator', 'sdc']
INVENTORY_TYPES = ['cloud', 'service', 'transport', 'vfmodule', 'nssi', 'nsi', 'slice_profiles', 'nst']
DEFAULT_INVENTORY_PROVIDER = INVENTORY_PROVIDERS[0]
CANDIDATE_KEYS = ['candidate_id', 'cost', 'inventory_type', 'location_id',
                  'location_type']
DEMAND_KEYS = ['filtering_attributes', 'passthrough_attributes', 'default_attributes', 'candidates', 'complex',
               'conflict_identifier', 'customer_id', 'default_cost', 'excluded_candidates',
               'existing_placement', 'flavor', 'inventory_provider',
               'inventory_type', 'port_key', 'region', 'required_candidates',
               'service_id', 'service_resource_id', 'service_subscription',
               'service_type', 'subdivision', 'unique', 'vlan_key']
CONSTRAINT_KEYS = ['type', 'demands', 'properties']
CONSTRAINTS = {
    # constraint_type: {
    #   split: split into individual constraints, one per demand
    #   required: list of required property names,
    #   optional: list of optional property names,
    #   thresholds: dict of property/base-unit pairs for threshold parsing
    #   allowed: dict of keys and allowed values (if controlled vocab);
    #            only use this for Conductor-controlled values!
    # }
    'attribute': {
        'split': True,
        'required': ['evaluate'],
    },
    'threshold': {
        'split': True,
        'required': ['evaluate'],
    },
    'distance_between_demands': {
        'required': ['distance'],
        'thresholds': {
            'distance': 'distance'
        },
    },
    'distance_to_location': {
        'split': True,
        'required': ['distance', 'location'],
        'thresholds': {
            'distance': 'distance'
        },
    },
    'instance_fit': {
        'split': True,
        'required': ['controller'],
        'optional': ['request'],
    },
    'inventory_group': {},
    'region_fit': {
        'split': True,
        'required': ['controller'],
        'optional': ['request'],
    },
    'zone': {
        'required': ['qualifier', 'category'],
        'optional': ['location'],
        'allowed': {'qualifier': ['same', 'different'],
                    'category': ['disaster', 'region', 'complex', 'country',
                                 'time', 'maintenance']},
    },
    'vim_fit': {
        'split': True,
        'required': ['controller'],
        'optional': ['request'],
    },
    'hpa': {
        'split': True,
        'required': ['evaluate'],
    },
}
HPA_FEATURES = ['architecture', 'hpa-feature', 'hpa-feature-attributes',
                'hpa-version', 'mandatory', 'directives']
HPA_OPTIONAL = ['score']
HPA_ATTRIBUTES = ['hpa-attribute-key', 'hpa-attribute-value', 'operator']
HPA_ATTRIBUTES_OPTIONAL = ['unit']
OPTIMIZATION_FUNCTIONS = {'distance_between': ['demand', 'location'],
                          'latency_between': ['demand', 'location'],
                          'attribute': ['demand', 'attribute']}


class TranslatorException(Exception):
    pass
