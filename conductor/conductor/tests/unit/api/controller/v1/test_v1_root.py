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
"""Test case for V1Controller /"""

from conductor.tests.unit.api import base_api
from oslo_config import cfg
import pecan

class TestV1Root(base_api.BaseApiTest):

    def setUp(self):
        super(TestV1Root, self).setUp()
        # self._set_config()
        # TODO(dileep.ranganathan): Move common mock and configs to BaseTest
        cfg.CONF.conductor_api.username = "admin"
        cfg.CONF.conductor_api.password = "default"

        self.app = self._make_app()

        def reset_pecan():
            pecan.set_config({}, overwrite=True)

        self.addCleanup(reset_pecan)


    def test_get_v1_root(self):
        actual_response = self.app.get('/v1', expect_errors=True)
        # print('GOT:%s' % actual_response)
        self.assertEqual(actual_response.status_int, 405)
