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

from conductor.i18n import _LI
from conductor.solver.optimizer.constraints import constraint
from conductor.solver.utils.utils import OPERATIONS
from oslo_log import log

LOG = log.getLogger(__name__)


class Threshold(constraint.Constraint):

    def __init__(self, _name, _type, _demand_list, _priority=0,
                 _properties=None):
        constraint.Constraint.__init__(
            self, _name, _type, _demand_list, _priority)
        self.properties_list = _properties.get('evaluate')

    def solve(self, _decision_path, _candidate_list, _request):

        conflict_list = list()
        demand_name = _decision_path.current_demand.name

        LOG.info(_LI("Solving constraint {} of type '{}' for demand - [{}]").format(
            self.name, self.constraint_type, demand_name))

        for candidate in _candidate_list:
            for prop in self.properties_list:
                attribute = prop.get('attribute')
                threshold = prop.get('threshold')
                operation = OPERATIONS.get(prop.get('operator'))

                attribute_value = candidate.get(attribute)
                if not attribute_value or not operation(attribute_value, threshold):
                    conflict_list.append(candidate)
                    break

        filtered_candidates = [c for c in _candidate_list if c not in conflict_list]

        return filtered_candidates