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
"""Test classes for rpc"""

import unittest
import uuid

from conductor.common import db_backend
from conductor.controller.rpc import ControllerRPCEndpoint as rpc
from conductor import service
from conductor.common.models import plan
from conductor.common.music.model import base
from oslo_config import cfg
from mock import patch


def plan_prepare(conf):
    music = db_backend.get_client()
    music.keyspace_create(keyspace=conf.keyspace)
    plan_tmp = base.create_dynamic_model(
        keyspace=conf.keyspace, baseclass=plan.Plan, classname="Plan")
    return plan_tmp


class TestRPCNoException(unittest.TestCase):
    def setUp(self):
        cfg.CONF.set_override('timeout', 10, 'controller')
        cfg.CONF.set_override('limit', 1, 'controller')
        cfg.CONF.set_override('keyspace', 'conductor')
        conf = cfg.CONF
        plan_class = plan_prepare(conf)
        self.r = rpc(conf, plan_class)
        self._cvx = ""
        self._arg = {
            "name": str(uuid.uuid4()),
            "timeout": conf,
            "limit": conf,
            "template": None
        }
        self.plan_expected = {
            "plan": {
                "name": "null",
                "id": "null",
                "status": "null"
            }
        }
        self.plan_mock = []
        element = plan_prepare(conf)
        setattr(element, "name", "null")
        setattr(element, "id", "null")
        setattr(element, "status", "null")
        setattr(element, "message", "null")
        e = {'recommendations': 'null'}
        setattr(element, "solution", e)
        self.plan_mock.append(element)
        self.the_plan_expected = [{
            "name": "null",
            "id": "null",
            "status": "null",
            "message": "null",
            "recommendations": "null"
        }]

    def test_plan_creation(self):
        a_arg = []
        b_arg = []
        rtn = self.r.plan_create(self._cvx, self._arg)
        for k in sorted(rtn.get('response')):
            a_arg.append(k)
        for key in sorted(self.plan_expected):
            b_arg.append(key)
        self.assertEqual(rtn.get('error'), False)
        self.assertEqual(a_arg, b_arg)
        for k in sorted(rtn.get('response').get('plan')):
            a_arg.append(k)
        for key in sorted(self.plan_expected.get('plan')):
            b_arg.append(key)
        self.assertEqual(a_arg, b_arg)

    @patch('conductor.common.music.model.search.Query.all')
    def test_plan_get_same_schema(self, mock_query):
        _id = {}
        mock_query.return_value = self.plan_mock
        rtn_get = self.r.plans_get(self._cvx, _id)
        plans = rtn_get.get('response').get('plans')
        self.assertEqual(plans, self.the_plan_expected)
        self.assertFalse(rtn_get.get('error'))

    @patch('conductor.common.music.model.search.Query.all')
    @patch('conductor.common.music.model.base.Base.delete')
    def test_plans_delete(self, mock_delete, mock_call):
        _id = {}
        mock_call.return_value = self.plan_mock
        rtn = self.r.plans_delete(self._cvx, _id)
        self.assertEqual(rtn.get('response'), {})
        self.assertFalse(rtn.get('error'))

    def tearDown(self):
        patch.stopall()


if __name__ == '__main__':
    unittest.main()
