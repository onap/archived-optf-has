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

from conductor.solver.optimizer import decision_path as dpath
from conductor.solver.optimizer import search
from random import randint

LOG = log.getLogger(__name__)


class RandomPick(search.Search):
    def __init__(self, conf):
        search.Search.__init__(self, conf)

    def search(self, _demand_list, _request):

        decision_path = dpath.DecisionPath()
        decision_path.set_decisions({})

        return self._find_current_best(_demand_list, decision_path, _request)

    def _find_current_best(self, _demand_list, _decision_path, _request):

        self.triageSolver.getSortedDemand(_demand_list)
        for demand in _demand_list:
            # apply the constraints on all candidates first
            _decision_path.current_demand = demand
            candidate_list = self._solve_constraints(_decision_path, _request)

            # When you have two demands and for one there are no candidates left after filtering by constraints
            # the code tries to randomly choose index randint(0, -1) what raises an exception. None is returned
            # in order to prevent that and this case is considered in the Optimizer respectively
            if len(candidate_list) > 0:
                # random pick one candidate
                r_index = randint(0, len(candidate_list) - 1)
                best_resource = candidate_list[r_index]
                _decision_path.decisions[demand.name] = best_resource
            else:
                return None

        return _decision_path
