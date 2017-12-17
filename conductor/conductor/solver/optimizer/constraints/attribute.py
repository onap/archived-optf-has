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


# python imports

# Conductor imports
from conductor.solver.optimizer.constraints import constraint

# Third-party library imports
from oslo_log import log

LOG = log.getLogger(__name__)


class Attribute(constraint.Constraint):
    def __init__(self, _name, _type, _demand_list, _priority=0,
                 _properties=None):
        constraint.Constraint.__init__(
            self, _name, _type, _demand_list, _priority)
        self.properties = _properties

    def solve(self, _decision_path, _candidate_list, _request):
        # call conductor engine with request parameters
        cei = _request.cei
        demand_name = _decision_path.current_demand.name
        select_list = cei.get_candidates_by_attributes(demand_name,
                                                       _candidate_list,
                                                       self.properties)
        _candidate_list[:] = \
            [c for c in _candidate_list if c in select_list]
        return _candidate_list
