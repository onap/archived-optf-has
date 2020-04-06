#
# -------------------------------------------------------------------------
#   Copyright (c) 2015-2018 AT&T Intellectual Property
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

from conductor.solver.request import demand
from conductor.solver.utils.utils import OPT_OPERATIONS
# from conductor.solver.resource import region
# from conductor.solver.resource import service


class Objective(object):

    def __init__(self):
        self.goal = None
        self.operation = None
        self.operand_list = []

    def compute(self, _decision_path, _request):
        value = 0.0

        for op in self.operand_list:
            value = OPT_OPERATIONS.get(self.operation)(value, op.compute(_decision_path, _request))

        _decision_path.cumulated_value = value
        _decision_path.total_value = \
            _decision_path.cumulated_value + \
            _decision_path.heuristic_to_go_value


class Operand(object):

    def __init__(self):
        self.operation = None
        self.weight = 0
        self.function = None

    def compute(self, _decision_path, _request):
        value = 0.0
        cei = _request.cei
        if self.function.func_type == "latency_between":
            if isinstance(self.function.loc_a, demand.Location):
                if self.function.loc_z.name in \
                        list(_decision_path.decisions.keys()):    # Python 3 Conversion -- dict object to list object
                    resource = \
                        _decision_path.decisions[self.function.loc_z.name]
                    candidate_cost = resource.get('cost')
                    loc = None
                    # if isinstance(resource, region.Region):
                    #     loc = resource.location
                    # elif isinstance(resource, service.Service):
                    #     loc = resource.region.location
                    loc = cei.get_candidate_location(resource)
                    value = \
                        self.function.compute(self.function.loc_a.value, loc) \
                        + candidate_cost
            elif isinstance(self.function.loc_z, demand.Location):
                if self.function.loc_a.name in \
                        list(_decision_path.decisions.keys()):    # Python 3 Conversion -- dict object to list object
                    resource = \
                        _decision_path.decisions[self.function.loc_a.name]
                    candidate_cost = resource.get('cost')
                    loc = None
                    # if isinstance(resource, region.Region):
                    #    loc = resource.location
                    # elif isinstance(resource, service.Service):
                    #    loc = resource.region.location
                    loc = cei.get_candidate_location(resource)
                    value = \
                        self.function.compute(self.function.loc_z.value, loc) \
                        + candidate_cost
            else:
                if self.function.loc_a.name in \
                        list(_decision_path.decisions.keys()) and \
                   self.function.loc_z.name in \
                        list(_decision_path.decisions.keys()):  # Python 3 Conversion -- dict object to list object
                    resource_a = \
                        _decision_path.decisions[self.function.loc_a.name]
                    loc_a = None
                    # if isinstance(resource_a, region.Region):
                    #     loc_a = resource_a.location
                    # elif isinstance(resource_a, service.Service):
                    #     loc_a = resource_a.region.location
                    loc_a = cei.get_candidate_location(resource_a)
                    resource_z = \
                        _decision_path.decisions[self.function.loc_z.name]
                    loc_z = None
                    # if isinstance(resource_z, region.Region):
                    #     loc_z = resource_z.location
                    # elif isinstance(resource_z, service.Service):
                    #     loc_z = resource_z.region.location
                    loc_z = cei.get_candidate_location(resource_z)

                    value = self.function.compute(loc_a, loc_z)

        elif self.function.func_type == "hpa_score":
            # Currently only minimize objective goal is supported
            # Higher the HPA score the better.
            # Invert HPA Score if goal is minimize
            invert = -1
            #
            # if self.function.goal == "max":
            #     invert = 1
            for demand_name, candidate_info in _decision_path.decisions.items():
                hpa_score = invert * float(candidate_info.get('hpa_score', 0))
                value += hpa_score

        elif self.function.func_type == "distance_between":
            if isinstance(self.function.loc_a, demand.Location):
                if self.function.loc_z.name in \
                        list(_decision_path.decisions.keys()):   # Python 3 Conversion -- dict object to list object
                    resource = \
                        _decision_path.decisions[self.function.loc_z.name]
                    candidate_cost = resource.get('cost')
                    loc = None
                    # if isinstance(resource, region.Region):
                    #     loc = resource.location
                    # elif isinstance(resource, service.Service):
                    #     loc = resource.region.location
                    loc = cei.get_candidate_location(resource)
                    value = \
                        self.function.compute(self.function.loc_a.value, loc) \
                        + candidate_cost
            elif isinstance(self.function.loc_z, demand.Location):
                if self.function.loc_a.name in \
                        list(_decision_path.decisions.keys()):    # Python 3 Conversion -- dict object to list object
                    resource = \
                        _decision_path.decisions[self.function.loc_a.name]
                    candidate_cost = resource.get('cost')
                    loc = None
                    # if isinstance(resource, region.Region):
                    #    loc = resource.location
                    # elif isinstance(resource, service.Service):
                    #    loc = resource.region.location
                    loc = cei.get_candidate_location(resource)
                    value = \
                        self.function.compute(self.function.loc_z.value, loc) \
                        + candidate_cost
            else:
                if self.function.loc_a.name in \
                        list(_decision_path.decisions.keys()) and \
                   self.function.loc_z.name in \
                        list(_decision_path.decisions.keys()):    # Python 3 Conversion -- dict object to list object
                    resource_a = \
                        _decision_path.decisions[self.function.loc_a.name]
                    loc_a = None
                    # if isinstance(resource_a, region.Region):
                    #     loc_a = resource_a.location
                    # elif isinstance(resource_a, service.Service):
                    #     loc_a = resource_a.region.location
                    loc_a = cei.get_candidate_location(resource_a)
                    resource_z = \
                        _decision_path.decisions[self.function.loc_z.name]
                    loc_z = None
                    # if isinstance(resource_z, region.Region):
                    #     loc_z = resource_z.location
                    # elif isinstance(resource_z, service.Service):
                    #     loc_z = resource_z.region.location
                    loc_z = cei.get_candidate_location(resource_z)

                    value = self.function.compute(loc_a, loc_z)

        elif self.function.func_type == "attribute":
            if self.function.demand in _decision_path.decisions:
                resource = _decision_path.decisions[self.function.demand]
                value = self.function.compute(resource)

        if self.operation == "product":
            value *= self.weight

        return value
