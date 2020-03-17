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


import copy
import unittest

import mock
import yaml
from conductor.solver.optimizer.constraints import hpa
from conductor.solver.utils import constraint_engine_interface as cei


class TestHPA(unittest.TestCase):

    def setUp(self):
        req_json_file = './conductor/tests/unit/solver/candidate_list.json'
        hpa_json_file = './conductor/tests/unit/solver/hpa_constraints.json'
        hpa_json = yaml.safe_load(open(hpa_json_file).read())
        req_json = yaml.safe_load(open(req_json_file).read())

        (constraint_id, constraint_info) = \
            list(hpa_json["conductor_solver"]["constraints"][0].items())[0]
        c_property = constraint_info['properties']
        constraint_type = constraint_info['properties']
        constraint_demands = list()
        parsed_demands = constraint_info['demands']
        if isinstance(parsed_demands, list):
            for d in parsed_demands:
                constraint_demands.append(d)
        self.hpa = hpa.HPA(constraint_id,
                           constraint_type,
                           constraint_demands,
                           _properties=c_property)

        self.candidate_list = req_json['candidate_list']

    def tearDown(self):
        pass

    @mock.patch.object(hpa.LOG, 'error')
    @mock.patch.object(hpa.LOG, 'info')
    @mock.patch.object(cei.LOG, 'debug')
    def test_solve(self, debug_mock, info_mock, error_mock):

        flavor_infos = [{"flavor_label_1": {"flavor-id": "vim-flavor-id1",
                                            "flavor-name": "vim-flavor-1"}},
                        {"flavor_label_2": {"flavor-id": "vim-flavor-id2",
                                            "flavor-name": "vim-flavor-2"}}]
        self.maxDiff = None
        hpa_candidate_list_1 = copy.deepcopy(self.candidate_list)
        hpa_candidate_list_1[1]['flavor_map'] = {}
        hpa_candidate_list_1[1]['flavor_map'].update(flavor_infos[0])
        hpa_candidate_list_2 = copy.deepcopy(hpa_candidate_list_1)
        hpa_candidate_list_2[1]['flavor_map'].update(flavor_infos[1])

        mock_decision_path = mock.MagicMock()
        mock_decision_path.current_demand.name = 'vG'
        request_mock = mock.MagicMock()
        client_mock = mock.MagicMock()
        client_mock.call.return_value = None
        request_mock.cei = cei.ConstraintEngineInterface(client_mock)

        self.assertEqual(None, self.hpa.solve(mock_decision_path,
                                              self.candidate_list,
                                              request_mock))

        client_mock.call.side_effect = [hpa_candidate_list_1,
                                        hpa_candidate_list_2]
        self.assertEqual(hpa_candidate_list_2,
                         self.hpa.solve(mock_decision_path,
                                        self.candidate_list, request_mock))


if __name__ == "__main__":
    unittest.main()
