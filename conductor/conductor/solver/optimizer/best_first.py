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
import operator
from oslo_log import log
import sys

from conductor.solver.optimizer import decision_path as dpath
from conductor.solver.optimizer import search

LOG = log.getLogger(__name__)


class BestFirst(search.Search):

    def __init__(self, conf):
        search.Search.__init__(self, conf)

    def search(self, _demand_list, _objective):
        dlist = copy.deepcopy(_demand_list)
        heuristic_solution = self._search_by_fit_first(dlist, _objective)
        if heuristic_solution is None:
            LOG.debug("no solution")
            return None

        open_list = []
        close_paths = {}

        ''' for the decision length heuristic '''
        # current_decision_length = 0

        # create root path
        decision_path = dpath.DecisionPath()
        decision_path.set_decisions({})

        # insert the root path into open_list
        open_list.append(decision_path)

        while len(open_list) > 0:
            p = open_list.pop(0)

            ''' for the decision length heuristic '''
            # dl = len(p.decisions)
            # if dl >= current_decision_length:
            #     current_decision_length = dl
            # else:
            #     continue

            # if explored all demands in p, complete the search with p
            unexplored_demand = self._get_new_demand(p, _demand_list)
            if unexplored_demand is None:
                return p

            p.current_demand = unexplored_demand

            msg = "demand = {}, decisions = {}, value = {}"
            LOG.debug(msg.format(p.current_demand.name,
                                 p.decision_id, p.total_value))

            # constraint solving
            candidate_list = self._solve_constraints(p)
            if len(candidate_list) > 0:
                for candidate in candidate_list:
                    # create path for each candidate for given demand
                    np = dpath.DecisionPath()
                    np.set_decisions(p.decisions)
                    np.decisions[p.current_demand.name] = candidate
                    _objective.compute(np)

                    valid_candidate = True

                    # check closeness for this decision
                    np.set_decision_id(p, candidate.name)
                    if np.decision_id in list(close_paths.keys()):  # Python 3 Conversion -- dict object to list object
                        valid_candidate = False

                    ''' for base comparison heuristic '''
                    # TODO(gjung): how to know this is about min
                    if _objective.goal == "min":
                        if np.total_value >= heuristic_solution.total_value:
                            valid_candidate = False
                    elif _objective.goal == "max":
                        if np.total_value <= heuristic_solution.total_value:
                            valid_candidate = False

                    if valid_candidate is True:
                        open_list.append(np)

                # sort open_list by value
                open_list.sort(key=operator.attrgetter("total_value"))
            else:
                LOG.debug("no candidates")

            # insert p into close_paths
            close_paths[p.decision_id] = p

        return heuristic_solution

    def _get_new_demand(self, _p, _demand_list):
        for demand in _demand_list:
            if demand.name not in list(_p.decisions.keys()):     # Python 3 Conversion -- dict object to list object
                return demand

        return None

    def _search_by_fit_first(self, _demand_list, _objective):
        decision_path = dpath.DecisionPath()
        decision_path.set_decisions({})

        return self._find_current_best(_demand_list, _objective, decision_path)

    def _find_current_best(self, _demand_list, _objective, _decision_path):
        if len(_demand_list) == 0:
            LOG.debug("search done")
            return _decision_path

        demand = _demand_list.pop(0)
        LOG.debug("demand = {}".format(demand.name))
        _decision_path.current_demand = demand
        candidate_list = self._solve_constraints(_decision_path)

        bound_value = 0.0
        if _objective.goal == "min":
            bound_value = sys.float_info.max

        while True:
            best_resource = None
            for candidate in candidate_list:
                _decision_path.decisions[demand.name] = candidate
                _objective.compute(_decision_path)
                if _objective.goal == "min":
                    if _decision_path.total_value < bound_value:
                        bound_value = _decision_path.total_value
                        best_resource = candidate

            if best_resource is None:
                LOG.debug("no resource, rollback")
                return None
            else:
                _decision_path.decisions[demand.name] = best_resource
                _decision_path.total_value = bound_value
                decision_path = self._find_current_best(
                    _demand_list, _objective, _decision_path)
                if decision_path is None:
                    candidate_list.remove(best_resource)
                else:
                    return decision_path
