#
# -------------------------------------------------------------------------
#   Copyright (c) 2015-2017 AT&T Intellectual Property
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

from oslo_log import log
import sys
import time

from conductor.solver.optimizer import decision_path as dpath
from conductor.solver.optimizer import search

LOG = log.getLogger(__name__)


class FitFirst(search.Search):

    def __init__(self, conf):
        search.Search.__init__(self, conf)

    def search(self, _demand_list, _objective, _request):
        decision_path = dpath.DecisionPath()
        decision_path.set_decisions({})

        _begin_time = int(round(time.time()))

        # Begin the recursive serarch
        return self._find_current_best(
            _demand_list, _objective, decision_path, _request, _begin_time)

    def _find_current_best(self, _demand_list, _objective,
                           _decision_path, _request, _begin_time):

        self.triageSolver.getSortedDemand(_demand_list)
        # Termination condition:
        # when order takes a long time to solve (more than 'timeout' value)
        # then jump out of the recursion
        if (int(round(time.time())) - _begin_time) > \
                self.conf.solver.solver_timeout:
            return None

        # _demand_list is common across all recursions
        if len(_demand_list) == 0:
            LOG.debug("search done")
            return _decision_path

        # get next demand to resolve
        demand = _demand_list.pop(0)
        LOG.debug("demand = {}".format(demand.name))
        _decision_path.current_demand = demand

        # call constraints to whittle initial candidates
        # candidate_list meets all constraints for the demand
        candidate_list = self._solve_constraints(_decision_path, _request)
        # find the best candidate among the list

        # bound_value keeps track of the max value discovered
        # thus far for the _decision_path. For every demand
        # added to the _decision_path bound_value will be set
        # to a really large value to begin with
        bound_value = 0.0
        version_value = "0.0"

        if "min" in _objective.goal:
            bound_value = sys.float_info.max

        # Start recursive search
        while True:
            best_resource = None
            # Find best candidate that optimizes the cost for demand.
            # The candidate list can be empty if the constraints
            # rule out all candidates
            for candidate in candidate_list:
                _decision_path.decisions[demand.name] = candidate
                _objective.compute(_decision_path, _request)
                # this will set the total_value of the _decision_path
                # thus far up to the demand
                if _objective.goal is None:
                    best_resource = candidate

                elif _objective.goal == "min_aic":
                    # convert the unicode to string
                    candidate_version = candidate \
                        .get("cloud_region_version").encode('utf-8')
                    if _decision_path.total_value < bound_value or \
                            (_decision_path.total_value == bound_value and self._compare_version(candidate_version,
                                                                                                 version_value) > 0):
                        bound_value = _decision_path.total_value
                        version_value = candidate_version
                        best_resource = candidate

                elif _objective.goal == "min":
                    # if the path value is less than bound value
                    # we have found the better candidate
                    if _decision_path.total_value < bound_value:
                        # relax the bound_value to the value of
                        # the path - this will ensure a future
                        # candidate will be picked only if it has
                        # a value lesser than the current best candidate
                        bound_value = _decision_path.total_value
                        best_resource = candidate

                elif _objective.goal == "max":
                    if _decision_path.total_value > bound_value:
                        bound_value = _decision_path.total_value
                        best_resource = candidate

            # Rollback if we don't have any candidate picked for
            # the demand.
            if best_resource is None:
                LOG.debug("no resource, rollback")
                # Put the current demand (which failed to find a
                # candidate) back in the list so that it can be picked
                # up in the next iteration of the recursion
                _demand_list.insert(0, demand)
                self.triageSolver.rollBackStatus(_decision_path.current_demand, _decision_path)
                return None  # return None back to the recursion
            else:
                # best resource is found, add to the decision path
                _decision_path.decisions[demand.name] = best_resource
                _decision_path.total_value = bound_value

                # Begin the next recursive call to find candidate
                # for the next demand in the list
                decision_path = self._find_current_best(
                    _demand_list, _objective, _decision_path, _request, _begin_time)

                # The point of return from the previous recursion.
                # If the call returns no candidates, no solution exists
                # in that path of the decision tree. Rollback the
                # current best_resource and remove it from the list
                # of potential candidates.
                if decision_path is None:
                    candidate_list.remove(best_resource)
                    # reset bound_value to a large value so that
                    # the next iteration of the current recursion
                    # will pick the next best candidate, which
                    # will have a value larger than the current
                    # bound_value (proof by contradiction:
                    # it cannot have a smaller value, if it wasn't
                    # the best_resource.
                    if "min" in _objective.goal:
                        bound_value = sys.float_info.max
                        version_value = "0.0"
                else:
                    # A candidate was found for the demand, and
                    # was added to the decision path. Return current
                    # path back to the recursion.
                    return decision_path

    def _compare_version(self, version1, version2):
        version1 = version1.split('.')
        version2 = version2.split('.')
        for i in range(max(len(version1), len(version2))):
            v1 = int(version1[i]) if i < len(version1) else 0
            v2 = int(version2[i]) if i < len(version2) else 0
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
        return 0
