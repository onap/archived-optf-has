#
# ------------------------------------------------------------------------
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
"""Test classes for translator_svc"""
import unittest

from mock import patch
from conductor.controller.translator_svc import TranslatorService
from conductor.common.models import plan
from oslo_config import cfg


class TestTranslatorServiceNoException(unittest.TestCase):

    
    def setUp(self):
        cfg.CONF.set_override('timeout', 10, 'controller')
        cfg.CONF.set_override('limit', 1, 'controller')
        cfg.CONF.set_override('keyspace', "conductor")
        cfg.CONF.set_override('polling_interval', 1, 'controller')
        cfg.CONF.set_override('keyspace', 'conductor_rpc', 'messaging_server')
        cfg.CONF.set_override('mock', True, 'music_api')
        self.conf = cfg.CONF
        kwargs = {'transport': '',
                  'target': '',
                  'endpoints': '',
                  'flush': '',
                  'plan_class': plan}
        self.translator_svc = TranslatorService(self.conf, kwargs)
        self.element = plan
        setattr(self.element, 'id', "")
        setattr(self.element, 'name', '')
        setattr(self.element, 'message', '')
        setattr(self.element, 'template', '')
        setattr(self.element, 'status', plan.TEMPLATE)

    @patch('conductor.controller.translator.Translator.translation')
    @patch('conductor.controller.translator.Translator.ok')
    def test_translate_complete(self, mock_trns, mock_ok):
        mock_trns.__get__.return_value = {"conductor_solver": {
            "version": "2016-11-01",
            "plan_id": "",
            "locations": "",
            "demands": "",
            "constraints": "",
            "objective": "",
            "reservations": ""
        }}
        mock_plan = self.element
        mock_ok.__get__.return_value = True
        self.translator_svc.translate(mock_plan)
        self.assertEquals(mock_plan.translation, mock_trns.translation)
        self.assertEquals(mock_plan.status, plan.TRANSLATED)

    @patch('conductor.controller.translator.Translator')
    @patch('conductor.controller.translator.Translator.error_message')
    @patch('conductor.controller.translator.Translator.ok') 
    def test_translate_error(self, mock_trns, mock_error, mock_ok):
        mock_plan = self.element
        mock_ok.__get__.return_value = False
        mock_error.__get__.return_value = ''
        self.translator_svc.translate(mock_plan)
        self.assertEquals(mock_plan.message, '')
        self.assertEquals(mock_plan.status, plan.ERROR)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
