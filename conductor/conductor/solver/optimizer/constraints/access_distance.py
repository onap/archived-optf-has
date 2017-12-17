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


class AccessDistance(constraint.Constraint):
    def __init__(self, _name, _type, _demand_list, _priority=0,
                 _comparison_operator=operator.le,
                 _threshold=None, _location=None):
        constraint.Constraint.__init__(
            self, _name, _type, _demand_list, _priority)

        # The distance threshold for the constraint
        self.distance_threshold = _threshold
        # The comparison operator from the constraint.
        self.comparison_operator = _comparison_operator
        # This has to be reference to a function
        # from the python operator class
        self.location = _location  # Location instance

    def solve(self, _decision_path, _candidate_list, _request):
        if _candidate_list is None:
            LOG.debug("Empty candidate list, need to get " +
                      "the candidate list for the demand/service")
            return _candidate_list
        conflict_list = []
        cei = _request.cei
        for candidate in _candidate_list:
            air_distance = utils.compute_air_distance(
                self.location.value,
                cei.get_candidate_location(candidate))
            if not self.comparison_operator(air_distance,
                                            self.distance_threshold):
                if candidate not in conflict_list:
                    conflict_list.append(candidate)

        _candidate_list = \
            [c for c in _candidate_list if c not in conflict_list]
        # self.distance_threshold
        # cei = _request.constraint_engine_interface
        # _candidate_list = \
        #     [candidate for candidate in _candidate_list if \
        #     (self.comparison_operator(
        #          utils.compute_air_distance(self.location.value,
        #              cei.get_candidate_location(candidate)),
        #          self.distance_threshold))]

        # # This section may be relevant ONLY when the candidate list
        # # of two demands are identical and we want to optimize the solver
        # # to winnow the candidate list of the current demand based on
        # # whether this constraint will be met for other demands
        #
        # # local candidate list
        # tmp_candidate_list = copy.deepcopy(_candidate_list)
        # for candidate in tmp_candidate_list:
        #     # TODO(snarayanan): Check if the location type matches
        #     # the candidate location type
        #     # if self.location.loc_type != candidate_location.loc_type:
        #     #    LOG.debug("Mismatch in the location types being compared.")
        #
        #
        #     satisfies_all_demands = True
        #     for demand in self.demand_list:
        #         # Ideally candidate should be in resources for
        #         # current demand if the candidate list is generated
        #         # from the demand.resources
        #         # However, this may not be guaranteed for other demands.
        #         if candidate not in demand.resources:
        #             LOG.debug("Candidate not in the demand's resources")
        #             satisfies_all_demands = False
        #             break
        #
        #         candidate_location = demand.resources[candidate].location
        #
        #         if not self.comparison_operator(utils.compute_air_distance(
        #                 self.location.value, candidate_location),
        #                  self.distance_threshold):
        #             # can we assume that the type of candidate_location
        #             # will be compatible with location.value ?
        #             satisfies_all_demands = False
        #             break
        #
        #     if not satisfies_all_demands:
        #         _candidate_list.remove(candidate)

        return _candidate_list
