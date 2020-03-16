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


import unittest

import mock
import yaml
from conductor.solver.optimizer.constraints import vim_fit
from conductor.solver.utils import constraint_engine_interface as cei


class TestVimFit(unittest.TestCase):

    def setUp(self):
        req_json_file = './conductor/tests/unit/solver/candidate_list.json'
        hpa_json_file = './conductor/tests/unit/solver/hpa_constraints.json'
        hpa_json = yaml.safe_load(open(hpa_json_file).read())
        req_json = yaml.safe_load(open(req_json_file).read())

        (constraint_id, constraint_info) = \
            list(hpa_json["conductor_solver"]["constraints"][2].items())[0]
        c_property = constraint_info['properties']
        constraint_type = constraint_info['properties']
        constraint_demands = list()
        parsed_demands = constraint_info['demands']
        if isinstance(parsed_demands, list):
            for d in parsed_demands:
                constraint_demands.append(d)
        self.vim_fit = vim_fit.VimFit(constraint_id,
                                      constraint_type,
                                      constraint_demands,
                                      _properties=c_property)

        self.candidate_list = req_json['candidate_list']

    def tearDown(self):
        pass

    @mock.patch.object(vim_fit.LOG, 'error')
    @mock.patch.object(vim_fit.LOG, 'info')
    @mock.patch.object(vim_fit.LOG, 'debug')
    def test_solve(self, debug_mock, info_mock, error_mock):

        self.maxDiff = None

        mock_decision_path = mock.MagicMock()
        mock_decision_path.current_demand.name = 'vG'
        request_mock = mock.MagicMock()
        client_mock = mock.MagicMock()
        client_mock.call.return_value = None
        request_mock.cei = cei.ConstraintEngineInterface(client_mock)

        self.assertEqual(self.candidate_list,
                         self.vim_fit.solve(mock_decision_path,
                                        self.candidate_list, request_mock))
        client_mock.call.return_value = self.candidate_list[1]
        request_mock.cei = cei.ConstraintEngineInterface(client_mock)

        self.assertEqual(self.candidate_list[1],
                         self.vim_fit.solve(mock_decision_path,
                                        self.candidate_list, request_mock))


if __name__ == "__main__":
    unittest.main()
