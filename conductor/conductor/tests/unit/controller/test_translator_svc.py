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
import mock
import uuid

from mock import patch
from mock import PropertyMock
from conductor.controller.translator_svc import TranslatorService
from conductor.common.models import plan as Plan
from conductor.common.music import api
from conductor.common.music.model import base
from oslo_config import cfg


class fake_plan():
    def __init__(self):
        self._id = ''
        self._name = ''
        self._template = ''
        self._trns = ''
        self._status = ''
        self._message = ''

    def update(self):
        pass

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def template(self):
        return self._template

    @property
    def translation(self):
        return self._trns

    @property
    def status(self):
        return self._status

    @property
    def message(self):
        return self._message


class TestTranslatorServiceNoException(unittest.TestCase):
    @patch(
        'conductor.controller.translator_svc.TranslatorService.setup_rpc')
    def setUp(self, mock_rpc):
        cfg.CONF.set_override('polling_interval', 1, 'controller')
        cfg.CONF.set_override('keyspace', 'conductor')
        cfg.CONF.set_override('timeout', 10, 'controller')
        cfg.CONF.set_override('limit', 1, 'controller')
        cfg.CONF.set_override('keyspace',
                              'conductor_rpc', 'messaging_server')
        cfg.CONF.set_override('mock', True, 'music_api')
        self.conf = cfg.CONF
        self.mock_plan_attr = mock.MagicMock()
        value_1 = PropertyMock(return_value='translated')
        type(self.mock_plan_attr).TRANSLATED = value_1
        value_2 = PropertyMock(return_value='error')
        type(self.mock_plan_attr).ERROR = value_2
        kwargs = {'plan_class': self.mock_plan_attr}
        self.translator_svc = TranslatorService(
            worker_id=1, conf=self.conf, kwargs=kwargs)

    @patch('conductor.controller.translator.Translator.ok')
    @patch('conductor.controller.translator.Translator.translate')
    def test_translate_complete(self, mock_translate, mock_ok_func):
        mock_plan = fake_plan()
        with patch('conductor.controller.translator.Translator.ok',
                   new_callable=PropertyMock) as mock_ok:
            mock_ok.return_value = True
        mock_ok_func.return_value = True
        self.translator_svc.Plan = self.mock_plan_attr
        self.translator_svc.translate(mock_plan)
        self.assertEquals(mock_plan.status, 'translated')

    @patch('conductor.controller.translator.Translator.translate')
    @patch('conductor.controller.translator.Translator.error_message')
    def test_translate_error(self, mock_error, mock_translate):
        mock_plan = fake_plan()
        with patch('conductor.controller.translator.Translator.ok',
                   new_callable=PropertyMock) as mock_ok:
            mock_ok.return_value = False
        mock_error.return_value = 'error'
        self.translator_svc.Plan = self.mock_plan_attr
        self.translator_svc.translate(mock_plan)
        self.assertEquals(mock_plan.status, 'error')

    def tearDown(self):
        patch.stopall()


if __name__ == '__main__':
    unittest.main()
