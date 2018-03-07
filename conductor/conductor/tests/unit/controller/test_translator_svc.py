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
import uuid

from mock import patch
from mock import PropertyMock
from conductor.controller.translator_svc import TranslatorService
from conductor.common.models import plan
from conductor.common.music import api
from conductor.common.music.model import base
from oslo_config import cfg


def plan_prepare(conf):
    music = api.API()
    music.keyspace_create(keyspace=conf.keyspace)
    plan_tmp = base.create_dynamic_model(
        keyspace=conf.keyspace, baseclass=plan.Plan, classname="Plan")
    return plan_tmp


class TestTranslatorServiceNoException(unittest.TestCase):
    def setUp(self):
        cfg.CONF.set_override('polling_interval', 1, 'controller')
        cfg.CONF.set_override('keyspace', 'conductor')
        cfg.CONF.set_override('timeout', 10, 'controller')
        cfg.CONF.set_override('limit', 1, 'controller')
        cfg.CONF.set_override('concurrent', True, 'controller')
        cfg.CONF.set_override('keyspace',
                              'conductor_rpc', 'messaging_server')
        cfg.CONF.set_override('mock', True, 'music_api')
        self.conf = cfg.CONF
        self.Plan = plan_prepare(self.conf)
        kwargs = self.Plan
        name = str(uuid.uuid4())
        timeout = self.conf.controller.timeout
        recommend_max = self.conf.controller.limit
        template = None
        status = self.Plan.TEMPLATE
        self.mock_plan = self.Plan(name, timeout, recommend_max, template,
                                   status=status)
        self.translator_svc = TranslatorService(
            worker_id=1, conf=self.conf, plan_class=kwargs)
        self.translator_svc.music.keyspace_create(keyspace=self.conf.keyspace)

    #TODO(ruoyu)
    @patch('conductor.controller.translator.Translator.ok')
    def translate_complete(self, mock_ok_func):
        with patch('conductor.controller.translator.Translator.ok',
                   new_callable=PropertyMock) as mock_ok:
            mock_ok.return_value = True
        mock_ok_func.return_value = True
        self.translator_svc.translate(self.mock_plan)
        self.assertEquals(self.mock_plan.status, 'translated')

    # TODO(ruoyu)
    @patch('conductor.controller.translator.Translator.translate')
    @patch('conductor.controller.translator.Translator.error_message')
    def translate_error(self, mock_error, mock_trns):
        with patch('conductor.controller.translator.Translator.ok',
                   new_callable=PropertyMock) as mock_ok:
            mock_ok.return_value = False
        mock_error.return_value = 'error'
        self.translator_svc.translate(self.mock_plan)
        self.assertEquals(self.mock_plan.status, 'error')

    def tearDown(self):
        patch.stopall()


if __name__ == '__main__':
    unittest.main()
