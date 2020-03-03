#!/usr/bin/env python
#
# -------------------------------------------------------------------------
#   Copyright (c) 2015-2017 AT&T Intellectual Property
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


# import json
import collections
import operator
import random

from conductor.solver.optimizer.constraints \
    import access_distance as access_dist
from conductor.solver.optimizer.constraints \
    import aic_distance as aic_dist
from conductor.solver.optimizer.constraints \
    import attribute as attribute_constraint
from conductor.solver.optimizer.constraints import hpa
from conductor.solver.optimizer.constraints \
    import inventory_group
from conductor.solver.optimizer.constraints \
    import service as service_constraint
from conductor.solver.optimizer.constraints import vim_fit
from conductor.solver.optimizer.constraints import zone
from conductor.solver.optimizer.constraints import threshold
from conductor.solver.request import demand
from conductor.solver.request import objective
from conductor.solver.request.functions import aic_version
from conductor.solver.request.functions import cost
from conductor.solver.request.functions import distance_between
from conductor.solver.request.functions import hpa_score
from conductor.solver.request.functions import latency_between
from conductor.solver.request import objective
from conductor.solver.triage_tool.traige_latency import TriageLatency
from oslo_log import log

LOG = log.getLogger(__name__)


# FIXME(snarayanan): This is really a SolverRequest (or Request) object
class Parser(object):

    demands = None  # type: Dict[Any, Any]
    locations = None  # type: Dict[Any, Any]
    obj_func_param = None

    def __init__(self, _region_gen=None):
        self.demands = {}
        self.locations = {}
        self.region_gen = _region_gen
        self.constraints = {}
        self.objective = None
        self.obj_func_param = list()
        self.cei = None
        self.request_id = None
        self.request_type = None
        self.region_group = None

    # def get_data_engine_interface(self):
    #    self.cei = cei.ConstraintEngineInterface()

    # FIXME(snarayanan): This should just be parse_template
    def parse_template(self, json_template=None, country_groups=None, regions_maps=None):
        if json_template is None:
            LOG.error("No template specified")
            return "Error"

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
            loc.country = location_info[
                'country'] if 'country' in location_info else None
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
                    _qualifier=qualifier, _category=category,
                    _location=location)
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
            elif constraint_type == "threshold":
                c_property = constraint_info.get("properties")
                my_threshold_constraint = \
                    threshold.Threshold(constraint_id,
                                        constraint_type,
                                        constraint_demands,
                                        _properties=c_property)
                self.constraints[my_threshold_constraint.name] = my_threshold_constraint
            elif constraint_type == "hpa":
                LOG.debug("Creating constraint - {}".format(constraint_type))
                c_property = constraint_info.get("properties")
                my_hpa_constraint = hpa.HPA(constraint_id,
                                            constraint_type,
                                            constraint_demands,
                                            _properties=c_property)
                self.constraints[my_hpa_constraint.name] = my_hpa_constraint
            elif constraint_type == "vim_fit":
                LOG.debug("Creating constraint - {}".format(constraint_type))
                c_property = constraint_info.get("properties")
                my_vim_constraint = vim_fit.VimFit(constraint_id,
                                                   constraint_type,
                                                   constraint_demands,
                                                   _properties=c_property)
                self.constraints[my_vim_constraint.name] = my_vim_constraint
            else:
                LOG.error("unknown constraint type {}".format(constraint_type))
                return

        # get objective function
        if "objective" not in json_template["conductor_solver"] \
                or not json_template["conductor_solver"]["objective"]:
            self.objective = objective.Objective()
        else:
            input_objective = json_template["conductor_solver"]["objective"]
            self.objective = objective.Objective()
            self.objective.goal = input_objective["goal"]
            self.objective.operation = input_objective["operation"]
            self.latencyTriage = TriageLatency()

            LOG.info("objective function params")
            for operand_data in input_objective["operands"]:
                if operand_data["function"] == "latency_between":
                    self.obj_func_param.append(operand_data["function_param"][1])
            LOG.info("done - objective function params")
            for operand_data in input_objective["operands"]:
                operand = objective.Operand()
                operand.operation = operand_data["operation"]
                operand.weight = float(operand_data["weight"])
                if operand_data["function"] == "latency_between":
                    LOG.debug("Processing objective function latency_between")
                    self.latencyTriage.takeOpimaztionType(operand_data["function"])
                    func = latency_between.LatencyBetween("latency_between")
                    func.region_group = self.assign_region_group_weight(country_groups, regions_maps)
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
                elif operand_data["function"] == "distance_between":
                    LOG.debug("Processing objective function distance_between")
                    self.latencyTriage.takeOpimaztionType(operand_data["function"])
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
                elif operand_data["function"] == "hpa_score":
                    func = hpa_score.HPAScore("hpa_score")
                    operand.function = func

                self.objective.operand_list.append(operand)
            self.latencyTriage.updateTriageLatencyDB(self.plan_id, self.request_id)

    def assign_region_group_weight(self, countries, regions):
        """ assign the latency group value to the country and returns a map"""
        LOG.info("Processing Assigning Latency Weight to Countries ")

        countries = self.resolve_countries(countries, regions,
                                           self.get_candidate_country_list())  # resolve the countries based on region type
        region_latency_weight = collections.OrderedDict()
        weight = 0

        if countries is None:
            LOG.info("No countries available to assign latency weight ")
            return region_latency_weight

        try:
            l_weight = ''
            for i, e in enumerate(countries):
                if e is None: continue
                for k, x in enumerate(e.split(',')):
                    region_latency_weight[x] = weight
                    l_weight += x + " : " + str(weight)
                    l_weight += ','
                weight = weight + 1
            LOG.info("Latency Weights Assigned ")
            LOG.info(l_weight)
        except Exception as err:
            LOG.info("Exception while assigning the latency weights " + err)
            print(err)
        return region_latency_weight

    def get_candidate_country_list(self):
        LOG.info("Processing Get Candidate Countries from demands  ")
        candidate_country_list = list()
        try:

            candidate_countries = ''
            for demand_id, demands in self.demands.items():
                candidate_countries += demand_id
                for candidte in list(demands.resources.values()):   # Python 3 Conversion -- dict object to list object
                    candidate_country_list.append(candidte["country"])
                    candidate_countries += candidte["country"]
                    candidate_countries += ','

            LOG.info("Available Candidate Countries " + candidate_countries)
        except Exception as err:
            print(err)
        return candidate_country_list

    def resolve_countries(self, countries_list, regions_map, candidates_country_list):
        # check the map with given location and retrieve the values
        LOG.info("Resolving Countries ")
        if countries_list is None:
            LOG.info("No Countries are available ")
            return countries_list

        countries_list = self.filter_invalid_rules(countries_list, regions_map)

        if countries_list is not None and countries_list.__len__() > 0 and countries_list.__getitem__(
                countries_list.__len__() - 1) == "*":
            self.process_wildcard_rules(candidates_country_list, countries_list)
        else:
            self.process_without_wildcard_rules(candidates_country_list, countries_list)

        return countries_list

    def process_without_wildcard_rules(self, candidates_country_list, countries_list):
        try:
            temp_country_list = list()
            for country_group in countries_list:
                for country in country_group.split(','):
                    temp_country_list.append(country)

            tmpcl = ''
            for cl in temp_country_list:
                tmpcl += cl
                tmpcl += ','

            LOG.info("Countries List before diff " + tmpcl)

            ccl = ''
            for cl in candidates_country_list:
                ccl += cl
                ccl += ','

            LOG.info("Candidates Countries List before diff " + ccl)

            # filterout the candidates that does not match the countries list
            # filter(lambda x: x not in countries_list, self.get_candidate_countries_list())
            LOG.info("Processing Difference between Candidate Countries and Latency Countries without *. ")
            diff_bw_candidates_and_countries = list(set(candidates_country_list).difference(temp_country_list))
            candcl = ''
            for cl in diff_bw_candidates_and_countries:
                candcl += cl
                candcl += ','

            LOG.info("Available countries after processing diff between " + candcl)

            self.drop_no_latency_rule_candidates(diff_bw_candidates_and_countries)
        except Exception as error:
            print(error)

    def drop_no_latency_rule_candidates(self, diff_bw_candidates_and_countries):

        cadidate_list_ = list()
        temp_candidates = dict()

        for demand_id, demands in self.demands.items():
            LOG.info("demand id " + demand_id)
            for candidte in list(demands.resources.values()):    # Python 3 Conversion -- dict object to list object
                LOG.info("candidate id " + candidte['candidate_id'])
                dem_candidate = {demand_id: demands}
                temp_candidates.update(dem_candidate)

        droped_candidates = ''
        for demand_id, demands in temp_candidates.items():
            droped_candidates += demand_id
            for candidate in list(demands.resources.values()):   # Python 3 Conversion -- dict object to list object
                if demand_id in self.obj_func_param and candidate["country"] in diff_bw_candidates_and_countries:
                    droped_candidates += candidate['candidate_id']
                    droped_candidates += ','
                    self.latencyTriage.latencyDroppedCandiate(candidate['candidate_id'], demand_id, reason="diff_bw_candidates_and_countries,Latecy weight ")
                    self.demands[demand_id].resources.pop(candidate['candidate_id'])
        LOG.info("dropped " + droped_candidates)

        # for demand_id, candidate_list in self.demands:
        #     LOG.info("Candidates for demand " + demand_id)
        #     cadidate_list_ = self.demands[demand_id]['candidates']
        #     droped_candidates = ''
        #     xlen = cadidate_list_.__len__() - 1
        #     len = xlen
        #     # LOG.info("Candidate List Length "+str(len))
        #     for i in range(len + 1):
        #         # LOG.info("iteration " + i)
        #         LOG.info("Candidate Country " + cadidate_list_[xlen]["country"])
        #         if cadidate_list_[xlen]["country"] in diff_bw_candidates_and_countries:
        #             droped_candidates += cadidate_list_[xlen]["country"]
        #             droped_candidates += ','
        #             self.demands[demand_id]['candidates'].remove(cadidate_list_[xlen])
        #             # filter(lambda candidate: candidate in candidate_list["candidates"])
        #             # LOG.info("Droping Cadidate not eligible for latency weight. Candidate ID " + cadidate_list_[xlen]["candidate_id"] + " Candidate Country: "+cadidate_list_[xlen]["country"])
        #             xlen = xlen - 1
        #         if xlen < 0: break
        #     LOG.info("Dropped Candidate Countries " + droped_candidates + " from demand " + demand_id)

    def process_wildcard_rules(self, candidates_country_list, countries_list, ):
        LOG.info("Processing the rules for " + countries_list.__getitem__(countries_list.__len__() - 1))
        candidate_countries = ''
        countries_list.remove(countries_list.__getitem__(
            countries_list.__len__() - 1))  # remove the wildcard and replace it with available candidates countries
        temp_country_list = list()
        for country_group in countries_list:
            for country in country_group.split(','):
                temp_country_list.append(country)
        temp_countries = ''
        for cl in temp_country_list:
            temp_countries += cl
            temp_countries += ','
        LOG.info("Countries before diff " + temp_countries)
        ccl = ''
        for cl in candidates_country_list:
            ccl += cl
            ccl += ','
        LOG.info("Candidates Countries List before diff " + ccl)
        diff_bw_candidates_and_countries = list(set(candidates_country_list).difference(temp_country_list))
        LOG.info("Processing Difference between Candidate Countries and Latency Countries for * . ")
        for c_group in diff_bw_candidates_and_countries:
            candidate_countries += c_group
            candidate_countries += ','
        LOG.info("Difference: " + candidate_countries[:-1])
        if candidate_countries.__len__() > 0:
            LOG.info(candidate_countries[:-1])
            countries_list.append(candidate_countries[:-1])  # append the list of difference to existing countries
        ac = ''
        for cl in countries_list:
            ac += cl
            ac += ','
        LOG.info("Available countries after processing diff between " + ac)

    def filter_invalid_rules(self, countries_list, regions_map):
        invalid_rules = list();
        for i, e in enumerate(countries_list):
            if e is None: continue

            for k, region in enumerate(e.split(',')):
                LOG.info("Processing the Rule for  " + region)
                if region.__len__() != 3:
                    if region == "*":
                        continue
                    region_list = regions_map.get(region)

                    if region_list is None:
                        LOG.info("Invalid region " + region)
                        invalid_rules.append(region)
                        continue
                    countries_list.remove(countries_list[i])
                    countries_list.insert(i, region_list)
        for ir in invalid_rules:
            LOG.info("Filtering out invalid rules from countries list ")
            LOG.info("invalid rule " + ir)

        countries_list = list(filter(lambda country: (country not in invalid_rules), countries_list))

        available_countries = ''
        for cl in countries_list:
            available_countries += cl
            available_countries += ','

        LOG.info("Available countries after the filteration " + available_countries[:-1])

        return countries_list

    def reorder_constraint(self):
        # added manual ranking to the constraint type for optimizing purpose the last 2 are costly interaction
        for constraint_name, constraint in self.constraints.items():
            if constraint.constraint_type == "distance_to_location":
                constraint.rank = 1
            elif constraint.constraint_type == "zone":
                constraint.rank = 2
            elif constraint.constraint_type == "attribute":
                constraint.rank = 3
            elif constraint.constraint_type == "hpa":
                constraint.rank = 4
            elif constraint.constraint_type == "inventory_group":
                constraint.rank = 5
            elif constraint.constraint_type == "vim_fit":
                constraint.rank = 6
            elif constraint.constraint_type == "instance_fit":
                constraint.rank = 7
            elif constraint.constraint_type == "region_fit":
                constraint.rank = 8
            elif constraint.constraint_type == "threshold":
                constraint.rank = 9
            else:
                constraint.rank = 10

    def attr_sort(self, attrs=['rank']):
        # this helper for sorting the rank
        return lambda k: [getattr(k, attr) for attr in attrs]

    def sort_constraint_by_rank(self):
        # this sorts as rank
        for d_name, cl in self.demands.items():
            cl_list = cl.constraint_list
            cl_list.sort(key=self.attr_sort(attrs=['rank']))

    def assgin_constraints_to_demands(self):
        # spread the constraints over the demands
        self.reorder_constraint()
        for constraint_name, constraint in self.constraints.items():
            for d in constraint.demand_list:
                if d in list(self.demands.keys()):     # Python 3 Conversion -- dict object to list object
                    self.demands[d].constraint_list.append(constraint)
        self.sort_constraint_by_rank()
