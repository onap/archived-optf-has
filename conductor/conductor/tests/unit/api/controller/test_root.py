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
"""Test case for RootController /"""

import json
import pecan
from conductor.tests.unit.api import base_api
from oslo_config import cfg

class TestRoot(base_api.BaseApiTest):

    def setUp(self):
        super(TestRoot, self).setUp()
        # self._set_config()
        # TODO(dileep.ranganathan): Move common mock and configs to BaseTest
        cfg.CONF.conductor_api.username = "admin"
        cfg.CONF.conductor_api.password = "default"

        self.app = self._make_app()

        def reset_pecan():
            pecan.set_config({}, overwrite=True)

        self.addCleanup(reset_pecan)

    def test_get_index(self):
        actual_response = self.app.get('/')
        req_json_file = './conductor/tests/unit/api/controller/versions.json'
        expected_response = json.loads(open(req_json_file).read())
        # print('GOT:%s' % actual_response)
        self.assertEqual(200, actual_response.status_int)
        self.assertJsonEqual(expected_response,
                             json.loads(actual_response.body))
