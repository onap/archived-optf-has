#
# -------------------------------------------------------------------------
#   Copyright (C) 2019 IBM.
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

"""Test class for reservation service"""

import unittest

from conductor.common import db_backend
from conductor.reservation.service import ReservationServiceLauncher as ReservationServiceLauncher
from conductor.reservation.service import ReservationService
from conductor.common.models import plan
from conductor.common.music.model import base
from oslo_config import cfg
import uuid
from mock import patch
import json

def plan_prepare(conf):
    cfg.CONF.set_override('certificate_authority_bundle_file', '../AAF_RootCA.cer', 'music_api')
    music = db_backend.get_client()
    music.keyspace_create(keyspace=conf.keyspace)
    plan_tmp = base.create_dynamic_model(
        keyspace=conf.keyspace, baseclass=plan.Plan, classname="Plan")
    return plan_tmp


CONF = cfg.CONF


class TestReservationService(unittest.TestCase):

    @patch('conductor.common.music.model.base.Base.table_create')
    @patch('conductor.common.music.model.base.Base.insert')
    @patch('conductor.reservation.service.ReservationService._reset_reserving_status')
    def setUp(self,  mock_reset, mock_insert, mock_table_create):

        self.conf = cfg.CONF
        self.Plan = plan_prepare(self.conf)
        kwargs = self.Plan
        name = str(uuid.uuid4())
        timeout = 10000
        recommend_max = 3
        template = None
        status = self.Plan.TEMPLATE
        self.mock_plan = self.Plan(name, timeout, recommend_max, template,
                                   status=status)
        self.service = ReservationService(
            worker_id=1, conf=self.conf, plan_class=kwargs)
        self.service.music.keyspace_create(keyspace=self.conf.keyspace)

        self.rl = ReservationServiceLauncher(self.conf)

    def test_current_time_seconds(self):
        self.assertIsInstance(self.service.current_time_seconds(), int)

    def test_millisec_to_sec(self):
        self.assertEqual(2, self.service.millisec_to_sec(2000))

    def test_rollback_reservation(self):
        reservation_list = list()
        self.assertEqual(True, self.service.rollback_reservation(reservation_list))

    @patch('conductor.common.music.model.base.Base.insert')
    @patch('conductor.common.music.model.search.Query.get_plan_by_col')
    @patch('conductor.common.music.model.base.Base.update')
    def test_reset_reserving_status(self, mock_call, mock_update, mock_insert):
        mock_plan = self.Plan(str(uuid.uuid4()),
                              100000,
                              3, None,
                              status=self.Plan.RESERVING)
        mock_call.return_value = mock_plan
        self.service._reset_reserving_status()
        mock_update.assert_called_once()

    @patch('conductor.reservation.service.ReservationService._gracefully_stop')
    def test_terminate(self, mock_stop):
        self.service.terminate()
        mock_stop.assert_called_once()
        self.assertFalse(self.service.running)

    @patch('conductor.reservation.service.ReservationService._restart')
    def test_reload(self, mock_restart):
        self.service.reload()
        mock_restart.assert_called_once()

    def tearDown(self):
        patch.stopall()


if __name__ == '__main__':
    unittest.main()
