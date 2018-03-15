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
import json
import unittest
import uuid

import conductor.data.service as service
import mock
import stevedore
import yaml
from conductor.common.utils import conductor_logging_util as log_util
from conductor.data.plugins.inventory_provider import extensions as ip_ext
from conductor.data.plugins.service_controller import extensions as sc_ext
from conductor.data.service import DataEndpoint
from oslo_config import cfg


class TestDataEndpoint(unittest.TestCase):

    def setUp(self):
        cfg.CONF.set_override('keyspace', 'conductor')
        ip_ext_manager = (
            ip_ext.Manager(cfg.CONF, 'conductor.inventory_provider.plugin'))
        sc_ext_manager = (
            sc_ext.Manager(cfg.CONF, 'conductor.service_controller.plugin'))
        self.data_ep = DataEndpoint(ip_ext_manager, sc_ext_manager)

    def tearDown(self):
        pass

    def test_get_candidate_location(self):
        req_json_file = './conductor/tests/unit/data/candidate_list.json'
        req_json_candidate = json.loads(open(req_json_file).read())
        req_json = dict()
        req_json['candidate'] = req_json_candidate['candidate_list'][0]
        location = (32.897480, -97.040443)
        self.assertEqual({'response': location, 'error': False},
                         self.data_ep.get_candidate_location(None, req_json))
        req_json['candidate']['latitude'] = None
        req_json['candidate']['longitude'] = None
        self.assertEqual({'response': None, 'error': True},
                         self.data_ep.get_candidate_location(None,
                                                             req_json))
        req_json['candidate'] = req_json_candidate['candidate_list'][1]
        location = (40.7128, -74.0060)
        self.assertEqual({'response': location, 'error': False},
                         self.data_ep.get_candidate_location(None, req_json))

    def test_get_candidate_zone(self):
        req_json_file = './conductor/tests/unit/data/candidate_list.json'
        req_json_candidate = json.loads(open(req_json_file).read())
        req_json = dict()
        req_json['candidate'] = req_json_candidate['candidate_list'][0]
        req_json['category'] = None
        self.assertEqual({'response': None, 'error': True},
                         self.data_ep.get_candidate_zone(None, req_json))
        req_json['category'] = 'region'
        self.assertEqual({'response': 'DLLSTX55', 'error': False},
                         self.data_ep.get_candidate_zone(None, req_json))
        req_json['category'] = 'complex'
        self.assertEqual({'response': 'dalls_one', 'error': False},
                         self.data_ep.get_candidate_zone(None, req_json))
        req_json['candidate'] = req_json_candidate['candidate_list'][1]
        req_json['category'] = 'region'
        self.assertEqual({'response': 'NYCNY55', 'error': False},
                         self.data_ep.get_candidate_zone(None, req_json))

    @mock.patch.object(service.LOG, 'error')
    @mock.patch.object(service.LOG, 'debug')
    @mock.patch.object(stevedore.ExtensionManager, 'map_method')
    def test_get_candidates_from_service(self, ext_mock, debug_mock,
                                         error_mock):
        req_json_file = './conductor/tests/unit/data/constraints.json'
        req_json = yaml.safe_load(open(req_json_file).read())
        candidate_list = req_json['candidate_list']
        ext_mock.return_value = [candidate_list]
        self.maxDiff = None
        self.assertEqual(2, len(
            self.data_ep.get_candidates_from_service(None, req_json)))
        req_json['controller'] = 'APP-C'
        self.assertEqual({'response': [], 'error': False},
                         self.data_ep.get_candidates_from_service(None,
                                                                  req_json))

    def test_get_candidate_discard_set(self):
        req_json_file = './conductor/tests/unit/data/constraints.json'
        req_json = yaml.safe_load(open(req_json_file).read())
        value_attrib = 'complex_name'
        value = req_json['properties']['evaluate'][value_attrib]
        candidate_list = req_json['candidate_list']
        self.assertEqual(2, len(self.data_ep.get_candidate_discard_set(value,
                                                                       candidate_list,
                                                                       value_attrib)))
        value_attrib = 'region'
        value = req_json['properties']['evaluate'][value_attrib]
        self.assertEqual(0, len(self.data_ep.get_candidate_discard_set(value,
                                                                       candidate_list,
                                                                       value_attrib)))

    @mock.patch.object(service.LOG, 'error')
    @mock.patch.object(service.LOG, 'debug')
    @mock.patch.object(service.LOG, 'info')
    @mock.patch.object(stevedore.ExtensionManager, 'map_method')
    @mock.patch.object(stevedore.ExtensionManager, 'names')
    def test_get_candidates_by_attributes(self, ext_mock2, ext_mock1,
                                          info_mock, debug_mock, error_mock):
        req_json_file = './conductor/tests/unit/data/constraints.json'
        req_json = yaml.safe_load(open(req_json_file).read())
        candidate_list = req_json['candidate_list']
        ext_mock1.return_value = [candidate_list]
        ext_mock2.return_value = [None]
        self.maxDiff = None
        expected_response = {'response': [candidate_list[0]], 'error': False}
        self.assertEqual(expected_response,
                         self.data_ep.get_candidates_by_attributes(None,
                                                                   req_json))

    @mock.patch.object(service.LOG, 'error')
    @mock.patch.object(service.LOG, 'debug')
    @mock.patch.object(service.LOG, 'info')
    @mock.patch.object(log_util, 'getTransactionId')
    @mock.patch.object(stevedore.ExtensionManager, 'map_method')
    def test_reslove_demands(self, ext_mock, logutil_mock, info_mock, debug_mock,
                             error_mock):
        req_json_file = './conductor/tests/unit/data/demands.json'
        req_json = yaml.safe_load(open(req_json_file).read())
        ctxt = {
            'plan_id': uuid.uuid4(),
            'keyspace': cfg.CONF.keyspace
        }
        logutil_mock.return_value = uuid.uuid4()
        ext_mock.return_value = []
        expected_response = {'response': {'resolved_demands': None},
                             'error': True}
        self.assertEqual(expected_response,
                         self.data_ep.resolve_demands(ctxt, req_json))
        return_value = req_json['demands']['vG']
        ext_mock.return_value = [return_value]
        expected_response = {'response': {'resolved_demands': return_value},
                             'error': False}
        self.assertEqual(expected_response,
                         self.data_ep.resolve_demands(ctxt, req_json))

    @mock.patch.object(service.LOG, 'error')
    @mock.patch.object(service.LOG, 'info')
    @mock.patch.object(stevedore.ExtensionManager, 'names')
    @mock.patch.object(service.DataEndpoint, 'match_hpa')
    def test_get_candidates_with_hpa(self, hpa_mock, ext_mock1,
                                     info_mock, error_mock):
        req_json_file = './conductor/tests/unit/data/candidate_list.json'
        hpa_json_file = './conductor/tests/unit/data/hpa_constraints.json'
        hpa_json = yaml.safe_load(open(hpa_json_file).read())
        req_json = yaml.safe_load(open(req_json_file).read())
        candidate_list = req_json['candidate_list']
        hpa_constraint = hpa_json['hpa_constraint_vG']['properties']
        features = hpa_constraint['evaluate'][0]['features']
        label_name = hpa_constraint['evaluate'][0]['label']
        ext_mock1.return_value = ['aai']
        flavor_info = {"flavor-id": "vim-flavor-id1",
                       "flavor-name": "vim-flavor-name1"}
        hpa_mock.return_value = flavor_info
        self.maxDiff = None
        hpa_candidate_list = copy.deepcopy(candidate_list)
        hpa_candidate_list[1]['flavor_map'] = {}
        hpa_candidate_list[1]['flavor_map'][label_name] = flavor_info
        expected_response = {'response': hpa_candidate_list, 'error': False}
        args = {"candidate_list": candidate_list,
                "features": features,
                "label_name": label_name}
        self.assertEqual(expected_response,
                         self.data_ep.get_candidates_with_hpa(None, args))


if __name__ == "__main__":
    unittest.main()
