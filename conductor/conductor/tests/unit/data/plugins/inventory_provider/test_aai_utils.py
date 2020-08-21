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

from mock import patch

from conductor.data.plugins.inventory_provider.utils import aai_utils

class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        patch.stopall()

    def test_convert_hyphen_to_under_score(self):
        slice_profile_file = './conductor/tests/unit/data/plugins/inventory_provider/slice_profile.json'
        slice_profile_hyphened = json.loads(open(slice_profile_file).read())

        converted_slice_profile_file = './conductor/tests/unit/data/plugins/inventory_provider' \
                                       '/slice_profile_converted.json'
        converted_slice_profile = json.loads(open(converted_slice_profile_file).read())
        self.assertEqual(converted_slice_profile, aai_utils.convert_hyphen_to_under_score(slice_profile_hyphened))

    def test_get_first_level_and_second_level_filter(self):
        first_level_filter_file = './conductor/tests/unit/data/plugins/inventory_provider/first_level_filter.json'
        first_level_filter = json.loads(open(first_level_filter_file).read())
        filtering_attributes = dict()
        filtering_attributes['orchestration-status'] = "active"
        filtering_attributes['service-role'] = "nssi"
        filtering_attributes['model-invariant-id'] = "123644"
        filtering_attributes['model-version-id'] = "524846"
        filtering_attributes['environment-context'] = 'shared'

        second_level_filter = {'service-role': 'nssi'}

        self.assertEqual(second_level_filter, aai_utils.get_first_level_and_second_level_filter(filtering_attributes,
                                                                                                  "service_instance"))

        self.assertEqual(first_level_filter, filtering_attributes)

        self.assertEqual({}, aai_utils.get_first_level_and_second_level_filter(filtering_attributes,
                                                                               "service_instance"))

    def test_add_query_params(self):
        first_level_filter_file = './conductor/tests/unit/data/plugins/inventory_provider/first_level_filter.json'
        first_level_filter = json.loads(open(first_level_filter_file).read())

        query_params = "?orchestration-status=active&model-invariant-id=123644&model-version-id=524846&" \
                       "environment-context=shared&"

        self.assertEqual(query_params, aai_utils.add_query_params(first_level_filter))
        first_level_filter = {}
        self.assertEqual('', aai_utils.add_query_params(first_level_filter))

    def test_add_query_params_and_depth(self):
        first_level_filter_file = './conductor/tests/unit/data/plugins/inventory_provider/first_level_filter.json'
        first_level_filter = json.loads(open(first_level_filter_file).read())

        query_params_with_depth = "?orchestration-status=active&model-invariant-id=123644&model-version-id=524846&" \
                                  "environment-context=shared&depth=2"

        self.assertEqual(query_params_with_depth, aai_utils.add_query_params_and_depth(first_level_filter, "2"))

        only_depth = "?depth=2"
        first_level_filter = {}
        self.assertEqual(only_depth, aai_utils.add_query_params_and_depth(first_level_filter, "2"))

    def test_get_inv_values_for_second_level_filter(self):
        nssi_response_file = './conductor/tests/unit/data/plugins/inventory_provider/nssi_response.json'
        nssi_response = json.loads(open(nssi_response_file).read())
        nssi_instance = nssi_response.get("service-instance")[0]
        second_level_filter = {'service-role': 'nsi'}
        inventory_attribute = {'service-role': 'nssi'}
        self.assertEqual(inventory_attribute, aai_utils.get_inv_values_for_second_level_filter(second_level_filter,
                                                                                               nssi_instance))
