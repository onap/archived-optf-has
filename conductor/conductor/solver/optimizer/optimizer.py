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

from oslo_config import cfg
from oslo_log import log
import copy
import time

from conductor import service
# from conductor.solver.optimizer import decision_path as dpath
# from conductor.solver.optimizer import best_first
# from conductor.solver.optimizer import greedy
from conductor.solver.optimizer import fit_first
from conductor.solver.optimizer import random_pick
from conductor.solver.request import demand
from conductor.solver.triage_tool.triage_data import TriageData

LOG = log.getLogger(__name__)

CONF = cfg.CONF

SOLVER_OPTS = [

]

CONF.register_opts(SOLVER_OPTS, group='solver')


class Optimizer(object):

    # FIXME(gjung): _requests should be request (no underscore, one item)
    def __init__(self, conf, _requests=None, _begin_time=None):
        self.conf = conf

        # start time of solving the plan
        if _begin_time is not None:
            self._begin_time = _begin_time

        # self.search = greedy.Greedy(self.conf)
        self.search = None
        # self.search = best_first.BestFirst(self.conf)

        if _requests is not None:
            self.requests = _requests

        # Were the 'simulators' ever used? It doesn't look like this.
        # Since solver/simulator code needs cleansing before being moved to ONAP,
        # I see no value for having this piece of code which is not letting us do
        # that cleanup. Also, Shankar has confirmed solver/simulators folder needs
        # to go away. Commenting out for now - may be should be removed permanently.
        # Shankar (TODO).
        # else:
        #     ''' for simulation '''
        #     req_sim = request_simulator.RequestSimulator(self.conf)
        #     req_sim.generate_requests()
        #     self.requests = req_sim.requests

    def get_solution(self, num_solutions):

        LOG.debug("search start for max {} solutions".format(num_solutions))
        for rk in self.requests:
            request = self.requests[rk]
            LOG.debug("--- request = {}".format(rk))

            decision_list = list()

            LOG.debug("1. sort demands")
            demand_list = self._sort_demands(request)
            for d in demand_list:
                LOG.debug("    demand = {}".format(d.name))

            LOG.debug("2. search")

            rand_counter = 10
            while num_solutions == 'all' or num_solutions > 0:

                LOG.debug("searching for the solution {}".format(len(decision_list) + 1))

                st = time.time()
                _copy_demand_list = copy.deepcopy(demand_list)

                if not request.objective.goal:
                    LOG.debug("No objective function is provided. "
                              "Random pick algorithm is used")
                    self.search = random_pick.RandomPick(self.conf)
                    best_path = self.search.search(demand_list, request)
                else:
                    LOG.debug("Fit first algorithm is used")
                    self.search = fit_first.FitFirst(self.conf)
                    best_path = self.search.search(demand_list,
                                                   request.objective, request)

                LOG.debug("search delay = {} sec".format(time.time() - st))

                demand_list = copy.deepcopy(_copy_demand_list)

                if best_path is not None:
                    self.search.print_decisions(best_path)
                    rand_counter = 10
                elif not request.objective.goal and rand_counter > 0 and self._has_candidates(request):
                    # RandomPick gave no candidates after applying constraints. If there are any candidates left
                    # lets' try again several times until some solution is found. When one of the demands is not unique
                    # it persists in the list all the time. In order to prevent infinite loop we need to have counter
                    rand_counter -= 1
                    LOG.debug("Incomplete random solution - repeat {}".format(rand_counter))
                    continue
                else:
                    LOG.debug("no solution found")
                    break

                # add the current solution to decision_list
                decision_list.append(best_path.decisions)

                #remove the candidate with "uniqueness = true"
                self._remove_unique_candidate(request, best_path, demand_list)

                if num_solutions != 'all':
                    num_solutions -= 1
            self.search.triageSolver.getSolution(decision_list)
            return decision_list

    def _has_candidates(self, request):
        for demand_name, demand in request.demands.items():
            LOG.debug("Req Available resources: {} {}".format(demand_name, len(request.demands[demand_name].resources)))
            if len(demand.resources) == 0:
                LOG.debug("No more candidates for demand {}".format(demand_name))
                return False

        return True

    def _remove_unique_candidate(self, _request, current_decision, demand_list):

        # This method is to remove previous solved/used candidate from consideration
        # when Conductor needs to provide multiple solutions to the user/client

        for demand_name, candidate_attr in current_decision.decisions.items():
            candidate_uniqueness = candidate_attr.get('uniqueness')
            if candidate_uniqueness and candidate_uniqueness == 'true':
                # if the candidate uniqueness is 'false', then remove
                # that solved candidate from the translated candidates list
                _request.demands[demand_name].resources.pop(candidate_attr.get('candidate_id'))
                # update the demand_list
                for demand in demand_list:
                    if(getattr(demand, 'name') == demand_name):
                        demand.resources = _request.demands[demand_name].resources

    def _sort_demands(self, _request):
        LOG.debug(" _sort_demands")
        demand_list = []

        # first, find loc-demand dependencies
        # using constraints and objective functions
        open_demand_list = []
        for key in _request.constraints:
            c = _request.constraints[key]
            if c.constraint_type == "access_distance":
                for dk in c.demand_list:
                    if _request.demands[dk].sort_base != 1:
                        _request.demands[dk].sort_base = 1
                        open_demand_list.append(_request.demands[dk])
        for op in _request.objective.operand_list:
            if op.function.func_type == "latency_between": #TODO   do i need to include the region_group here?
                if isinstance(op.function.loc_a, demand.Location):
                    if _request.demands[op.function.loc_z.name].sort_base != 1:
                        _request.demands[op.function.loc_z.name].sort_base = 1
                        open_demand_list.append(op.function.loc_z)
                elif isinstance(op.function.loc_z, demand.Location):
                    if _request.demands[op.function.loc_a.name].sort_base != 1:
                        _request.demands[op.function.loc_a.name].sort_base = 1
                        open_demand_list.append(op.function.loc_a)
            elif op.function.func_type == "distance_between":
                if isinstance(op.function.loc_a, demand.Location):
                    if _request.demands[op.function.loc_z.name].sort_base != 1:
                        _request.demands[op.function.loc_z.name].sort_base = 1
                        open_demand_list.append(op.function.loc_z)
                elif isinstance(op.function.loc_z, demand.Location):
                    if _request.demands[op.function.loc_a.name].sort_base != 1:
                        _request.demands[op.function.loc_a.name].sort_base = 1
                        open_demand_list.append(op.function.loc_a)

        if len(open_demand_list) == 0:
            init_demand = self._exist_not_sorted_demand(_request.demands)
            open_demand_list.append(init_demand)

        # second, find demand-demand dependencies
        while True:
            d_list = self._get_depended_demands(open_demand_list, _request)
            for d in d_list:
                demand_list.append(d)

            init_demand = self._exist_not_sorted_demand(_request.demands)
            if init_demand is None:
                break
            open_demand_list.append(init_demand)

        return demand_list

    def _get_depended_demands(self, _open_demand_list, _request):
        demand_list = []

        while True:
            if len(_open_demand_list) == 0:
                break

            d = _open_demand_list.pop(0)
            if d.sort_base != 1:
                d.sort_base = 1
            demand_list.append(d)

            for key in _request.constraints:
                c = _request.constraints[key]
                # FIXME(snarayanan): "aic" only to be known by conductor-data
                if c.constraint_type == "aic_distance":
                    if d.name in c.demand_list:
                        for dk in c.demand_list:
                            if dk != d.name and \
                                    _request.demands[dk].sort_base != 1:
                                _request.demands[dk].sort_base = 1
                                _open_demand_list.append(
                                    _request.demands[dk])

            for op in _request.objective.operand_list:
                if op.function.func_type == "latency_between":  #TODO
                    if op.function.loc_a.name == d.name:
                        if op.function.loc_z.name in \
                                _request.demands.keys():
                            if _request.demands[
                                    op.function.loc_z.name].sort_base != 1:
                                _request.demands[
                                    op.function.loc_z.name].sort_base = 1
                                _open_demand_list.append(op.function.loc_z)
                    elif op.function.loc_z.name == d.name:
                        if op.function.loc_a.name in \
                                _request.demands.keys():
                            if _request.demands[
                                    op.function.loc_a.name].sort_base != 1:
                                _request.demands[
                                    op.function.loc_a.name].sort_base = 1
                                _open_demand_list.append(op.function.loc_a)

                elif op.function.func_type == "distance_between":
                    if op.function.loc_a.name == d.name:
                        if op.function.loc_z.name in \
                                _request.demands.keys():
                            if _request.demands[
                                    op.function.loc_z.name].sort_base != 1:
                                _request.demands[
                                    op.function.loc_z.name].sort_base = 1
                                _open_demand_list.append(op.function.loc_z)
                    elif op.function.loc_z.name == d.name:
                        if op.function.loc_a.name in \
                                _request.demands.keys():
                            if _request.demands[
                                    op.function.loc_a.name].sort_base != 1:
                                _request.demands[
                                    op.function.loc_a.name].sort_base = 1
                                _open_demand_list.append(op.function.loc_a)

        return demand_list

    def _exist_not_sorted_demand(self, _demands):
        not_sorted_demand = None
        for key in _demands:
            demand = _demands[key]
            if demand.sort_base != 1:
                not_sorted_demand = demand
                break
        return not_sorted_demand

