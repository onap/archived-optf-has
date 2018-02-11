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
"""Test case for PlansController"""

import json

import mock
from conductor.api.controllers.v1 import plans
from conductor.tests.unit.api import base_api
from oslo_serialization import jsonutils


class TestPlansController(base_api.BaseApiTest):

    def test_index_options(self):
        actual_response = self.app.options('/v1/plans', expect_errors=True)
        self.assertEqual(204, actual_response.status_int)
        self.assertEqual("GET,POST", actual_response.headers['Allow'])

    @mock.patch.object(plans.LOG, 'error')
    @mock.patch.object(plans.LOG, 'debug')
    @mock.patch.object(plans.LOG, 'warning')
    @mock.patch.object(plans.LOG, 'info')
    def test_index_get(self, info_mock, warning_mock, debug_mock, error_mock):
        actual_response = self.app.get('/v1/plans')
        self.assertEqual(200, actual_response.status_int)

    @mock.patch.object(plans.LOG, 'error')
    @mock.patch.object(plans.LOG, 'debug')
    @mock.patch.object(plans.LOG, 'warning')
    @mock.patch.object(plans.LOG, 'info')
    def test_index_post(self, info_mock, warning_mock, debug_mock, error_mock):
        req_json_file = './conductor/tests/unit/api/controller/v1/plans.json'
        params = jsonutils.dumps(json.loads(open(req_json_file).read()))
        print(params)
        response = self.app.post('/v1/plans', params=params,
                                 expect_errors=True)
        self.assertEqual(500, response.status_int)

    def test_index_httpmethod_notallowed(self):
        actual_response = self.app.put('/v1/plans', expect_errors=True)
        self.assertEqual(405, actual_response.status_int)
        actual_response = self.app.patch('/v1/plans', expect_errors=True)
        self.assertEqual(405, actual_response.status_int)
