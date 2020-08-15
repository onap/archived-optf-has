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

import unittest

from conductor.solver.optimizer.decision_path import DecisionPath
from conductor.solver.request.parser import Parser
from conductor.solver.request.functions.attribute import Attribute


class TestAttribute(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_attribute(self):
        candidate = {"canidate_id": "1234",
                     "candidate_type": "nsi",
                     "latency": 5,
                     "reliability": 99.9}
        decisions = {"urllc": candidate}
        decision_path = DecisionPath()
        decision_path.decisions = decisions
        params = {"demand": "urllc",
                  "attribute": "latency"}
        attribute = Attribute("attribute")
        args = attribute.get_args_from_params(decision_path, Parser(), params)
        self.assertEqual(5, attribute.compute(*args))
