#
# -------------------------------------------------------------------------
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
import unittest
import conductor.solver.utils.utils as utils

class TestUtils(unittest.TestCase):

    def setUp(self):
        self._dst = None
        self._src = None

    def test_utils(self):
        self.assertEqual(0.0, utils.compute_air_distance(self._src, self._dst))
        self.assertEqual(1.242742, utils.convert_km_to_miles(2.0))
        self.assertEqual(2.0, utils.convert_miles_to_km(1.242742))

if __name__ == "__main__":
    unittest.main()
