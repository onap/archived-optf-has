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

from operator import itemgetter
from oslo_log import log

from conductor.solver.optimizer import decision_path as dpath
from conductor.solver.triage_tool.triage_data import TriageData

LOG = log.getLogger(__name__)


class Search(object):

    def __init__(self, conf):
        self.conf = conf
        self.triageSolver = TriageData()

    def search(self, _demand_list, _objective):
        decision_path = dpath.DecisionPath()
        decision_path.set_decisions({})

        ''' implement search algorithm '''

        return decision_path

    def _solve_constraints(self, _decision_path, _request):
        candidate_list = []
        solver={}
        for key in _decision_path.current_demand.resources:
            resource = _decision_path.current_demand.resources[key]
            candidate_list.append(resource)
        self.assignNodeId(candidate_list, _decision_path.current_demand.name)
        self.triageSolver.aasignNodeIdToCandidate(candidate_list, _decision_path.current_demand, _request.request_id,
                                                  _request.plan_id)

        for constraint in _decision_path.current_demand.constraint_list:
            LOG.debug("Evaluating constraint = {}".format(constraint.name))
            LOG.debug("Available candidates before solving "
                      "constraint {}".format(candidate_list))
            candidates_before = candidate_list

            solver['candidate_before_list'] = candidate_list
            candidate_list =\
                constraint.solve(_decision_path, candidate_list, _request)
            LOG.debug("Available candidates after solving "
                      "constraint {}".format(candidate_list))
            solver['constraint_name_for_can'] = constraint.name
            solver['solver_demand_name'] = _decision_path.current_demand.name
            solver['candidate_after_list']=candidate_list
            candidate_after = candidate_list
            if len(candidate_list) == 0:
                LOG.error("No candidates found for demand {} "
                          "when constraint {} was evaluated "
                          "".format(_decision_path.current_demand,
                                    constraint.name)
                          )
                self.dropped_candidate( solver['candidate_before_list'], candidate_after, constraint.name, _decision_path.current_demand.name)
                break
            self.dropped_candidate(solver['candidate_before_list'], candidate_after, constraint.name,
                                   _decision_path.current_demand.name)
            self.triageSolver.checkCandidateAfter(solver)

        if len(candidate_list) > 0:
            self._set_candidate_cost(candidate_list)
        return candidate_list

    def _set_candidate_cost(self, _candidate_list):
        _candidate_list[:] = sorted(_candidate_list, key=itemgetter("cost"))
    def dropped_candidate(self,candidates_before, candidate_after, constraint_name, demand_name):
        dropped_candidate = []
        for dc in candidates_before:
            if dc not in candidate_after:
                dropped_details={}
                dropped_details['constraint_name_dropped'] = constraint_name
                dropped_details['name'] = demand_name
                dc['constraints'].append(dropped_details)
                dropped_candidate.append(dc)
        self.triageSolver.droppedCadidatesStatus(dropped_candidate)
    def assignNodeId(self, candidate_list, demand_name):
        for cr in candidate_list:
            if not 'node_id' in cr:
                cr['name'] = demand_name
                cr['node_id'] = (demand_name + '|' + cr['candidate_id'])
                cr['constraints'] = []
    def print_decisions(self, _best_path):
        if _best_path:
            msg = "--- demand = {}, chosen resource = {} at {}"
            for demand_name in _best_path.decisions:
                resource = _best_path.decisions[demand_name]
                if 'location_id' in resource:
                    LOG.debug(msg.format(demand_name, resource["candidate_id"],
                                         resource["location_id"]))

            msg = "--- total value of decision = {}"
            LOG.debug(msg.format(_best_path.total_value))
            msg = "--- total cost of decision = {}"
            LOG.debug(msg.format(_best_path.total_cost))


