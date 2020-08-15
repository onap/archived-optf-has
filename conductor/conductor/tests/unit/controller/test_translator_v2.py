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
"""Test classes for translator V2"""

import copy
import json
from mock import patch
import os
import unittest
import uuid
from oslo_config import cfg

from conductor.controller.translator_utils import TranslatorException
from conductor.controller.translator_v2 import TranslatorV2

DIR = os.path.dirname(__file__)


class TestTranslatorV2(unittest.TestCase):

    def setUp(self):

        with open(os.path.join(DIR, 'template_v2.json'), 'r') as tpl:
            self.template = json.loads(tpl.read())
        with open(os.path.join(DIR, 'opt_schema.json'), 'r') as sch:
            self.opt_schema = json.loads(sch.read())

    def tearDown(self):
        pass

    @patch('conductor.common.music.model.base.Base.table_create')
    @patch('conductor.controller.translator.Translator.parse_demands')
    def test_translator_template_v2(self, mock_table, mock_parse):
        cfg.CONF.set_override('keyspace', 'conductor')
        cfg.CONF.set_override('keyspace', 'conductor_rpc', 'messaging_server')
        cfg.CONF.set_override('concurrent', True, 'controller')
        cfg.CONF.set_override('certificate_authority_bundle_file', '../AAF_RootCA.cer', 'music_api')
        conf = cfg.CONF
        translator_v2 = TranslatorV2(conf, 'v2_test', str(uuid.uuid4()), self.template,
                                     self.opt_schema)
        translator_v2.translate()
        self.assertEqual(translator_v2._ok, True)
        self.assertEqual(self.template.get('optimization'),
                         translator_v2._translation.get('conductor_solver').get('objective'))

    @patch('conductor.common.music.model.base.Base.table_create')
    def test_translator_error_version(self, mock_table):
        temp = copy.deepcopy(self.template)
        temp["homing_template_version"] = "2020-04-04"
        conf = cfg.CONF
        translator_v2 = TranslatorV2(conf, 'v2_test', str(uuid.uuid4()), temp,
                                     self.opt_schema)
        translator_v2.create_components()
        self.assertRaises(TranslatorException, translator_v2.validate_components)

    @patch('conductor.common.music.model.base.Base.table_create')
    def test_translator_no_optimization(self, mock_table):
        conf = cfg.CONF
        translator_v2 = TranslatorV2(conf, 'v2_test', str(uuid.uuid4()), self.template,
                                     self.opt_schema)
        self.assertEqual(None, translator_v2.parse_optimization({}))

    @patch('conductor.common.music.model.base.Base.table_create')
    def test_translator_v2_wrong_opt(self, mock_table):
        opt = {"goal": "nothing"}
        conf = cfg.CONF
        translator_v2 = TranslatorV2(conf, 'v2_test', str(uuid.uuid4()), self.template,
                                     self.opt_schema)
        self.assertRaises(TranslatorException, translator_v2.parse_optimization, optimization=opt)

    @patch('conductor.common.music.model.base.Base.table_create')
    @patch('conductor.controller.translator.Translator.parse_demands')
    def test_translator_incorrect_demand(self, mock_table, mock_parse):
        templ = copy.deepcopy(self.template)
        templ["optimization"]["operation_function"]["operands"][0]["params"]["demand"] = "vF"
        conf = cfg.CONF
        translator_v2 = TranslatorV2(conf, 'v2_test', str(uuid.uuid4()), templ,
                                     self.opt_schema)
        translator_v2.create_components()
        self.assertRaises(TranslatorException, translator_v2.parse_optimization,
                          optimization=templ["optimization"])


if __name__ == '__main__':
    unittest.main()
