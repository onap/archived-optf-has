#!/usr/bin/env python
#
# -------------------------------------------------------------------------
#   Copyright (c) 2015-2017 AT&T Intellectual Property
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


import copy


class DecisionPath(object):

    def __init__(self):
        """local copy of decisions so far

        key = demand.name, value = region or service instance
        """

        self.decisions = None

        ''' to identify this decision path in the search '''
        self.decision_id = ""

        ''' current demand to be dealt with'''
        self.current_demand = None

        ''' decision values so far '''
        self.cumulated_value = 0.0
        self.cumulated_cost = 0.0
        self.heuristic_to_go_value = 0.0
        self.heuristic_to_go_cost = 0.0
        # cumulated_value + heuristic_to_go_value (if exist)
        self.total_value = 0.0
        # cumulated_cost + heuristic_to_go_cost (if exist)
        self.total_cost = 0.0

    def set_decisions(self, _prior_decisions):
        self.decisions = copy.deepcopy(_prior_decisions)

    def set_decision_id(self, _dk, _rk):
        self.decision_id += (str(_dk) + ":" + str(_rk) + ">")
