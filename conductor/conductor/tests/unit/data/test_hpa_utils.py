#
# -------------------------------------------------------------------------
#   Copyright (c) 2018 Intel Corporation Intellectual Property
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
import unittest
import mock
import yaml
from conductor.data import hpa_utils

class TestMatchHPA(unittest.TestCase):

    def setUp(self):
        flavor_json_file = './conductor/tests/unit/data/hpa_flavors.json'
        flavor_json = yaml.safe_load(open(flavor_json_file).read())
        feature_json_file = './conductor/tests/unit/data/hpa_req_features.json'
        self.feature_json = yaml.safe_load(open(feature_json_file).read())
        candidate_json_file = './conductor/tests/unit/data/candidate_list.json'
        self.candidate_json = yaml.safe_load(open(candidate_json_file).read())
        self.candidate_json['candidate_list'][1]['flavors'] = flavor_json

    def tearDown(self):
        pass

    def test_match(self):
        hpa_provider = hpa_utils.HpaMatchProvider()
        flavor_name = hpa_provider.match_flavor(self.candidate_json['candidate_list'][1], self.feature_json)
        self.assertEqual(flavor_name, 'flavor-cpu-pinning-ovsdpdk-instruction-set')

if __name__ == "__main__":
    unittest.main()


