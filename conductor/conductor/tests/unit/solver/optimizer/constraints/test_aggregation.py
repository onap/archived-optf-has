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

from conductor.solver.optimizer.constraints.aggregation import Aggregation
from conductor.solver.optimizer.decision_path import DecisionPath
from conductor.solver.request.demand import Demand


class TestAggregation(unittest.TestCase):

    def test_solve(self):
        candidates_file = './conductor/tests/unit/data/plugins/' \
                          'inventory_provider/nssi_candidate.json'
        candidates = json.loads(open(candidates_file).read())

        ran_candidate1 = {"candidate_id": "123",
                          "latency": 15}

        ran_candidate2 = {"candidate_id": "456",
                          "latency": 5}

        decision_path = DecisionPath()
        decision_path.current_demand = Demand('URLLC')
        decision_path.decisions = {}

        properties = {'evaluate': [{'attribute': 'latency', 'threshold': 30, 'operator': 'lte',
                      'function': 'sum'}]}

        aggregation_obj = Aggregation('urllc_aggregation', 'aggregation', ['URLLC', 'ran'],
                                      _priority=0, _properties=properties)

        self.assertEqual(candidates, aggregation_obj.solve(decision_path, candidates, None))

        decision_path.decisions = {"ran": ran_candidate1}

        self.assertEqual([], aggregation_obj.solve(decision_path, candidates, None))

        decision_path.decisions = {"ran": ran_candidate2}

        self.assertEqual(candidates, aggregation_obj.solve(decision_path, candidates, None))

        properties = {'evaluate': [{'attribute': 'latency', 'threshold': 10, 'operator': 'lte',
                      'function': 'sum'}]}

        decision_path.decisions = {}

        aggregation_obj = Aggregation('urllc_aggregation', 'aggregation', ['URLLC', 'ran'],
                                      _priority=0, _properties=properties)

        self.assertEqual([], aggregation_obj.solve(decision_path, candidates, None))


if __name__ == '__main__':
    unittest.main()
