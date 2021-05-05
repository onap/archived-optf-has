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

"""Test class for model order_lock"""

import unittest
from conductor.common.models.order_lock import OrderLock

class TestOrder_Lock(unittest.TestCase):

    def setUp(self):
        self.orderLock = OrderLock()

    def testOrderLock(self):
        self.assertEqual(True, self.orderLock.atomic())
        self.assertEqual("id", self.orderLock.pk_name())
        self.assertEqual(None, self.orderLock.pk_value())

        self.values = {'is_spinup_completed': False, 'id': None, 'spinup_completed_timestamp': None, 'plans': None}
        self.assertEqual(self.values, self.orderLock.values())

        self.reprVal = '<OrderLock None>'
        self.assertEqual(self.reprVal, self.orderLock.__repr__())

        self.assertEqual(False, self.orderLock.__json__().get('is_spinup_completed'))

        self.schema = {'PRIMARY KEY': '(id)', 'is_spinup_completed': 'boolean', 'id': 'text', 'spinup_completed_timestamp': 'bigint', 'plans': 'map<text, text>'}

        self.assertEqual(self.schema, self.orderLock.schema())



if __name__ == '__main__':
        unittest.main()
