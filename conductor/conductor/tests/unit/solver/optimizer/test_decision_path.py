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

"""Test class for optimizer decision_path.py"""

import unittest
from conductor.solver.optimizer.decision_path import DecisionPath


class TestDecisionPath(unittest.TestCase):

    def setUp(self):
        self.decisionPath = DecisionPath()

    def test_decision_path(self):
        self.assertEqual(0.0, self.decisionPath.cumulated_value)
        self.assertEqual(0.0, self.decisionPath.cumulated_cost)
        self.assertEqual(0.0, self.decisionPath.heuristic_to_go_value)
        self.assertEqual(0.0, self.decisionPath.heuristic_to_go_cost)
        self.assertEqual(0.0, self.decisionPath.total_value)
        self.assertEqual(0.0, self.decisionPath.total_cost)


if __name__ == '__main__':
    unittest.main()
