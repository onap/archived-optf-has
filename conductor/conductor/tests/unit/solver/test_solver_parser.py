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

import mock
import unittest

from conductor.common import db_backend
from conductor.solver.request import demand
from conductor.solver.request.parser import Parser as SolverRequestParser
from conductor.solver.optimizer.constraints import access_distance as access_dist
from conductor.solver.triage_tool.traige_latency import TriageLatency
from collections import OrderedDict
from oslo_config import cfg


class TestSolverParser(unittest.TestCase):


    def setUp(self):
        # Initialize music API
        music = db_backend.get_client()
        cfg.CONF.set_override('keyspace', 'conductor')
        music.keyspace_create(keyspace=cfg.CONF.keyspace)
        self.sp = SolverRequestParser()

        c1 = access_dist.AccessDistance(_name = 'c1', _type = 't1', _demand_list = ['d1', 'd2'])
        c2 = access_dist.AccessDistance(_name = 'c2', _type = 't1', _demand_list = ['d1'])
        self.sp.constraints = {'c1': c1, 'c2': c2}
        self.sp.demands = {'d1': demand.Demand('d1'), 'd2': demand.Demand('d2')}

    def test_assign_region_group_weight(self):
        # input:
        # two group of countries:
        # USA and MEX belong to the first region group
        # CHN and IND belong to the second region group
        # output:
        # a dictionary which assign corresspoding weight values to each country
        # ('USA', 0), ('MEX', 0), ('CHN', 1), ('IND', 1)
        countries = ['USA,MEX', 'CHN,IND']

        self.sp.resolve_countries = mock.MagicMock(return_value=countries)
        actual_response = self.sp.assign_region_group_weight(None, None)
        self.assertEqual(actual_response, OrderedDict([('USA', 0), ('MEX', 0), ('CHN', 1), ('IND', 1)]))

    def test_filter_invalid_rules(self):

        # test case 1:
        # No region placeholder
        # input should be the same as output
        countries = ['USA,MEX', 'CHN,IND']
        regions_map = dict()
        actual_response = self.sp.filter_invalid_rules(countries, regions_map)
        self.assertEqual(actual_response, ['USA,MEX', 'CHN,IND'])

        # test case 2
        # input:
        # region placeholder => EUROPE: 'DEU,ITA'
        # replacing all 'EUROPE' in countries parameter to 'DEU,ITA'
        countries = ['EUROPE', 'CHN,IND']
        regions_map = dict()
        regions_map['EUROPE'] = 'DEU,ITA'
        actual_response = self.sp.filter_invalid_rules(countries, regions_map)
        self.assertEqual(actual_response,  ['DEU,ITA', 'CHN,IND'])

    def test_drop_no_latency_rule_candidates(self):

        # test case:
        # one demand 'demand_1' contains two candidates (d1_candidate1 and d1_candidate2)
        # candidate1 locates in USA and candidate2 locates in ITA
        # the parameter 'diff_bw_candidates_and_countries' contains a list with one element 'ITA'
        # this function should get rid of candidate2 (locates in ITA) from the demand1 candidate list
        d1_candidate1 = dict()
        d1_candidate1['candidate_id'] = 'd1_candidate1'
        d1_candidate1['country'] = 'USA'

        d1_candidate2 = dict()
        d1_candidate2['candidate_id'] = 'd1_candidate2'
        d1_candidate2['country'] = 'ITA'

        test_demand_1 = demand.Demand('demand_1')
        test_demand_1.resources['d1_candidate1'] = d1_candidate1
        test_demand_1.resources['d1_candidate2'] = d1_candidate2
        self.sp.demands = {'demand_1': test_demand_1}

        self.sp.obj_func_param = ['demand_1']
        diff_bw_candidates_and_countries = ['ITA']

        self.sp.latencyTriage = TriageLatency()
        self.sp.latencyTriage.latencyDroppedCandiate = mock.MagicMock(return_value=None)

        self.sp.drop_no_latency_rule_candidates(diff_bw_candidates_and_countries)
        self.assertEqual(self.sp.demands['demand_1'].resources, {'d1_candidate1': {'candidate_id': 'd1_candidate1', 'country': 'USA'}})

    def test_resolve_countries(self):

        countries_with_wildcard = ['USA,MEX', 'CHN,IND', '*']
        countries_without_wildcard = ['USA,MEX', 'CHN, IND', 'ITA']
        candidates_country_list = ['USA', 'CHN', 'USA', 'IND']

        # test case 1
        # pass country list with wildcard in it
        self.sp.filter_invalid_rules = mock.MagicMock(return_value=countries_with_wildcard)
        actual_response = self.sp.resolve_countries(countries_with_wildcard, None, candidates_country_list)
        self.assertEqual(actual_response, countries_with_wildcard)

        # test case 2
        # country list without wildcard rule
        self.sp.filter_invalid_rules = mock.MagicMock(return_value=countries_without_wildcard)
        actual_response = self.sp.resolve_countries(countries_without_wildcard, None, candidates_country_list)
        self.assertEqual(actual_response, countries_without_wildcard)

    def test_assgin_constraints_to_demands(self):
        # The 'side effect' or impact of sp.assgin_constraints_to_demands() method is to
        # correctly change the instance variable (a dict) of self.sp.constraints to hold/contain
        # against each constraint, the correct list of demaands as set in another instance varaible (dictornary)
        # of self.sp.demands. That's what we are testing below. See how the two dictornaries are set in the setUp()
        # method

        self.sp.assgin_constraints_to_demands()
        returned_constraints = [c.name for c in self.sp.demands['d1'].constraint_list]
        self.assertEqual(sorted(returned_constraints), ['c1', 'c2'])

    def test_sort_constraint_by_rank(self):
        # The 'side effect' or impact of sp.assgin_constraints_to_demands() method is to
        # correctly change the instance variable (a dict) of self.sp.constraints to hold/contain
        # against each constraint, the correct list of demaands as set in another instance varaible (dictornary)
        # of self.sp.demands. That's what we are testing below. See how the two dictornaries are set in the setUp()
        # method

        self.sp.sort_constraint_by_rank()
        returned_constraints = [c.name for c in self.sp.demands['d1'].constraint_list]
        self.assertNotEqual(sorted(returned_constraints), ['c1', 'c3'])

    def tearDown(self):
        self.sp.constraints = {}
        self.sp.demands = {}

if __name__ == "__main__":
    unittest.main()