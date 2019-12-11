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

import unittest

import conductor.data.plugins.vim_controller.multicloud as mc
import mock
from oslo_config import cfg


class TestMultiCloud(unittest.TestCase):

    def setUp(self):
        cli_opts = [
            cfg.BoolOpt('debug',
                        short='d',
                        default=False,
                        help='Print debugging output.'),
        ]
        cfg.CONF.register_cli_opts(cli_opts)
        self.mc_ep = mc.MULTICLOUD()
        self.mc_ep.conf.set_override('certificate_authority_bundle_file', '../AAF_RootCA.cer', 'multicloud')
        self.mc_ep.conf.set_override('debug', False)

    def tearDown(self):
        mock.patch.stopall()

    def test_initialize(self):
        self.mc_ep.initialize()
        self.assertEqual('http://msb.onap.org/api/multicloud',
                         self.mc_ep.rest.server_url)
        self.assertEqual((float(3.05), float(30)), self.mc_ep.rest.timeout)
        self.assertEqual(None, super(mc.MULTICLOUD, self.mc_ep).name())
        self.assertEqual("MultiCloud", self.mc_ep.name())

    @mock.patch.object(mc.LOG, 'error')
    @mock.patch.object(mc.LOG, 'debug')
    @mock.patch.object(mc.LOG, 'info')
    @mock.patch('conductor.common.rest.REST.request')
    def test_check_vim_capacity(self, rest_mock, i_mock, d_mock, e_mock):
        self.mc_ep.initialize()
        response = mock.MagicMock()
        response.status_code = 400
        response.text = {"VIMs": ["att-aic_NYCNY33"]}
        vim_request = {
            "vCPU": 10,
            "Memory": {
                "quantity": "10",
                "unit": "GB"
            },
            "Storage": {
                "quantity": "100",
                "unit": "GB"
            },
            "VIMs": ["att-aic_NYCNY33"]
        }

        rest_mock.return_value = None
        self.assertEqual(None, self.mc_ep.check_vim_capacity(vim_request))
        rest_mock.return_value = response
        self.assertEqual(None, self.mc_ep.check_vim_capacity(vim_request))
        response.status_code = 200
        response.json.return_value = response.text
        rest_mock.return_value = response
        self.assertEqual(['att-aic_NYCNY33'],
                         self.mc_ep.check_vim_capacity(vim_request))
        response.json.return_value = None
        rest_mock.return_value = response
        self.assertEqual(None, self.mc_ep.check_vim_capacity(vim_request))
        response.text = {"VIMs": []}
        response.json.return_value = response.text
        rest_mock.return_value = response
        self.assertEqual([], self.mc_ep.check_vim_capacity(vim_request))
        response.text = {"VIMs": None}
        response.json.return_value = response.text
        rest_mock.return_value = response
        self.assertEqual(None, self.mc_ep.check_vim_capacity(vim_request))


if __name__ == "__main__":
    unittest.main()
