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

import unittest
import uuid

from conductor.data.plugins.inventory_provider.candidates.candidate import Candidate
from conductor.data.plugins.inventory_provider.candidates.slice_profiles_candidate import SliceProfilesCandidate

class TestCandidates(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_slice_profiles_candidate(self):
        id = str(uuid.uuid4())
        expected_candidate = {
                                "candidate_id": id,
                                "core_latency": 15,
                                "core_reliability": 99.99,
                                "cost": 1.0,
                                "coverage_area": "City: Chennai",
                                "coverage_area_ta_list": "City: Chennai",
                                "inventory_provider": "generator",
                                "inventory_type": "slice_profiles",
                                "latency": 25,
                                "ran_coverage_area_ta_list": "City: Chennai",
                                "ran_latency": 10,
                                "ran_reliability": 99.99,
                                "reliability": 99.99,
                                "uniqueness": "true",
                                "creation_cost": 0.9
                            }
        info = Candidate.build_candidate_info("generator", "slice_profiles", 1.0, "true", id)
        subnet_requirements = {"core": {"latency": 15, "reliability": 99.99},
                               "ran": {"latency": 10, "reliability": 99.99, "coverage_area_ta_list": "City: Chennai"}
                               }

        candidate = SliceProfilesCandidate(info=info, subnet_requirements=subnet_requirements,
                                           default_fields={"creation_cost": 0.9},coverage_area="City: Chennai")

        self.assertEqual(expected_candidate, candidate.convert_nested_dict_to_dict())
