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

import copy

from conductor.data.plugins.inventory_provider.candidates.candidate import Candidate


def copy_first(x):
    return list(filter(None, x))[0]


ATTRIBUTE_AGGREGATION = {
    "max_bandwidth": copy_first,
    "jitter": sum,
    "sst": copy_first,
    "latency": sum,
    "resource_sharing_level": copy_first,
    "s_nssai": copy_first,
    "plmn_id_list": copy_first,
    "availability": copy_first,
    "throughput": min,
    "reliability": copy_first,
    "max_number_of_ues": copy_first,
    "exp_data_rate_ul": min,
    "exp_data_rate_dl": min,
    "ue_mobility_level": copy_first,
    "coverage_area_ta_list": copy_first,
    "activity_factor": copy_first,
    "survival_time": copy_first,
    "max_number_of_conns": copy_first
}


class SliceProfilesCandidate(Candidate):

    def __init__(self, **kwargs):
        super().__init__(kwargs["info"])
        self.subnet_requirements = kwargs["subnet_requirements"]

    def convert_nested_dict_to_dict(self):
        nested_dict = self.__dict__

        slice_requirements = self.get_slice_requirements()

        slice_profile_candidate = copy.deepcopy(nested_dict)
        slice_profile_candidate.pop("subnet_requirements")
        slice_profile_candidate.update(slice_requirements)
        for subnet, slice_profile in self.subnet_requirements.items():
            subnet_req = {f'{subnet}_{key}': value for key, value in slice_profile.items()}
            slice_profile_candidate.update(subnet_req)

        return slice_profile_candidate

    def get_slice_requirements(self):
        slice_requirements_keys = set()
        for slice_profile in self.subnet_requirements.values():
            slice_requirements_keys.update(slice_profile.keys())

        slice_profile_tuples = {}
        for key in slice_requirements_keys:
            attributes = []
            for slice_profile in self.subnet_requirements.values():
                attributes.append(slice_profile.get(key))
            slice_profile_tuples[key] = attributes

        return {attr: ATTRIBUTE_AGGREGATION[attr](values) for attr, values in slice_profile_tuples.items()}
