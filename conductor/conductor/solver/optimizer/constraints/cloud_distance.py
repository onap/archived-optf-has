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


import operator
from oslo_log import log

from conductor.solver.optimizer.constraints import constraint
from conductor.solver.utils import utils

LOG = log.getLogger(__name__)


class CloudDistance(constraint.Constraint):
    def __init__(self, _name, _type, _demand_list, _priority=0,
                 _comparison_operator=operator.le, _threshold=None):
        constraint.Constraint.__init__(
            self, _name, _type, _demand_list, _priority)
        self.distance_threshold = _threshold
        self.comparison_operator = _comparison_operator
        if len(_demand_list) <= 1:
            LOG.debug("Insufficient number of demands.")
            raise ValueError

    def solve(self, _decision_path, _candidate_list, _request):
        conflict_list = []

        # get the list of candidates filtered from the previous demand
        solved_demands = list()  # demands that have been solved in the past
        decision_list = list()
        future_demands = list()  # demands that will be solved in future

        # LOG.debug("initial candidate list {}".format(_candidate_list.name))

        # find previously made decisions for the constraint's demand list
        for demand in self.demand_list:
            # decision made for demand
            if demand in _decision_path.decisions:
                solved_demands.append(demand)
                # only one candidate expected per demand in decision path
                decision_list.append(
                    _decision_path.decisions[demand])
            else:  # decision will be made in future
                future_demands.append(demand)
                # placeholder for any optimization we may
                # want to do for demands in the constraint's demand
                # list that conductor will solve in the future

        # LOG.debug("decisions = {}".format(decision_list))

        # temp copy to iterate
        # temp_candidate_list = copy.deepcopy(_candidate_list)
        # for candidate in temp_candidate_list:
        for candidate in _candidate_list:
            # check if candidate satisfies constraint
            # for all relevant decisions thus far
            is_candidate = True
            for filtered_candidate in decision_list:
                cei = _request.cei
                if not self.comparison_operator(
                        utils.compute_air_distance(
                            cei.get_candidate_location(candidate),
                            cei.get_candidate_location(filtered_candidate)),
                        self.distance_threshold):
                    is_candidate = False

            if not is_candidate:
                if candidate not in conflict_list:
                    conflict_list.append(candidate)

        _candidate_list = \
            [c for c in _candidate_list if c not in conflict_list]

        # msg = "final candidate list for demand {} is "
        # LOG.debug(msg.format(_decision_path.current_demand.name))
        # for c in _candidate_list:
        #    LOG.debug("    " + c.name)

        return _candidate_list
