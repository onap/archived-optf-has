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

from conductor.i18n import _LE
from conductor.solver.optimizer.constraints import constraint

LOG = log.getLogger(__name__)


class Service(constraint.Constraint):
    def __init__(self, _name, _type, _demand_list, _priority=0,
                 _controller=None, _request=None, _cost=None,
                 _inventory_type=None):
        constraint.Constraint.__init__(
            self, _name, _type, _demand_list, _priority)
        if _controller is None:
            LOG.debug("Provider URL not available")
            raise ValueError
        self.request = _request
        self.controller = _controller
        self.cost = _cost
        self.inventory_type = _inventory_type

    def solve(self, _decision_path, _candidate_list, _request):
        select_list = list()
        candidates_to_check = list()
        demand_name = _decision_path.current_demand.name
        # service-check candidates of the same inventory type
        # select candidate of all other types
        for candidate in _candidate_list:
            if self.inventory_type == "cloud":
                if candidate["inventory_type"] == "cloud":
                    candidates_to_check.append(candidate)
                else:
                    select_list.append(candidate)
            elif self.inventory_type == "service":
                if candidate["inventory_type"] == "service":
                    candidates_to_check.append(candidate)
                else:
                    select_list.append(candidate)
        # call conductor data with request parameters
        if len(candidates_to_check) > 0:
            cei = _request.cei
            filtered_list = cei.get_candidates_from_service(
                self.name, self.constraint_type, candidates_to_check,
                self.controller, self.inventory_type, self.request,
                self.cost, demand_name)
            for c in filtered_list:
                select_list.append(c)
        else:
            LOG.error(_LE("Constraint {} ({}) has no candidates of "
                          "inventory type {} for demand {}").format(
                self.name, self.constraint_type,
                self.inventory_type, demand_name)
            )

        _candidate_list[:] = [c for c in _candidate_list if c in select_list]
        return _candidate_list
