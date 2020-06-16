#
# -------------------------------------------------------------------------
#   Copyright (C) 2020 Wipro Limited.
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

import json
import unittest
from conductor.solver.optimizer.constraints.threshold import Threshold
from conductor.solver.optimizer.decision_path import DecisionPath
from conductor.solver.request.demand import Demand


class TestThreshold(unittest.TestCase):

    def test_solve(self):

        candidates_file = './conductor/tests/unit/data/plugins/inventory_provider/nssi_candidate.json'
        candidates = json.loads(open(candidates_file).read())
        # test 1
        properties = {'evaluate':
                          [{'attribute': 'latency', 'threshold': 30, 'operator': 'lte'},
                           {'attribute': 'exp_data_rate_ul', 'threshold': 70, 'operator': 'gte'}]}

        threshold_obj = Threshold('urllc_threshold', 'threshold', ['URLLC'], _priority=0,
                                  _properties=properties)

        decision_path = DecisionPath()
        decision_path.current_demand = Demand('URLLC')

        self.assertEqual(candidates, threshold_obj.solve(decision_path, candidates, None))

        # test 2
        properties = {'evaluate':
                          [{'attribute': 'latency', 'threshold': 10, 'operator': 'lte'},
                           {'attribute': 'exp_data_rate_ul', 'threshold': 120, 'operator': 'gte'}]}

        threshold_obj = Threshold('urllc_threshold', 'threshold', ['URLLC'], _priority=0,
                                  _properties=properties)

        self.assertEqual([], threshold_obj.solve(decision_path, candidates, None))

        # test 3
        properties = {'evaluate':
                          [{'attribute': 'latency', 'threshold': 10, 'operator': 'lte'},
                           {'attribute': 'area_traffic_cap', 'threshold': 120, 'operator': 'gte'}]}

        threshold_obj = Threshold('urllc_threshold', 'threshold', ['URLLC'], _priority=0,
                                  _properties=properties)

        self.assertEqual([], threshold_obj.solve(decision_path, candidates, None))


if __name__ == "__main__":
    unittest.main()
