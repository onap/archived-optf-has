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

"""Test class for resources region.py"""

import unittest
from conductor.solver.resource.region import Region
from conductor.solver.resource.region import Zone
from conductor.solver.resource.region import Link

class TestResourceRegion(unittest.TestCase):

    def setUp(self):
        self._rid = None
        self.address = {}
        self.zones = {}
        self.capacity = {}
        self.allocated_demand_list = []
        self.properties = {}
        self.neighbor_list = []
        self._zid = None
        self._region_name = ''

        self.resource_region = Region(self._rid)
        self._zone = Zone(self._zid)
        self._link = Link(self._region_name)

    def test_resource_region(self):

        self.assertEqual('active', self.resource_region.status)
        self.assertEqual(None, self.resource_region.region_type)
        self.assertEqual(None, self.resource_region.location)
        self.assertEqual(self.address, self.resource_region.address)
        self.assertEqual(self.zones, self.resource_region.zones)
        self.assertEqual(0.0, self.resource_region.cost)
        self.assertEqual(None, self.resource_region.update_capacity())
        self.assertEqual(self.allocated_demand_list, self.resource_region.allocated_demand_list)
        self.assertEqual(self.properties, self.resource_region.properties)
        self.assertEqual(self.neighbor_list, self.resource_region.neighbor_list)
        self.assertEqual(0, self.resource_region.last_update)
        self.assertEqual(None, self.resource_region.update_capacity())
        self.assertEqual(None, self.resource_region.get_json_summary())
        self.assertEqual(None, self._zone.get_json_summary())
        self.assertEqual(None, self._link.get_json_summary())


if __name__ == '__main__':
    unittest.main()
