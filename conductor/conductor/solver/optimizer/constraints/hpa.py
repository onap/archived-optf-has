#!/usr/bin/env python
#
# -------------------------------------------------------------------------
#   Copyright (c) 2018 Intel Corporation Intellectual Property
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

'''Solver class for constraint type hpa
   Hardware Platform Awareness (HPA) constraint plugin'''

# python imports

from conductor.i18n import _LE, _LI
# Conductor imports
from conductor.solver.optimizer.constraints import constraint
# Third-party library imports
from oslo_log import log

LOG = log.getLogger(__name__)


class HPA(constraint.Constraint):
    def __init__(self, _name, _type, _demand_list, _priority=0,
                 _properties=None):
        constraint.Constraint.__init__(
            self, _name, _type, _demand_list, _priority)
        self.properties = _properties

    def solve(self, _decision_path, _candidate_list, _request):
        '''
        Solver for HPA constraint type.
        :param _decision_path: decision tree
        :param _candidate_list: List of candidates
        :param _request: solver request
        :return: candidate_list with hpa features and flavor label mapping
        '''
        # call conductor engine with request parameters
        cei = _request.cei
        demand_name = _decision_path.current_demand.name
        LOG.info(_LI("Solving constraint type '{}' for demand - [{}]").format(
            self.constraint_type, demand_name))
        vm_label_list = self.properties.get('evaluate')
        for vm_demand in vm_label_list:
            label_name = vm_demand['flavorLabel']
            flavorProperties = vm_demand['flavorProperties']
            response = (cei.get_candidates_with_hpa(label_name,
                                                    _candidate_list,
                                                    flavorProperties))
            if response:
                _candidate_list = response
            else:
                LOG.error(_LE("No matching candidates for HPA exists").format(
                    label_name))
                _candidate_list = response
                break
                # No need to continue.

        return _candidate_list
