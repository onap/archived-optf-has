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

"""Test class for model order_lock_history"""

import unittest
from conductor.common.models.order_lock_history import OrderLockHistory


class TestOrderLockHistory(unittest.TestCase):

    def setUp(self):
        self.orderLockHistory = OrderLockHistory()

    def test_OrderLockHistory(self):
        self.assertEqual(True, self.orderLockHistory.atomic())
        self.assertEqual("id", self.orderLockHistory.pk_name())
        self.assertEqual(None, self.orderLockHistory.pk_value())
        self.value = {'is_spinup_completed': False, 'conflict_id': None, 'spinup_completed_timestamp': None, 'plans': None}
        self.assertEqual(self.value, list(self.orderLockHistory.values()))
        self.assertEqual("text", self.orderLockHistory.schema().get("conflict_id"))
        self.assertEqual(None, self.orderLockHistory.__json__().get("plans"))


if __name__ == '__main__':
    unittest.main()
