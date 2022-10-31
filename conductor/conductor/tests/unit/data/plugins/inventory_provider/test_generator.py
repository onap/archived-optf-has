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
import json
import mock
from mock import patch
from conductor.data.plugins.inventory_provider.cps import CPS

from conductor.data.plugins.inventory_provider.generator import Generator


class TestGenerator(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        patch.stopall()

    def test_generate_candidate(self):

        candidates_file = './conductor/tests/unit/data/plugins/inventory_provider/generated_candidates.json'
        expected_candidates = json.loads(open(candidates_file).read())
        for candidate in expected_candidates:
            candidate['coverage_area_ta_list'] = '[234, 123, 421]'
        coverage_area_file='./conductor/tests/unit/data/plugins/inventory_provider/coverage_area.json'
        coverage_area_json = json.loads(open(coverage_area_file).read())
        generator = Generator()

        filtering_attributes = {
                                  'service_profile': {
                                        'latency': {'value': 30, 'operator': 'lte'},
                                        'reliability': {'value': 99.99, 'operator': 'gte'},
                                        'coverage_area': {'value': 'City: Chennai-1,2,3', 'operator': 'eq'}
                                  },
                                  'subnets': {
                                     'core': {'latency': {'min': 15, 'max': 30, 'steps': 1},
                                              'reliability': {'values': [99.99]}},
                                     'ran': {'latency': {'min': 10, 'max': 30, 'steps': 1},
                                             'reliability': {'values': [99.99]},
                                             'coverage_area_ta_list': {"derive_from":{"method":"get_tracking_area",
                                                                                "args": {
                                                                         "coverage_area": "Chennai-1,2,3"
                                                                             }}}}
                                  }
                                }
        self.mock_get_coverage_area_ta = mock.patch.object(CPS, 'get_coveragearea_ta',
                                                         return_value=coverage_area_json)

        self.mock_get_coverage_area_ta.start()

        self.maxDiff=None

        generated_candidates = generator.generate_candidates('slice_profiles', filtering_attributes,
                                                             candidate_uniqueness='true',
                                                             default_fields={"creation_cost": 0.9})

        for candidate in generated_candidates:
            self.assertIsNotNone(candidate['candidate_id'])
            del candidate['candidate_id']

        self.assertEqual(expected_candidates, generated_candidates)

        self.assertEqual([], generator.generate_candidates('cloud', filtering_attributes,
                                                           candidate_uniqueness='true',
                                                           default_fields={"creation_cost": 0.9}))

    def test_resolve_demands(self):
        demands_file = './conductor/tests/unit/data/plugins/inventory_provider/gen_demand_list.json'
        demands = json.loads(open(demands_file).read())
        coverage_area_file = './conductor/tests/unit/data/plugins/inventory_provider/coverage_area.json'
        coverage_area_json = json.loads(open(coverage_area_file).read())

        resolved_demands_file = './conductor/tests/unit/data/plugins/inventory_provider/resolved_demands_gen.json'
        expected_resolved_demands = json.loads(open(resolved_demands_file).read())

        generator = Generator()
        self.mock_get_coverage_area_ta = mock.patch.object(CPS, 'get_coveragearea_ta',
                                                         return_value=coverage_area_json)

        self.mock_get_coverage_area_ta.start()

        self.maxDiff=None
        resolved_demands = generator.resolve_demands(demands, plan_info=None, triage_translator_data=None)
        for _, candidate_list in resolved_demands.items():
            for candidate in candidate_list:
                self.assertIsNotNone(candidate['candidate_id'])
                del candidate['candidate_id']

        self.assertEqual(expected_resolved_demands, resolved_demands)
