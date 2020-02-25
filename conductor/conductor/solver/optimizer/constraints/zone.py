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

from .constraint import Constraint # Python 3 import statement relative imports

LOG = log.getLogger(__name__)


class Zone(Constraint):
    def __init__(self, _name, _type, _demand_list, _priority=0,
                 _qualifier=None, _category=None,  _location=None):
        Constraint.__init__(self, _name, _type, _demand_list, _priority)

        self.qualifier = _qualifier  # different or same
        self.category = _category  # disaster, region, or update
        self.location = _location
        self.comparison_operator = None

        if self.qualifier == "same":
            self.comparison_operator = operator.eq
        elif self.qualifier == "different":
            self.comparison_operator = operator.ne

    def solve(self, _decision_path, _candidate_list, _request):
        conflict_list = []

        decision_list = list()
        # find previously made decisions for the constraint's demand list
        for demand in self.demand_list:
            # decision made for demand
            if demand in _decision_path.decisions:
                decision_list.append(_decision_path.decisions[demand])
        # temp copy to iterate
        # temp_candidate_list = copy.deepcopy(_candidate_list)
        # for candidate in temp_candidate_list:
        for candidate in _candidate_list:
            # check if candidate satisfies constraint
            # for all relevant decisions thus far
            is_candidate = True
            cei = _request.cei

            # TODO(larry): think of an other way to handle this special case
            if self.location and self.category == 'country':
                if not self.comparison_operator(
                        cei.get_candidate_zone(candidate, self.category),
                        self.location.country):
                    is_candidate = False
            for filtered_candidate in decision_list:
                if not self.comparison_operator(
                        cei.get_candidate_zone(candidate, self.category),
                        cei.get_candidate_zone(filtered_candidate,
                                               self.category)):
                    is_candidate = False

            if not is_candidate:
                if candidate not in conflict_list:
                    conflict_list.append(candidate)
                    # _candidate_list.remove(candidate)

        _candidate_list[:] =\
            [c for c in _candidate_list if c not in conflict_list]

        # msg = "final candidate list for demand {} is "
        # LOG.debug(msg.format(_decision_path.current_demand.name))
        # for c in _candidate_list:
        #     print "    " + c.name

        return _candidate_list
