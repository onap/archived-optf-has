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

class Candidate(object):
    def __init__(self, info):
        self.candidate_id = info.get('candidate_id')
        if info.get('candidate_type'):
            self.candidate_type = info.get('candidate_type')
        if info.get('service_resource_id'):
            self.service_resource_id = info.get('service_resource_id')
        self.inventory_provider = info.get('inventory_provider')
        self.inventory_type = info.get('inventory_type')
        self.uniqueness = info.get('uniqueness')
        self.cost = info.get('cost')

    def convert_nested_dict_to_dict(self):
        candidate = dict()
        nested_dict = self.__dict__
        keys = nested_dict.keys()
        for key in keys:
            if type(nested_dict.get(key)) == dict:
                candidate.update(nested_dict.get(key, {}))
            else:
                candidate[key] = nested_dict.get(key, "")
        return candidate

    @staticmethod
    def build_candidate_info(inv_prov, inv_type, cost, uniqueness, id, service_resource_id=None):
        info = dict()
        info['candidate_id'] = id
        # info['candidate_type']
        info['inventory_provider'] = inv_prov
        info['inventory_type'] = inv_type
        info['uniqueness'] = uniqueness
        info['cost'] = cost
        info['service_resource_id'] = service_resource_id
        return info
