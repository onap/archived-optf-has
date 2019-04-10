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
from conductor.solver.request.functions.distance_between import DistanceBetween
from conductor.solver.request.functions.cloud_version import CloudVersion
from conductor.solver.request.functions.aic_version import AICVersion
from conductor.solver.request.functions.cost import Cost
from conductor.solver.request.functions.hpa_score import HPAScore


class TestDistanceBetween(unittest.TestCase):
    def setUp(self):
        self.db = DistanceBetween(None)
        self.cv = CloudVersion(None)
        self.aicversion = AICVersion(None)
        self.cost = Cost(None)
        self.hpa_score = HPAScore(None)

    def test_distance_between(self):
        self.assertEqual(0.0,  self.db.compute(0.0, 0.0))
        self.assertEqual(None, self.cv.func_type)
        self.assertEqual(None, self.cv.loc)
        self.assertEqual(None, self.aicversion.loc)
        self.assertEqual(None, self.aicversion.func_type)
        self.assertEqual(None, self.cost.loc)
        self.assertEqual(None, self.cost.func_type)
        self.assertEqual(0, self.hpa_score.score)
        self.assertEqual(None, self.hpa_score.func_type)


if __name__ == "__main__":
    unittest.main()
