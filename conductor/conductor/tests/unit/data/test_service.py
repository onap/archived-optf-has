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
from conductor.data.plugins.file_system import extensions as fs_ext
from conductor.data.plugins.vim_controller import extensions as vc_ext
from conductor.data.service import DataEndpoint
from oslo_config import cfg


class TestDataEndpoint(unittest.TestCase):

    def setUp(self):
        ip_ext_manager = (
            ip_ext.Manager(cfg.CONF, 'conductor.inventory_provider.plugin'))
        vc_ext_manager = (
            vc_ext.Manager(cfg.CONF, 'conductor.vim_controller.plugin'))
        sc_ext_manager = (
            sc_ext.Manager(cfg.CONF, 'conductor.service_controller.plugin'))
        fs_ext_manager = (
            fs_ext.Manager(cfg.CONF, 'conductor.file_system.plugin'))

        self.data_ep = DataEndpoint(ip_ext_manager,
                                    vc_ext_manager,
                                    sc_ext_manager,
                                    fs_ext_manager)

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
        self.assertEqual(3, len(self.data_ep.get_candidate_discard_set(value,
                                                                       candidate_list,
                                                                       value_attrib)))
        value_attrib = 'region'
        value = req_json['properties']['evaluate'][value_attrib]
        self.assertEqual(0, len(self.data_ep.get_candidate_discard_set(value,
                                                                       candidate_list,
                                                                       value_attrib)))

    def test_get_candidate_discard_set_by_cloud_region(self):
        req_json_file = './conductor/tests/unit/data/constraints.json'
        req_json = yaml.safe_load(open(req_json_file).read())
        value_attrib = 'location_id'
        value = req_json['properties']['evaluate']['cloud-region']
        candidate_list = req_json['candidate_list']
        self.assertEqual(2, len(
            self.data_ep.get_candidate_discard_set_by_cloud_region(value,
                                                                   candidate_list,
                                                                   value_attrib)))

    @mock.patch.object(service.LOG, 'error')
    @mock.patch.object(service.LOG, 'debug')
    @mock.patch.object(service.LOG, 'info')
    @mock.patch.object(stevedore.ExtensionManager, 'map_method')
    @mock.patch.object(stevedore.ExtensionManager, 'names')
    def test_get_inventory_group_candidates(self, ext2_mock, ext1_mock,
                                            info_mock, debug_mock, error_mock):
        ext1_mock.return_value = None
        req_json_file = './conductor/tests/unit/data/constraints.json'
        req_json = yaml.safe_load(open(req_json_file).read())
        self.assertEqual({'response': [], 'error': True},
                         self.data_ep.get_inventory_group_candidates(None,
                                                                     arg=req_json))
        ext1_mock.return_value = [None]
        self.assertEqual({'response': [], 'error': True},
                         self.data_ep.get_inventory_group_candidates(None,
                                                                     arg=req_json))
        pairs = [['instance-1', 'instance-2']]
        ext1_mock.return_value = [pairs]
        ext2_mock.return_value = ['aai']
        candidate_list = req_json['candidate_list']
        expected_candidate_list = [c for c in candidate_list
                                   if c["candidate_id"] == 'instance-1']
        self.assertEqual({'response': expected_candidate_list, 'error': False},
                         self.data_ep.get_inventory_group_candidates(None,
                                                                     arg=req_json))

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
        ext_mock1.side_effect = ip_ext_sideeffect
        ext_mock2.return_value = ['aai']
        self.maxDiff = None
        expected_response = {'response': [candidate_list[0]], 'error': False}
        self.assertEqual(expected_response,
                         self.data_ep.get_candidates_by_attributes(None,
                                                                   req_json))
        req_json['properties']['evaluate']['network_roles'] = {"all": []}
        expected_response = {'response': [candidate_list[0]], 'error': False}
        self.assertEqual(expected_response,
                         self.data_ep.get_candidates_by_attributes(None,
                                                                   req_json))
        req_json['properties']['evaluate']['network_roles'] = {"any": []}
        expected_response = {'response': [candidate_list[0]], 'error': False}
        self.assertEqual(expected_response,
                         self.data_ep.get_candidates_by_attributes(None,
                                                                   req_json))
        req_json['properties']['evaluate']['network_roles'] = {
            "all": ['role-1']}
        expected_response = {'response': [], 'error': False}
        self.assertEqual(expected_response,
                         self.data_ep.get_candidates_by_attributes(None,
                                                                   req_json))
        req_json['properties']['evaluate']['network_roles'] = {
            "all": ['role-2']}
        expected_response = {'response': [], 'error': False}
        self.assertEqual(expected_response,
                         self.data_ep.get_candidates_by_attributes(None,
                                                                   req_json))

    @mock.patch.object(service.LOG, 'error')
    @mock.patch.object(service.LOG, 'debug')
    @mock.patch.object(service.LOG, 'info')
    @mock.patch.object(log_util, 'getTransactionId')
    @mock.patch.object(stevedore.ExtensionManager, 'map_method')
    def test_resolve_demands(self, ext_mock, logutil_mock, info_mock,
                             debug_mock,
                             error_mock):
        self.maxDiff = None
        req_json_file = './conductor/tests/unit/data/demands.json'
        req_json = yaml.safe_load(open(req_json_file).read())
        ctxt = {
            'plan_id': uuid.uuid4(),
            'keyspace': cfg.CONF.keyspace,
            'candidate_file_path' : './conductor/data/plugins/file_system/NST.json'
        }
        logutil_mock.return_value = uuid.uuid4()
        ext_mock.return_value = []
        expected_response = {'response': {'resolved_demands': None, 'trans': {'plan_id': None,
                                                                                      'plan_name': None,
                                                                                      'translator_triage': []}},
                             'error': True}
        self.assertEqual(expected_response,
                         self.data_ep.resolve_demands(ctxt, req_json))
        return_value = req_json['demands']['vG']
        ext_mock.return_value = [return_value]
        expected_response = { 'error': False, 'response':
            { 'resolved_demands':
                  [{ 'attributes':
                         { 'customer-id': 'some_company', 'provisioning-status': 'provisioned' },
                     'inventory_provider': 'aai', 'inventory_type': 'service', 'service_type': 'vG' },
                   { 'inventory_provider': 'aai', 'inventory_type': 'cloud' } ],
              'trans': { 'plan_id': 'plan_abc', 'plan_name': 'plan_name', 'translator_triage': [ [] ] } } }
        self.assertEqual(expected_response,
                         self.data_ep.resolve_demands(ctxt, req_json))
        req_json_for_nst = {'plan_info': {'plan_name': 'nst_selection', 'plan_id': 'aa9acedb-7a66-4385-b88b-044e1dec5334'},
                            'triage_translator_data': {'plan_name': [None], 'plan_id': None},
                            'demands': {'NST': [{'inventory_type': 'NST', 'provider': 'aai', 'inventory_provider': 'file_system'}]}}
        expected_response_for_nst = {'NST': [{'candidate_id': 'NST1', 'NST_name': 'NST1', 'cost': 2, 'inventory_provider': 'file_system', 'inventory_type': 'NST', 'latency': 10, 'reliability': 100},
                                             {'candidate_id': 'NST2', 'NST_name': 'NST2', 'cost': 2, 'inventory_provider': 'file_system', 'inventory_type': 'NST', 'latency': 1, 'reliability': 90}]}
        self.assertEqual(expected_response_for_nst,
                         self.data_ep.resolve_demands(ctxt, req_json_for_nst ))
    @mock.patch.object(service.LOG, 'error')
    @mock.patch.object(service.LOG, 'debug')
    @mock.patch.object(service.LOG, 'info')
    @mock.patch.object(log_util, 'getTransactionId')
    @mock.patch.object(stevedore.ExtensionManager, 'map_method')
    def test_resolve_vfmodule_demands(self, ext_mock, logutil_mock, info_mock,
                             debug_mock,
                             error_mock):
        self.maxDiff = None
        req_json_file = './conductor/tests/unit/data/demands_vfmodule.json'
        req_json = yaml.safe_load(open(req_json_file).read())
        ctxt = {
            'plan_id': uuid.uuid4(),
            'keyspace': cfg.CONF.keyspace
        }
        logutil_mock.return_value = uuid.uuid4()
        return_value = req_json['demands']['vFW-SINK']
        ext_mock.return_value = [return_value]
        expected_response = \
            {'response': {'trans': {'translator_triage': [ [] ], 'plan_name': 'plan_name', 'plan_id': 'plan_abc'},
                          'resolved_demands': [{'service_resource_id': 'vFW-SINK-XX', 'vlan_key': 'vlan_key',
                                                'inventory_provider': 'aai', 'inventory_type': 'vfmodule',
                                                'excluded_candidates': [
                                                    {'candidate_id': ['e765d576-8755-4145-8536-0bb6d9b1dc9a'],
                                                     'inventory_type': 'vfmodule'
                                                     }], 'port_key': 'vlan_port', 'service_type': 'vFW-SINK-XX',
                                                'attributes': {'global-customer-id': 'Demonstration',
                                                               'cloud-region-id': {'get_param': 'chosen_region'},
                                                               'model-version-id':
                                                                   '763731df-84fd-494b-b824-01fc59a5ff2d',
                                                               'prov-status': 'ACTIVE',
                                                               'service_instance_id': {'get_param': 'service_id'},
                                                               'model-invariant-id':
                                                                   'e7227847-dea6-4374-abca-4561b070fe7d',
                                                               'orchestration-status': ['active']
                                                               }
                                                }]
                          }, 'error': False}

        self.assertEqual(expected_response,
                         self.data_ep.resolve_demands(ctxt, req_json))

    @mock.patch.object(service.LOG, 'error')
    @mock.patch.object(service.LOG, 'info')
    @mock.patch.object(stevedore.ExtensionManager, 'names')
    @mock.patch.object(stevedore.ExtensionManager, 'map_method')
    def test_get_candidates_with_hpa(self, hpa_mock, ext_mock1,
                                     info_mock, error_mock):
        req_json_file = './conductor/tests/unit/data/candidate_list.json'
        hpa_json_file = './conductor/tests/unit/data/hpa_constraints.json'
        hpa_json = yaml.safe_load(open(hpa_json_file).read())
        req_json = yaml.safe_load(open(req_json_file).read())
        candidate_list = req_json['candidate_list']
        (constraint_id, constraint_info) = \
            list(hpa_json["conductor_solver"]["constraints"][0].items())[0]
        hpa_constraint = constraint_info['properties']
        flavorProperties = hpa_constraint['evaluate'][0]['flavorProperties']
        id = hpa_constraint['evaluate'][0]['id']
        type = hpa_constraint['evaluate'][0]['type']
        directives = hpa_constraint['evaluate'][0]['directives']
        attr = directives[0].get("attributes")
        label_name = attr[0].get("attribute_name")
        ext_mock1.return_value = ['aai']
        flavor_info = {"flavor-id": "vim-flavor-id1",
                       "flavor-name": "vim-flavor-name1"}
        directive = [
            {
                "id": id,
                "type": type,
                "directives": directives
            }
        ]
        hpa_mock.return_value = [flavor_info]
        self.maxDiff = None
        args = generate_args(candidate_list, flavorProperties, id, type, directives)
        hpa_candidate_list = copy.deepcopy(candidate_list)
        hpa_candidate_list[1]['flavor_map'] = {}
        hpa_candidate_list[1]['flavor_map'][label_name] = "vim-flavor-name1"
        hpa_candidate_list[1]['all_directives'] = {}
        hpa_candidate_list[1]['all_directives']['directives'] = directive
        hpa_candidate_list1 = []
        hpa_candidate_list1.append(hpa_candidate_list[0])
        expected_response = {'response': hpa_candidate_list1, 'error': False}
        self.assertEqual(expected_response,
                         self.data_ep.get_candidates_with_hpa(None, args))

        hpa_candidate_list2 = list()
        hpa_candidate_list2.append(copy.deepcopy(candidate_list[0]))
        args = generate_args(candidate_list, flavorProperties, id, type, directives)
        hpa_mock.return_value = []
        expected_response = {'response': hpa_candidate_list2, 'error': False}
        self.assertEqual(expected_response,
                         self.data_ep.get_candidates_with_hpa(None, args))

        flavor_info = {}
        hpa_mock.return_value = [flavor_info]
        expected_response = {'response': hpa_candidate_list2, 'error': False}
        self.assertEqual(expected_response,
                         self.data_ep.get_candidates_with_hpa(None, args))

        flavor_info = {"flavor-id": "vim-flavor-id1",
                       "flavor-name": ""}
        hpa_mock.return_value = [flavor_info]
        expected_response = {'response': hpa_candidate_list2, 'error': False}
        self.assertEqual(expected_response,
                         self.data_ep.get_candidates_with_hpa(None, args))

        flavor_info = {"flavor-id": "vim-flavor-id1"}
        hpa_mock.return_value = [flavor_info]
        expected_response = {'response': hpa_candidate_list2, 'error': False}
        self.assertEqual(expected_response,
                         self.data_ep.get_candidates_with_hpa(None, args))

    @mock.patch.object(service.LOG, 'warn')
    @mock.patch.object(service.LOG, 'info')
    @mock.patch.object(stevedore.ExtensionManager, 'names')
    @mock.patch.object(stevedore.ExtensionManager, 'map_method')
    def test_get_candidates_with_vim_capacity(self, vim_mock, ext_mock1,
                                              info_mock, warn_mock):
        req_json_file = './conductor/tests/unit/data/candidate_list.json'
        hpa_json_file = './conductor/tests/unit/data/hpa_constraints.json'
        hpa_json = yaml.safe_load(open(hpa_json_file).read())
        req_json = yaml.safe_load(open(req_json_file).read())
        candidate_list = req_json['candidate_list']
        ext_mock1.return_value = ['MultiCloud']
        (constraint_id, constraint_info) = \
            list(hpa_json["conductor_solver"]["constraints"][2].items())[0]
        vim_request = constraint_info['properties']['request']
        ctxt = {}
        candidate_list_copy = list(copy.deepcopy(candidate_list))
        args = {"candidate_list": [candidate_list_copy[1]],
                "request": vim_request}
        vim_mock.return_value = [['att-aic_NYCNY55']]
        self.assertEqual({'response': [candidate_list[1]], 'error': False},
                         self.data_ep.get_candidates_with_vim_capacity(ctxt,
                                                                       args))
        vim_mock.return_value = []
        self.assertEqual({'response': [candidate_list[1]], 'error': True},
                         self.data_ep.get_candidates_with_vim_capacity(ctxt,
                                                                       args))
        vim_mock.return_value = [None]
        self.assertEqual({'response': [candidate_list[1]], 'error': True},
                         self.data_ep.get_candidates_with_vim_capacity(ctxt,
                                                                       args))
        vim_mock.return_value = None
        self.assertEqual({'response': [candidate_list[1]], 'error': True},
                         self.data_ep.get_candidates_with_vim_capacity(ctxt,
                                                                       args))
        vim_mock.return_value = [[]]
        self.assertEqual({'response': [], 'error': False},
                         self.data_ep.get_candidates_with_vim_capacity(ctxt,
                                                                       args))


def generate_args(candidate_list, flavorProperties, vf_id, model_type, directives):
    arg_candidate_list = copy.deepcopy(candidate_list)
    args = {"candidate_list": arg_candidate_list,
            "flavorProperties": flavorProperties,
            "id": vf_id,
            "type": model_type,
            "directives": directives}
    return args

def ip_ext_sideeffect(*args, **kwargs):
    req_json_file = './conductor/tests/unit/data/constraints.json'
    req_json = yaml.safe_load(open(req_json_file).read())
    candidate_list = req_json['candidate_list']
    if args[0] == 'check_network_roles':
        if kwargs['network_role_id'] == 'role-1':
            return None
        else:
            return ['DLLSTX55']
    elif args[0] == 'check_candidate_role':
        return ['candidate-role0']


if __name__ == "__main__":
    unittest.main()
