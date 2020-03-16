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
from oslo_log import log

LOG = log.getLogger(__name__)


class Threshold(constraint.Constraint):

    OPERATIONS = {'gte': lambda x, y: x >= y,
                  'lte': lambda x, y: x <= y,
                  'gt': lambda x, y: x > y,
                  'lt': lambda x, y: x < y,
                  'eq': lambda x, y: x == y
                  }

    def __init__(self, _name, _type, _demand_list, _priority=0,
                 _properties=None):
        constraint.Constraint.__init__(
            self, _name, _type, _demand_list, _priority)
        self.attribute = _properties.get('attribute')
        self.operation = self.OPERATIONS.get(_properties.get('operator'))
        self.threshold = _properties.get('threshold')

    def solve(self, _decision_path, _candidate_list, _request):

        filtered_candidates = list()
        demand_name = _decision_path.current_demand.name

        LOG.info(_LI("Solving constraint type '{}' for demand - [{}]").format(
            self.constraint_type, demand_name))

        for candidate in _candidate_list:
            attribute_value = candidate.get(self.attribute)
            if self.operation(attribute_value, self.threshold):
                filtered_candidates.append(candidate)

        return filtered_candidates





