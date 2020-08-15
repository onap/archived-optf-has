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
import os
import unittest

from conductor.solver.optimizer.decision_path import DecisionPath
from conductor.solver.request.objective_v2 import ObjectiveV2
from conductor.solver.request.parser import Parser

BASE_DIR = os.path.dirname(__file__)


class TestObjectiveV2(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(BASE_DIR, 'objective.json'), 'r') as obj:
            self.objective_functions = json.loads(obj.read())

    def tearDown(self):
        pass

    def test_objective(self):

        expected = [10, 0.6]
        candidate_core = {"candidate_id": "12345",
                          "candidate_type": "nssi",
                          "latency": 10,
                          "throughput": 200}
        candidate_ran = {"candidate_id": "12345",
                         "candidate_type": "nssi",
                         "latency": 15,
                         "throughput": 300}
        candidate_transport = {"candidate_id": "12345",
                               "candidate_type": "nssi",
                               "latency": 8,
                               "throughput": 400}

        decisions = {"urllc_core": candidate_core,
                     "urllc_ran": candidate_ran,
                     "urllc_transport": candidate_transport}

        decision_path = DecisionPath()
        decision_path.decisions = decisions
        request = Parser()

        actual = []
        for objective_function in self.objective_functions:
            objective_v2 = ObjectiveV2(objective_function)
            objective_v2.compute(decision_path, request)
            actual.append(decision_path.cumulated_value)

        self.assertEqual(expected, actual)

