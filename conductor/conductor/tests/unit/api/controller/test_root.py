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

from conductor.tests.unit.api import base_api


class TestRoot(base_api.BaseApiTest):

    def test_get_index(self):
        actual_response = self.app.get('/')
        req_json_file = './conductor/tests/unit/api/controller/versions.json'
        expected_response = json.loads(open(req_json_file).read())
        print('GOT:%s' % actual_response)
        self.assertJsonEqual(actual_response.status_int, 200)
        self.assertJsonEqual(expected_response,
                             json.loads(actual_response.body))
