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


from oslo_log import log

from .constraint import Constraint    # Python 3 import statement relative imports

LOG = log.getLogger(__name__)


class InventoryGroup(Constraint):
    def __init__(self, _name, _type, _demand_list, _priority=0):
        Constraint.__init__(self, _name, _type, _demand_list, _priority)
        if not len(self.demand_list) == 2:
            LOG.debug("More than two demands in the list")
            raise ValueError

    def solve(self, _decision_path, _candidate_list, _request):

        # check if other demand in the demand pair has been already solved
        # other demand in pair
        other_demand = [d for d in self.demand_list if
                        d != _decision_path.current_demand.name][0]
        if other_demand not in _decision_path.decisions:
            LOG.debug("Other demand not yet resolved, " +
                      "return the current candidates")
            return _candidate_list
        # expect only one candidate per demand in decision
        resolved_candidate = _decision_path.decisions[other_demand]
        cei = _request.cei
        inventory_group_candidates = cei.get_inventory_group_candidates(
            _candidate_list,
            _decision_path.current_demand.name,
            resolved_candidate)
        _candidate_list = [candidate for candidate in _candidate_list if
                           (candidate in inventory_group_candidates)]

        '''
        # Alternate implementation that *may* be more efficient
        # if the decision path has multiple candidates per solved demand
        # *and* inventory group is smaller than than the candidate list

        select_list = list()
        # get candidates for current demand
        current_demand = _decision_path.current_demand
        current_candidates = _candidate_list

        # get inventory groups for current demand,
        # assuming that group information is tied with demand
        inventory_groups = cei.get_inventory_groups(current_demand)

        for group in inventory_groups:
            if group[0] in current_candidates and group[1] in other_candidates:
                # is the symmetric candidacy valid too ?
                if group[0] not in select_list:
                    select_list.append(group[0])
        _candidate_list[:] = [c for c in _candidate_list if c in select_list]
        '''

        return _candidate_list
