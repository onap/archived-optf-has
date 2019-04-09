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

"""Test class for resources service.py"""

import unittest
from conductor.solver.resource.service import Service


class TestService(unittest.TestCase):

    def setUp(self):
        self._sid = None
        self.capacity = {}
        self.allocated_demand_list = []
        self.properties = {}
        self.resource_service = Service(self._sid)

    def test_resource_service(self):
        self.assertEqual(None, self.resource_service.name)
        self.assertEqual(None, self.resource_service.region)
        self.assertEqual('active', self.resource_service.status)
        self.assertEqual(0.0, self.resource_service.cost)
        self.assertEqual(self.capacity, self.resource_service.capacity)
        self.assertEqual(self.allocated_demand_list, self.resource_service.allocated_demand_list)
        self.assertEqual(self.properties, self.resource_service.properties)
        self.assertEqual(0, self.resource_service.last_update)
        self.assertEqual(None, self.resource_service.update_capacity())
        self.assertEqual(None, self.resource_service.get_json_summary())


if __name__ == '__main__':
    unittest.main()
