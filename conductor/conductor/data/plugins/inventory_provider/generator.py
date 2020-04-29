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

LOG = log.getLogger(__name__)


class Generator(base.InventoryProviderBase):

    def __init__(self):
        """Initialize variables"""
        pass

    def name(self):
        """Return human-readable name."""
        return "Generator"

    def resolve_demands(self, demands, plan_info, triage_translator_data):
        """Resolve demands into candidate list"""
        resolved_demands = dict()
        for name, requirements in demands.items():
            resolved_demands[name] = list()
            for requirement in requirements:
                inventory_type = requirement.get('inventory_type').lower()
                candidate_uniqueness = requirement.get('unique', 'true')
                filtering_attributes = requirement.get('filtering_attributes')

                resolved_demands[name].append(self.generate_candidates(inventory_type,
                                                                       filtering_attributes,
                                                                       candidate_uniqueness))

        return resolved_demands

    def generate_candidates(self, inventory_type, filtering_attributes, candidate_uniqueness):
        candidate_list = list()

        if inventory_type == "nssi":
            attribute_names, attribute_combinations = \
                self.generate_combinations(filtering_attributes)
            for combination in attribute_combinations:
                candidate = dict()

                for (name, value) in zip(attribute_names, combination):
                    candidate[name] = value

                candidate['candidate_id'] = str(uuid.uuid4())
                candidate['cost'] = 1.0
                candidate['inventory_type'] = inventory_type
                candidate['inventory_provider'] = 'generator'
                candidate['uniqueness'] = candidate_uniqueness
                candidate['candidate_type'] = 'nssi'

                candidate_list.append(candidate)
        else:
            LOG.debug("No functionality implemented for \
                      generating candidates for inventory_type {}".format(inventory_type))

        return candidate_list

    def generate_combinations(self, attributes):
        """Generates all combination of the given attribute values."""
        attr = dict()
        for attribute, attr_params in attributes.items():
            values = attr_params.get('values')
            if not values:
                values = range(attr_params.get('min', 1), attr_params.get('max'),
                               attr_params.get('steps', 1))
            attr[attribute] = values

        attribute_names = list(attr.keys())
        attribute_combinations = list(itertools.product(*attr.values()))
        return attribute_names, attribute_combinations
