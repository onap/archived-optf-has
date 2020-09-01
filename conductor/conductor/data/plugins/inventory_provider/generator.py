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

import itertools
import uuid

from oslo_log import log

from conductor.data.plugins.inventory_provider import base
from conductor.data.plugins.inventory_provider.candidates.candidate import Candidate
from conductor.data.plugins.inventory_provider.candidates.slice_profiles_candidate import SliceProfilesCandidate

LOG = log.getLogger(__name__)


class Generator(base.InventoryProviderBase):

    def __init__(self):
        """Initialize variables"""
        pass

    def name(self):
        """Return human-readable name."""
        return "generator"

    def resolve_demands(self, demands, plan_info, triage_translator_data):
        """Resolve demands into candidate list"""
        resolved_demands = {}
        for name, requirements in demands.items():
            resolved_demands[name] = []
            for requirement in requirements:
                inventory_type = requirement.get('inventory_type').lower()
                candidate_uniqueness = requirement.get('unique', 'true')
                filtering_attributes = requirement.get('filtering_attributes')
                resolved_demands[name].extend(self.generate_candidates(inventory_type,
                                                                       filtering_attributes,
                                                                       candidate_uniqueness))

        return resolved_demands

    def generate_candidates(self, inventory_type, filtering_attributes, candidate_uniqueness):

        if inventory_type == "slice_profiles":
            return self.generate_slice_profile_candidates(filtering_attributes, inventory_type, candidate_uniqueness)
        else:
            LOG.debug("No functionality implemented for \
                      generating candidates for inventory_type {}".format(inventory_type))
            return []

    def generate_slice_profile_candidates(self, filtering_attributes, inventory_type, candidate_uniqueness):
        """Generates a list of slice profile candidate based on the filtering attributes,

           A sample filtering attribute is given below
           filtering_attributes = {'core': {'latency': {'min': 15, 'max': 20, 'steps': 1},
                                            'reliability': {'values': [99.999]}},
                                   'ran': {'latency': {'min': 10, 'max': 20, 'steps': 1},
                                           'reliability': {'values': [99.99]},
                                           'coverage_area_ta_list': {'values': ['City: Chennai']}}}
            It will generate slice profile combination from the attributes for each subnet and
            generates combination of slice profile tuples from the each subnet.
        """
        subnet_combinations = {}
        for subnet, attributes in filtering_attributes.items():
            attribute_names, attribute_combinations = generate_combinations(attributes)
            subnet_combinations[subnet] = organize_combinations(attribute_names, attribute_combinations)

        subnet_names, slice_profile_combinations = get_combinations_from_dict(subnet_combinations)
        organized_combinations = organize_combinations(subnet_names, slice_profile_combinations)
        candidates = []
        for combination in organized_combinations:
            info = Candidate.build_candidate_info(self.name(), inventory_type, 1.0, candidate_uniqueness,
                                                  str(uuid.uuid4()))
            candidate = SliceProfilesCandidate(info=info, subnet_requirements=combination)
            candidates.append(candidate.convert_nested_dict_to_dict())

        return candidates


def generate_combinations(attributes):
    """Generates all combination of the given attribute values.

       The params can have a values list or range(min, max)
       from which the combinations are generated.
    """
    attr = dict()
    for attribute, attr_params in attributes.items():
        values = attr_params.get('values')
        if not values:
            values = range(attr_params.get('min', 1), attr_params.get('max'),
                           attr_params.get('steps', 1))
        attr[attribute] = values

    return get_combinations_from_dict(attr)


def get_combinations_from_dict(attr):
    """Generates combinations from a dictionary containing lists

       Input:
       attr = {"latency": [1,2,3],
               "reliability": [99.99, 99.9]
              }
       Output:
       attribute_name: ["latency", "reliability"]
       attribute_combinations: [[1,99.99], [2,99.99], [3,99.99], [1,99.9], [2,99.9], [3,99.9]]
    """
    attribute_names = list(attr.keys())
    attribute_combinations = list(itertools.product(*attr.values()))
    return attribute_names, attribute_combinations


def organize_combinations(attribute_names, attribute_combinations):
    """Organise the generated combinations into list of dicts.

       Input:
       attribute_name: ["latency", "reliability"]
       attribute_combinations: [[1,99.99], [2,99.99], [3,99.99], [1,99.9], [2,99.9], [3,99.9]]
       Output:
       combinations = [{'latency': 1, 'reliability': 99.99},
                       {'latency': 2, 'reliability': 99.99},
                       {'latency': 3, 'reliability': 99.99},
                       {'latency': 1, 'reliability': 99.9},
                       {'latency': 2, 'reliability': 99.9},
                       {'latency': 3, 'reliability': 99.9}
                      ]
    """
    combinations = []
    for combination in attribute_combinations:
        comb = {}
        for (name, value) in zip(attribute_names, combination):
            comb[name] = value
        combinations.append(comb)
    return combinations
