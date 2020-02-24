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

"""Test class for model region_placeholders"""

import unittest
from conductor.common.models.region_placeholders import RegionPlaceholders


class TestRegionPlaceholders(unittest.TestCase):

    def setUp(self):
        self.regionPlaceHolder = RegionPlaceholders()

    def test_RegionPlaceholders(self):
        self.assertEqual(True, self.regionPlaceHolder.atomic())
        self.assertEqual("id", self.regionPlaceHolder.pk_name())
        self.assertEqual(None, self.regionPlaceHolder.pk_value())
        self.value = {'region_name': None, 'countries': None}
        self.assertEqual(self.value, list(self.regionPlaceHolder.values()))
        self.assertEqual("text", self.regionPlaceHolder.schema().get("region_name"))
        self.assertEqual(None, self.regionPlaceHolder.__json__().get("region_name"))


if __name__ == '__main__':
    unittest.main()
