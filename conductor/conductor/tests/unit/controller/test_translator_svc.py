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
import time
import futurist

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
    @patch('conductor.common.music.model.base.Base.table_create')
    @patch('conductor.common.music.model.base.Base.insert')
    @patch('conductor.controller.translator_svc.TranslatorService._reset_template_status')
    def setUp(self, mock_reset, mock_insert, mock_table_create):
        cfg.CONF.set_override('polling_interval', 1, 'controller')
        cfg.CONF.set_override('keyspace', 'conductor')
        cfg.CONF.set_override('timeout', 10, 'controller')
        cfg.CONF.set_override('limit', 1, 'controller')
        cfg.CONF.set_override('concurrent', True, 'controller')
        cfg.CONF.set_override('keyspace',
                              'conductor_rpc', 'messaging_server')
        cfg.CONF.set_override('certificate_authority_bundle_file', '../AAF_RootCA.cer', 'music_api')
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

    # TODO(ruoyu)
    @patch('conductor.controller.translator.Translator.ok')
    def translate_complete(self, mock_ok_func):
        with patch('conductor.controller.translator.Translator.ok',
                   new_callable=PropertyMock) as mock_ok:
            mock_ok.return_value = True
        mock_ok_func.return_value = True
        self.translator_svc.translate(self.mock_plan)
        self.assertEquals(self.mock_plan.status, 'translated')


    @patch('conductor.controller.translator.Translator.translate')
    @patch('conductor.controller.translator.Translator.error_message')
    @patch('conductor.common.music.model.base.Base.update')
    def test_translate_error(self, mock_row_update, mock_error, mock_trns):
        with patch('conductor.controller.translator.Translator.ok',
                   new_callable=PropertyMock) as mock_ok:
            mock_ok.return_value = False
        mock_error.return_value = 'error'
        self.translator_svc.translate(self.mock_plan)
        self.assertEquals(self.mock_plan.status, 'error')

    def test_millisec_to_sec(self):
        self.assertEquals(self.translator_svc.millisec_to_sec(1000), 1)

    def test_current_time_seconds(self):
        self.assertEquals(self.translator_svc.current_time_seconds(),
                          int(round(time.time())))

    @patch('conductor.common.music.model.base.Base.insert')
    @patch('conductor.common.music.model.search.Query.get_plan_by_col')
    @patch('conductor.common.music.model.base.Base.update')
    def test_reset_template_status(self, mock_call, mock_update, mock_insert):
        mock_plan = self.Plan(str(uuid.uuid4()),
                              self.conf.controller.timeout,
                              self.conf.controller.limit, None,
                              status=self.Plan.TRANSLATING)
        mock_call.return_value = mock_plan
        self.translator_svc._reset_template_status()
        mock_update.assert_called_once()

    @patch('conductor.controller.translator_svc.TranslatorService._gracefully_stop')
    def test_terminate(self, mock_stop):
        self.translator_svc.terminate()
        mock_stop.assert_called_once()
        self.assertFalse(self.translator_svc.running)

    @patch('conductor.controller.translator_svc.TranslatorService._restart')
    def test_reload(self, mock_restart):
        self.translator_svc.reload()
        mock_restart.assert_called_once()

    def tearDown(self):
        patch.stopall()


if __name__ == '__main__':
    unittest.main()
