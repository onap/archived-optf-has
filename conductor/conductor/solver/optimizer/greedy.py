#!/bin/python
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


from oslo_log import log
import sys

from conductor.solver.optimizer import decision_path as dpath
from conductor.solver.optimizer import search

LOG = log.getLogger(__name__)


class Greedy(search.Search):

    def __init__(self, conf):
        search.Search.__init__(self, conf)

    def search(self, _demand_list, _objective):
        decision_path = dpath.DecisionPath()
        decision_path.set_decisions({})

        for demand in _demand_list:
            LOG.debug("demand = {}".format(demand.name))

            decision_path.current_demand = demand
            candidate_list = self._solve_constraints(decision_path)

            bound_value = 0.0
            if _objective.goal == "min":
                bound_value = sys.float_info.max

            best_resource = None
            for candidate in candidate_list:
                decision_path.decisions[demand.name] = candidate
                _objective.compute(decision_path)
                if _objective.goal == "min":
                    if decision_path.total_value < bound_value:
                        bound_value = decision_path.total_value
                        best_resource = candidate
                elif _objective.goal == "max":
                    if decision_path.total_value > bound_value:
                        bound_value = decision_path.total_value
                        best_resource = candidate

            if best_resource is not None:
                decision_path.decisions[demand.name] = best_resource
                decision_path.total_value = bound_value
            else:
                return None

        return decision_path
