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


# import json
import operator

from oslo_log import log
import random

from conductor.solver.optimizer.constraints \
    import access_distance as access_dist
from conductor.solver.optimizer.constraints \
    import attribute as attribute_constraint
from conductor.solver.optimizer.constraints \
    import aic_distance as aic_dist
from conductor.solver.optimizer.constraints \
    import inventory_group
from conductor.solver.optimizer.constraints \
    import service as service_constraint
from conductor.solver.optimizer.constraints import zone
from conductor.solver.request import demand
from conductor.solver.request.functions import aic_version
from conductor.solver.request.functions import cost
from conductor.solver.request.functions import distance_between
from conductor.solver.request import objective

# from conductor.solver.request.functions import distance_between
# from conductor.solver.request import objective
# from conductor.solver.resource import region
# from conductor.solver.resource import service
# from conductor.solver.utils import constraint_engine_interface as cei
# from conductor.solver.utils import utils

LOG = log.getLogger(__name__)


# FIXME(snarayanan): This is really a SolverRequest (or Request) object
class Parser(object):

    def __init__(self, _region_gen=None):
        self.demands = {}
        self.locations = {}
        self.region_gen = _region_gen
        self.constraints = {}
        self.objective = None
        self.cei = None
        self.request_id = None
        self.request_type = None

    # def get_data_engine_interface(self):
    #    self.cei = cei.ConstraintEngineInterface()

    # FIXME(snarayanan): This should just be parse_template
    def parse_template(self, json_template=None):
        if json_template is None:
            LOG.error("No template specified")
            return "Error"
        # fd = open(self.region_gen.data_path + \
        #     "/../dhv/dhv_test_template.json", "r")
        # fd = open(template, "r")
        # parse_template = json.load(fd)
        # fd.close()

        # get request type
        self.request_type = json_template['conductor_solver']['request_type']

        # get demands
        demand_list = json_template["conductor_solver"]["demands"]
        for demand_id, candidate_list in demand_list.items():
            current_demand = demand.Demand(demand_id)
            # candidate should only have minimal information like location_id
            for candidate in candidate_list["candidates"]:
                candidate_id = candidate["candidate_id"]
                current_demand.resources[candidate_id] = candidate
            current_demand.sort_base = 0  # this is only for testing
            self.demands[demand_id] = current_demand

        # get locations
        location_list = json_template["conductor_solver"]["locations"]
        for location_id, location_info in location_list.items():
            loc = demand.Location(location_id)
            loc.loc_type = "coordinates"
            loc.value = (float(location_info["latitude"]),
                         float(location_info["longitude"]))
            loc.country = location_info['country'] if 'country' in location_info else None
            self.locations[location_id] = loc

        # get constraints
        input_constraints = json_template["conductor_solver"]["constraints"]
        for constraint_id, constraint_info in input_constraints.items():
            constraint_type = constraint_info["type"]
            constraint_demands = list()
            parsed_demands = constraint_info["demands"]
            if isinstance(parsed_demands, list):
                for d in parsed_demands:
                    constraint_demands.append(d)
            else:
                constraint_demands.append(parsed_demands)
            if constraint_type == "distance_to_location":
                c_property = constraint_info.get("properties")
                location_id = c_property.get("location")
                op = operator.le  # default operator
                c_op = c_property.get("distance").get("operator")
                if c_op == ">":
                    op = operator.gt
                elif c_op == ">=":
                    op = operator.ge
                elif c_op == "<":
                    op = operator.lt
                elif c_op == "<=":
                    op = operator.le
                elif c_op == "=":
                    op = operator.eq
                dist_value = c_property.get("distance").get("value")
                my_access_distance_constraint = access_dist.AccessDistance(
                    constraint_id, constraint_type, constraint_demands,
                    _comparison_operator=op, _threshold=dist_value,
                    _location=self.locations[location_id])
                self.constraints[my_access_distance_constraint.name] = \
                    my_access_distance_constraint
            elif constraint_type == "distance_between_demands":
                c_property = constraint_info.get("properties")
                op = operator.le  # default operator
                c_op = c_property.get("distance").get("operator")
                if c_op == ">":
                    op = operator.gt
                elif c_op == ">=":
                    op = operator.ge
                elif c_op == "<":
                    op = operator.lt
                elif c_op == "<=":
                    op = operator.le
                elif c_op == "=":
                    op = operator.eq
                dist_value = c_property.get("distance").get("value")
                my_aic_distance_constraint = aic_dist.AICDistance(
                    constraint_id, constraint_type, constraint_demands,
                    _comparison_operator=op, _threshold=dist_value)
                self.constraints[my_aic_distance_constraint.name] = \
                    my_aic_distance_constraint
            elif constraint_type == "inventory_group":
                my_inventory_group_constraint = \
                    inventory_group.InventoryGroup(
                        constraint_id, constraint_type, constraint_demands)
                self.constraints[my_inventory_group_constraint.name] = \
                    my_inventory_group_constraint
            elif constraint_type == "region_fit":
                c_property = constraint_info.get("properties")
                controller = c_property.get("controller")
                request = c_property.get("request")
                # inventory type is cloud for region_fit
                inventory_type = "cloud"
                my_service_constraint = service_constraint.Service(
                    constraint_id, constraint_type, constraint_demands,
                    _controller=controller, _request=request, _cost=None,
                    _inventory_type=inventory_type)
                self.constraints[my_service_constraint.name] = \
                    my_service_constraint
            elif constraint_type == "instance_fit":
                c_property = constraint_info.get("properties")
                controller = c_property.get("controller")
                request = c_property.get("request")
                # inventory type is service for instance_fit
                inventory_type = "service"
                my_service_constraint = service_constraint.Service(
                    constraint_id, constraint_type, constraint_demands,
                    _controller=controller, _request=request, _cost=None,
                    _inventory_type=inventory_type)
                self.constraints[my_service_constraint.name] = \
                    my_service_constraint
            elif constraint_type == "zone":
                c_property = constraint_info.get("properties")
                location_id = c_property.get("location")
                qualifier = c_property.get("qualifier")
                category = c_property.get("category")
                location = self.locations[location_id] if location_id else None
                my_zone_constraint = zone.Zone(
                    constraint_id, constraint_type, constraint_demands,
                    _qualifier=qualifier, _category=category, _location=location)
                self.constraints[my_zone_constraint.name] = my_zone_constraint
            elif constraint_type == "attribute":
                c_property = constraint_info.get("properties")
                my_attribute_constraint = \
                    attribute_constraint.Attribute(constraint_id,
                                                   constraint_type,
                                                   constraint_demands,
                                                   _properties=c_property)
                self.constraints[my_attribute_constraint.name] = \
                    my_attribute_constraint
            else:
                LOG.error("unknown constraint type {}".format(constraint_type))
                return

        # get objective function
        if "objective" not in json_template["conductor_solver"]\
           or not json_template["conductor_solver"]["objective"]:
            self.objective = objective.Objective()
        else:
            input_objective = json_template["conductor_solver"]["objective"]
            self.objective = objective.Objective()
            self.objective.goal = input_objective["goal"]
            self.objective.operation = input_objective["operation"]
            for operand_data in input_objective["operands"]:
                operand = objective.Operand()
                operand.operation = operand_data["operation"]
                operand.weight = float(operand_data["weight"])
                if operand_data["function"] == "distance_between":
                    func = distance_between.DistanceBetween("distance_between")
                    param = operand_data["function_param"][0]
                    if param in self.locations:
                        func.loc_a = self.locations[param]
                    elif param in self.demands:
                        func.loc_a = self.demands[param]
                    param = operand_data["function_param"][1]
                    if param in self.locations:
                        func.loc_z = self.locations[param]
                    elif param in self.demands:
                        func.loc_z = self.demands[param]
                    operand.function = func
                elif operand_data["function"] == "aic_version":
                    self.objective.goal = "min_aic"
                    func = aic_version.AICVersion("aic_version")
                    func.loc = operand_data["function_param"]
                    operand.function = func
                elif operand_data["function"] == "cost":
                    func = cost.Cost("cost")
                    func.loc = operand_data["function_param"]
                    operand.function = func

                self.objective.operand_list.append(operand)

    def get_data_from_aai_simulator(self):
        loc = demand.Location("uCPE")
        loc.loc_type = "coordinates"
        latitude = random.uniform(self.region_gen.least_latitude,
                                  self.region_gen.most_latitude)
        longitude = random.uniform(self.region_gen.least_longitude,
                                   self.region_gen.most_longitude)
        loc.value = (latitude, longitude)
        self.locations[loc.name] = loc

        demand1 = demand.Demand("vVIG")
        demand1.resources = self.region_gen.regions
        demand1.sort_base = 0  # this is only for testing
        self.demands[demand1.name] = demand1

        demand2 = demand.Demand("vGW")
        demand2.resources = self.region_gen.regions
        demand2.sort_base = 2  # this is only for testing
        self.demands[demand2.name] = demand2

        demand3 = demand.Demand("vVIG2")
        demand3.resources = self.region_gen.regions
        demand3.sort_base = 1  # this is only for testing
        self.demands[demand3.name] = demand3

        demand4 = demand.Demand("vGW2")
        demand4.resources = self.region_gen.regions
        demand4.sort_base = 3  # this is only for testing
        self.demands[demand4.name] = demand4

        constraint_list = []

        access_distance = access_dist.AccessDistance(
            "uCPE-all", "access_distance",
            [demand1.name, demand2.name, demand3.name, demand4.name],
            _comparison_operator=operator.le, _threshold=50000,
            _location=loc)
        constraint_list.append(access_distance)

        '''
        access_distance = access_dist.AccessDistance(
            "uCPE-all", "access_distance", [demand1.name, demand2.name],
            _comparison_operator=operator.le, _threshold=5000, _location=loc)
        constraint_list.append(access_distance)

        aic_distance = aic_dist.AICDistance(
            "vVIG-vGW", "aic_distance", [demand1.name, demand2.name],
            _comparison_operator=operator.le, _threshold=50)
        constraint_list.append(aic_distance)

        same_zone = zone.Zone(
            "same-zone", "zone", [demand1.name, demand2.name],
            _qualifier="same", _category="zone1")
        constraint_list.append(same_zone)
        '''
    def reorder_constraint(self):
        # added manual ranking to the constraint type for optimizing purpose the last 2 are costly interaction
        for constraint_name, constraint in self.constraints.items():
            if constraint.constraint_type == "distance_to_location":
                constraint.rank = 1
            elif constraint.constraint_type == "zone":
                constraint.rank = 2
            elif constraint.constraint_type == "attribute":
                constraint.rank = 3
            elif constraint.constraint_type == "inventory_group":
                constraint.rank = 4
            elif constraint.constraint_type == "instance_fit":
                constraint.rank = 5
            elif constraint.constraint_type == "region_fit":
                constraint.rank = 6
            else:
                constraint.rank = 7

    def attr_sort(self, attrs=['rank']):
        #this helper for sorting the rank
        return lambda k: [getattr(k, attr) for attr in attrs]

    def sort_constraint_by_rank(self):
        # this sorts as rank
        for d_name, cl in self.demands.items():
            cl_list = cl.constraint_list
            cl_list.sort(key=self.attr_sort(attrs=['rank']))


    def assgin_constraints_to_demands(self):
        # self.parse_dhv_template() # get data from DHV template
        # self.get_data_from_aai_simulator() # get data from aai simulation
        # renaming simulate to assgin_constraints_to_demands
        # spread the constraints over the demands
        self.reorder_constraint()
        for constraint_name, constraint in self.constraints.items():
            for d in constraint.demand_list:
                if d in self.demands.keys():
                    self.demands[d].constraint_list.append(constraint)
        self.sort_constraint_by_rank()
