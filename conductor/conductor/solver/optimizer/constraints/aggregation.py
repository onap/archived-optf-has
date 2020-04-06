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

from conductor.solver.optimizer.constraints import constraint
from conductor.solver.utils.utils import AGGREGATION_FUNCTIONS, OPERATIONS


class CrossDemandAttributeAggregation(constraint.Constraint):
    def __init__(self, _name, _type, _demand_list, _priority=0, _properties=None):
        constraint.Constraint.__init__(
            self, _name, _type, _demand_list, _priority)
        self.properties = _properties.get('evaluate')

    def solve(self, _decision_path, _candidate_list, _request):
        conflict_list = []

        # get the list of candidates filtered from the previous demand
        solved_demands = list()  # demands that have been solved in the past
        decision_list = list()
        future_demands = list()  # demands that will be solved in future

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
        if len(future_demands) == 1:
            for candidate in _candidate_list:
                # check if candidate satisfies constraint
                # for all relevant decisions thus far
                is_candidate = True
                temp_decision_list = decision_list.copy()
                temp_decision_list.append(candidate)

                for prop in self.properties:

                    attribute = prop.get('attribute')
                    aggregate_function = AGGREGATION_FUNCTIONS.get(prop.get('function'))
                    operation = OPERATIONS.get(prop.get('operator'))
                    threshold = prop.get('threshold')

                    attribute_list = [x.get(attribute) for x in temp_decision_list]

                    if not operation(aggregate_function(attribute_list), threshold):
                        is_candidate = False
                        continue

                if not is_candidate:
                    if candidate not in conflict_list:
                        conflict_list.append(candidate)

            _candidate_list = \
                [c for c in _candidate_list if c not in conflict_list]

        return _candidate_list
