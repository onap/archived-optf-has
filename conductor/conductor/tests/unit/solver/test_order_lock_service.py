#
# -------------------------------------------------------------------------
#   Copyright (c) 2015-2017 AT&T Intellectual Property
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
"""Test classes for order_locks_services"""

import mock
import unittest
import uuid

from conductor.common import db_backend
from conductor.common.models.order_lock import OrderLock
from conductor.solver.orders_lock.orders_lock_service import OrdersLockingService
from oslo_config import cfg


class TestOrdersLockingService(unittest.TestCase):
    def setUp(self):
        # Initialize music API
        cfg.CONF.set_override('certificate_authority_bundle_file', '../AAF_RootCA.cer', 'music_api')
        music = db_backend.get_client()
        cfg.CONF.set_override('keyspace', 'conductor')
        music.keyspace_create(keyspace=cfg.CONF.keyspace)
        self.order_lock_svc = OrdersLockingService()

    def test_update_order_status(self):

        rehome_status = OrderLock.COMPLETED
        plan_id = uuid.uuid4()
        plans = {
            plan_id: '{"status": "under-spin-up"}'
        }
        order_lock_inst = OrderLock(id='conflict_id')
        order_lock_inst.update = mock.MagicMock(return_value=None)
        actual_response = self.order_lock_svc._update_order_status(rehome_status=rehome_status,
                                                                   plans=plans,
                                                                   order_lock=order_lock_inst)

        self.assertEqual(actual_response, {plan_id: OrderLock.COMPLETED})

    def test_update_order_status_and_get_effected_plans(self):

        plan_id = uuid.uuid4()
        plans = {
            plan_id: '{'
                         '"status": "under-spin-up",'
                         '"service_resource_id": "resource-id"'
                     '}'
        }
        order_locks = [OrderLock(id='conflict_id', plans=plans)]
        rehome_status = OrderLock.COMPLETED

        self.order_lock_svc.OrderLock.query = mock.MagicMock(return_value=None)
        self.order_lock_svc.OrderLock.query.all = mock.MagicMock(return_value=order_locks)
        self.order_lock_svc._update_order_status = mock.MagicMock(return_value=None)
        self.order_lock_svc._get_plans_by_id = mock.MagicMock(return_value=plans)

        actual_response = self.order_lock_svc.update_order_status_and_get_effected_plans(rehome_status=rehome_status,
                                                                                         service_resource_id='resource-id')
        self.assertEqual(actual_response, plans)

    def test_rehomes_for_service_resource(self):

        plan_id = uuid.uuid4()
        plans = {
            plan_id: '{'
                         '"status": "rehome",'
                         '"service_resource_id": "resource-id"'
                     '}'
        }
        order_locks = [OrderLock(id='conflict_id', plans=plans)]

        rehome_status = OrderLock.COMPLETED
        self.order_lock_svc.update_order_status_and_get_effected_plans = mock.MagicMock(return_value=plans)
        self.order_lock_svc.OrderLock.query = mock.MagicMock(return_value=None)
        self.order_lock_svc.OrderLock.query.all = mock.MagicMock(return_value=order_locks)

        actual_response = self.order_lock_svc.rehomes_for_service_resource(rehome_status, 'resource-id', list())
        expect_response = [{'plan_id': plan_id, 'should_rehome': True}]

        self.assertEqual(actual_response, expect_response)

    def test_get_plans_by_id(self):

        plan_id = uuid.uuid4()
        plans = {
            plan_id: '{'
                     '"status": "under-spin-up",'
                     '"service_resource_id": "resource-id"'
                     '}'
        }
        order_locks = [OrderLock(id='conflict_id', plans=plans)]
        self.order_lock_svc.OrderLock.query = mock.MagicMock(return_value=None)
        self.order_lock_svc.OrderLock.query.get_plan_by_col = mock.MagicMock(return_value=order_locks)
        actual_response = self.order_lock_svc._get_plans_by_id('order_id')

        self.assertEqual(actual_response, plans)


if __name__ == '__main__':
    unittest.main()
