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
import copy
import json
import mock
import unittest
from unittest.mock import patch

from oslo_config import cfg

import conductor.data.plugins.inventory_provider.aai as aai
from conductor.data.plugins.inventory_provider.aai import AAI
from conductor.data.plugins.inventory_provider.sdc import SDC
from conductor.data.plugins.inventory_provider.hpa_utils import match_hpa
from conductor.data.plugins.triage_translator.triage_translator import TraigeTranslator


class TestAAI(unittest.TestCase):

    def setUp(self):
        cfg.CONF.set_override('password', '4HyU6sI+Tw0YMXgSHr5sJ5C0UTkeBaxXoxQqWuSVFugls7sQnaAXp4zMfJ8FKFrH', 'aai')
        CONF = cfg.CONF
        CONF.register_opts(aai.AAI_OPTS, group='aai')
        self.conf = CONF
        self.aai_ep = AAI()

    def tearDown(self):
        mock.patch.stopall()

    def test_get_version_from_string(self):

        self.assertEqual("2.5", self.aai_ep._get_version_from_string("AAI2.5"))
        self.assertEqual("3.0", self.aai_ep._get_version_from_string("AAI3.0"))

    def test_aai_versioned_path(self):

        self.assertEqual('/{}/cloud-infrastructure/cloud-regions/?depth=0'.format(self.conf.aai.server_url_version),
                         self.aai_ep._aai_versioned_path("/cloud-infrastructure/cloud-regions/?depth=0"))
        self.assertEqual('/{}/query?format=id'.format(self.conf.aai.server_url_version),
                         self.aai_ep._aai_versioned_path("/query?format=id"))

    def test_resolve_clli_location(self):

        req_json_file = './conductor/tests/unit/data/plugins/inventory_provider/_request_clli_location.json'
        req_json = json.loads(open(req_json_file).read())

        response = mock.MagicMock()
        response.status_code = 200
        response.ok = True
        response.json.return_value = req_json

        self.mock_get_request = mock.patch.object(AAI, '_request', return_value=response)
        self.mock_get_request.start()
        self.assertEqual({'country': u'USA', 'latitude': u'40.39596', 'longitude': u'-74.135342'} ,
                        self.aai_ep.resolve_clli_location("clli_code"))

    def test_get_inventory_group_pair(self):

        req_json_file = './conductor/tests/unit/data/plugins/inventory_provider/_request_inventory_group_pair.json'
        req_json = json.loads(open(req_json_file).read())

        response = mock.MagicMock()
        response.status_code = 200
        response.ok = True
        response.json.return_value = req_json

        self.mock_get_request = mock.patch.object(AAI, '_request', return_value=response)
        self.mock_get_request.start()
        self.assertEqual([[u'instance-1', u'instance-2']] ,
                        self.aai_ep.get_inventory_group_pairs("service_description"))

    def test_resolve_host_location(self):

        req_json_file = './conductor/tests/unit/data/plugins/inventory_provider/_request_host_name.json'
        req_json = json.loads(open(req_json_file).read())

        req_response = mock.MagicMock()
        req_response.status_code = 200
        req_response.ok = True
        req_response.json.return_value = req_json

        complex_json_file = './conductor/tests/unit/data/plugins/inventory_provider/_get_complex.json'
        complex_json = json.loads(open(complex_json_file).read())

        self.mock_get_request = mock.patch.object(AAI, '_request', return_value=req_response)
        self.mock_get_request.start()

        self.mock_get_complex = mock.patch.object(AAI, '_get_complex', return_value=complex_json)
        self.mock_get_complex.start()

        self.assertEqual({'country': u'USA', 'latitude': u'28.543251', 'longitude': u'-81.377112'} ,
                         self.aai_ep.resolve_host_location("host_name"))

    def test_resolve_demands_inventory_type_cloud(self):

        self.aai_ep.conf.HPA_enabled = True
        TraigeTranslator.getPlanIdNAme = mock.MagicMock(return_value=None)
        TraigeTranslator.addDemandsTriageTranslator = mock.MagicMock(return_value=None)

        plan_info = {
            'plan_name': 'name',
            'plan_id': 'id'
        }
        triage_translator_data = None

        demands_list_file = './conductor/tests/unit/data/plugins/inventory_provider/demand_list.json'
        demands_list = json.loads(open(demands_list_file).read())

        generic_vnf_list_file = './conductor/tests/unit/data/plugins/inventory_provider/generic_vnf_list.json'
        generic_vnf_list = json.loads(open(generic_vnf_list_file).read())

        regions_response_file = './conductor/tests/unit/data/plugins/inventory_provider/regions.json'
        regions_response = json.loads(open(regions_response_file).read())

        demand_service_response_file = './conductor/tests/unit/data/plugins/inventory_provider/resolve_demand_service_response.json'
        demand_service_response = json.loads(open(demand_service_response_file).read())

        complex_json_file = './conductor/tests/unit/data/plugins/inventory_provider/_get_complex.json'
        complex_json = json.loads(open(complex_json_file).read())

        req_response = mock.MagicMock()
        req_response.status_code = 200
        req_response.ok = True
        req_response.json.return_value = demand_service_response

        self.mock_first_level_service_call = mock.patch.object(AAI, 'first_level_service_call', return_value=generic_vnf_list)
        self.mock_first_level_service_call.start()

        self.mock_get_regions = mock.patch.object(AAI, '_get_regions', return_value=regions_response)
        self.mock_get_regions.start()

        regions_list = list()
        regions_list.append(regions_response.get('region-name'))
        self.mock_resolve_cloud_regions_by_cloud_region_id = mock.patch.object(AAI,
                                                                               'resolve_cloud_regions_by_cloud_region_id',
                                                                               return_value=regions_list)
        self.mock_resolve_cloud_regions_by_cloud_region_id.start()


        self.mock_resolve_v_server_for_candidate = mock.patch.object(AAI, 'resolve_v_server_for_candidate',
                                                                      return_value=demand_service_response)
        self.mock_resolve_v_server_for_candidate.start()

        complex_link = {"link": "/aai/v10/complex-id", "d_value": 'test-id'}
        self.mock_resolve_complex_info_link_for_v_server = mock.patch.object(AAI,
                                                                             'resolve_complex_info_link_for_v_server',
                                                                             return_value=complex_link)
        self.mock_resolve_complex_info_link_for_v_server.start()

        self.mock_get_complex = mock.patch.object(AAI, '_get_complex', return_value=complex_json)
        self.mock_get_complex.start()

        flavor_info = regions_response["region-name"]["flavors"]
        self.maxDiff = None
        self.assertCountEqual({u'demand_name': [
            {'candidate_id': u'service-instance-id', 'city': None,
             'cloud_owner': u'cloud-owner',
             'uniqueness': 'true',
             'vim-id': u'cloud-owner_cloud-region-id',
             'vlan_key': None, 'cloud_region_version': '', 'complex_name': None, 'cost': 1.0,
             'country': u'USA', 'existing_placement': 'false',
             'host_id': u'vnf-name', 'inventory_provider': 'aai',
             'inventory_type': 'service', 'latitude': u'28.543251',
             'location_id': u'cloud-region-id', 'location_type': 'att_aic',
             'longitude': u'-81.377112', 'physical_location_id': u'test-id',
             'port_key': None,
             'region': u'SE', 'service_resource_id': '',
             'sriov_automation': 'false', 'state': None},
            {'candidate_id': u'region-name', 'city': u'Middletown',
             'cloud_owner': u'cloud-owner',
             'uniqueness': 'true',
             'vim-id': u'cloud-owner_region-name',
             'cloud_region_version': u'1.0', 'complex_name': u'complex-name',
             'cost': 2.0, 'country': u'USA', 'existing_placement': 'false',
             'inventory_provider': 'aai', 'inventory_type': 'cloud',
             'latitude': u'50.34', 'location_id': u'region-name',
             'location_type': 'att_aic', 'longitude': u'30.12',
             'physical_location_id': u'complex-id',
             'region': u'USA', 'service_resource_id': u'service-resource-id-123',
             'sriov_automation': 'false', 'state': u'NJ',
             'flavors': flavor_info}]},
            self.aai_ep.resolve_demands(demands_list, plan_info=plan_info,
                                        triage_translator_data=triage_translator_data))

    def test_resolve_demands_inventory_type_service(self):
        self.aai_ep.conf.HPA_enabled = True
        TraigeTranslator.getPlanIdNAme = mock.MagicMock(return_value=None)
        TraigeTranslator.addDemandsTriageTranslator = mock.MagicMock(return_value=None)

        plan_info = {
            'plan_name': 'name',
            'plan_id': 'id'
        }
        triage_translator_data = None

        demands_list_file = './conductor/tests/unit/data/plugins/inventory_provider/service_demand_list.json'
        demands_list = json.loads(open(demands_list_file).read())

        generic_vnf_list_file = './conductor/tests/unit/data/plugins/inventory_provider/vfmodule_service_generic_vnf_list.json'
        generic_vnf_list = json.loads(open(generic_vnf_list_file).read())

        v_server_file = './conductor/tests/unit/data/plugins/inventory_provider/vfmodule_vserver.json'
        v_server = json.loads(open(v_server_file).read())

        demand_service_response_file = './conductor/tests/unit/data/plugins/inventory_provider/resolve_demand_service_response.json'
        demand_service_response = json.loads(open(demand_service_response_file).read())

        complex_file = './conductor/tests/unit/data/plugins/inventory_provider/vfmodule_complex.json'
        complex_response = json.loads(open(complex_file).read())

        region_response_file = './conductor/tests/unit/data/plugins/inventory_provider/vfmodule_region.json'
        region_response = json.loads(open(region_response_file).read())

        results_file = './conductor/tests/unit/data/plugins/inventory_provider/service_candidates.json'
        results_json = json.loads(open(results_file).read())

        req_response = mock.MagicMock()
        req_response.status_code = 200
        req_response.ok = True
        req_response.json.return_value = demand_service_response

        def mock_first_level_service_call_response(path, name, service_type):
            if "equipment-role" in path:
                return list()
            else:
                return generic_vnf_list

        self.mock_first_level_service_call = mock.patch.object(AAI, 'first_level_service_call',
                                                               side_effect=mock_first_level_service_call_response)
        self.mock_first_level_service_call.start()

        regions = list()
        regions.append(region_response)
        self.mock_resolve_cloud_regions_by_cloud_region_id = mock.patch.object(AAI,
                                                                               'resolve_cloud_regions_by_cloud_region_id',
                                                                               return_value=regions)
        self.mock_resolve_cloud_regions_by_cloud_region_id.start()

        self.mock_resolve_v_server_for_candidate = mock.patch.object(AAI, 'resolve_v_server_for_candidate',
                                                                      return_value=v_server)
        self.mock_resolve_v_server_for_candidate.start()

        complex_link = {"link": "/aai/v14/cloud-infrastructure/complexes/complex/clli1", "d_value": 'clli1'}
        self.mock_resolve_complex_info_link_for_v_server = mock.patch.object(AAI,
                                                                             'resolve_complex_info_link_for_v_server',
                                                                             return_value=complex_link)
        self.mock_resolve_complex_info_link_for_v_server.start()

        self.mock_get_complex = mock.patch.object(AAI, '_get_complex', return_value=complex_response)
        self.mock_get_complex.start()

        self.maxDiff = None
        self.assertEqual(results_json, self.aai_ep.resolve_demands(demands_list, plan_info=plan_info,
                                         triage_translator_data=triage_translator_data))

    def test_resolve_demands_inventory_type_vfmodule(self):
        self.aai_ep.conf.HPA_enabled = True
        TraigeTranslator.getPlanIdNAme = mock.MagicMock(return_value=None)
        TraigeTranslator.addDemandsTriageTranslator = mock.MagicMock(return_value=None)

        plan_info = {
            'plan_name': 'name',
            'plan_id': 'id'
        }
        triage_translator_data = None

        demands_list_file = './conductor/tests/unit/data/plugins/inventory_provider/vfmodule_demand_list.json'
        demands_list = json.loads(open(demands_list_file).read())

        generic_vnf_list_file = './conductor/tests/unit/data/plugins/inventory_provider/vfmodule_service_generic_vnf_list.json'
        generic_vnf_list = json.loads(open(generic_vnf_list_file).read())

        vfmodules_list_file = './conductor/tests/unit/data/plugins/inventory_provider/vfmodule_list.json'
        vfmodules_list = json.loads(open(vfmodules_list_file).read())

        v_server_file = './conductor/tests/unit/data/plugins/inventory_provider/vfmodule_vserver.json'
        v_server = json.loads(open(v_server_file).read())

        demand_service_response_file = './conductor/tests/unit/data/plugins/inventory_provider/resolve_demand_service_response.json'
        demand_service_response = json.loads(open(demand_service_response_file).read())

        complex_file = './conductor/tests/unit/data/plugins/inventory_provider/vfmodule_complex.json'
        complex_response = json.loads(open(complex_file).read())

        region_response_file = './conductor/tests/unit/data/plugins/inventory_provider/vfmodule_region.json'
        region_response = json.loads(open(region_response_file).read())

        results_file = './conductor/tests/unit/data/plugins/inventory_provider/vfmodule_candidates.json'
        results_json = json.loads(open(results_file).read())

        req_response = mock.MagicMock()
        req_response.status_code = 200
        req_response.ok = True
        req_response.json.return_value = demand_service_response

        def mock_first_level_service_call_response(path, name, service_type):
            if "equipment-role" in path:
                return list()
            else:
                return generic_vnf_list

        self.mock_first_level_service_call = mock.patch.object(AAI, 'first_level_service_call',
                                                               side_effect=mock_first_level_service_call_response)
        self.mock_first_level_service_call.start()

        self.mock_resolve_vf_modules_for_generic_vnf = mock.patch.object(AAI, 'resolve_vf_modules_for_generic_vnf',
                                                                         return_value=vfmodules_list)
        self.mock_resolve_vf_modules_for_generic_vnf.start()

        regions = list()
        regions.append(region_response)
        self.mock_resolve_cloud_regions_by_cloud_region_id = mock.patch.object(AAI,
                                                                               'resolve_cloud_regions_by_cloud_region_id',
                                                                               return_value=regions)
        self.mock_resolve_cloud_regions_by_cloud_region_id.start()

        self.mock_resolve_v_server_for_candidate = mock.patch.object(AAI, 'resolve_v_server_for_candidate',
                                                                       return_value=v_server)
        self.mock_resolve_v_server_for_candidate.start()

        complex_link = {"link": "/aai/v14/cloud-infrastructure/complexes/complex/clli1", "d_value": 'clli1'}
        self.mock_resolve_complex_info_link_for_v_server = mock.patch.object(AAI, 'resolve_complex_info_link_for_v_server',
                                                                             return_value=complex_link)
        self.mock_resolve_complex_info_link_for_v_server.start()

        self.mock_get_complex = mock.patch.object(AAI, '_get_complex', return_value=complex_response)
        self.mock_get_complex.start()

        self.maxDiff = None
        self.assertEqual(results_json, self.aai_ep.resolve_demands(demands_list, plan_info=plan_info,
                                         triage_translator_data=triage_translator_data))

    def test_get_complex(self):

        complex_json_file = './conductor/tests/unit/data/plugins/inventory_provider/_request_get_complex.json'
        complex_json = json.loads(open(complex_json_file).read())

        response = mock.MagicMock()
        response.status_code = 200
        response.ok = True
        response.json.return_value = complex_json

        self.mock_get_request = mock.patch.object(AAI, '_request', return_value=response)
        self.mock_get_request.start()

        self.assertEqual({u'city': u'Middletown', u'latitude': u'28.543251', u'longitude': u'-81.377112', u'country': u'USA', u'region': u'SE'},
                         self.aai_ep._get_complex("/v10/complex/complex_id", "complex_id"))

    def test_check_network_roles(self):

        network_role_json_file = './conductor/tests/unit/data/plugins/inventory_provider/_request_network_role.json'
        network_role_json = json.loads(open(network_role_json_file).read())

        response = mock.MagicMock()
        response.status_code = 200
        response.ok = True
        response.json.return_value = network_role_json

        self.mock_get_request = mock.patch.object(AAI, '_request', return_value=response)
        self.mock_get_request.start()
        self.assertEqual(set(['test-cloud-value']) ,
                        self.aai_ep.check_network_roles("network_role_id"))

    def test_check_candidate_role(self):

        candidate_role_json_file = './conductor/tests/unit/data/plugins/inventory_provider/_request_candidate_role.json'
        candidate_role_json = json.loads(open(candidate_role_json_file).read())

        response = mock.MagicMock()
        response.status_code = 200
        response.ok = True
        response.json.return_value = candidate_role_json

        self.mock_get_request = mock.patch.object(AAI, '_request', return_value=response)
        self.mock_get_request.start()

        self.assertEqual("test-role",
                         self.aai_ep.check_candidate_role("candidate_host_id"))

    def test_match_inventory_attributes(self):
        template_attributes = dict()
        template_attributes['attr-1'] = ['attr-1-value1', 'attr-1-value2']

        inventory_attributes = dict()
        inventory_attributes['attr-1'] = 'attr-1-value1'

        self.assertEqual(True,
                         self.aai_ep.match_inventory_attributes(template_attributes, inventory_attributes, "candidate-id"))

        template_attributes['attr-1'] = {
            'not': ['attr-1-value2']
        }
        self.assertEqual(True,
                         self.aai_ep.match_inventory_attributes(template_attributes, inventory_attributes,
                                                                "candidate-id"))

        template_attributes['attr-1'] = {
            'not': ['attr-1-value1']
        }
        self.assertEqual(False,
                         self.aai_ep.match_inventory_attributes(template_attributes, inventory_attributes,
                                                                "candidate-id"))

    def test_refresh_cache(self):
        regions_response_file = './conductor/tests/unit/data/plugins/inventory_provider/cache_regions.json'
        regions_response = json.loads(open(regions_response_file).read())

        complex_json_file = './conductor/tests/unit/data/plugins/inventory_provider/_cached_complex.json'
        complex_json = json.loads(open(complex_json_file).read())

        flavors_json_file = './conductor/tests/unit/data/plugins/inventory_provider/_request_get_flavors.json'
        flavors_json = json.loads(open(flavors_json_file).read())

        response = mock.MagicMock()
        response.status_code = 200
        response.ok = True
        response.json.return_value = regions_response

        self.mock_get_regions = mock.patch.object(AAI, '_request', return_value=response)
        self.mock_get_regions.start()

        self.mock_get_complex = mock.patch.object(AAI, '_get_complex', return_value=complex_json)
        self.mock_get_complex.start()

        self.mock_get_flavors = mock.patch.object(AAI, '_get_flavors',
                                                  return_value=flavors_json)
        self.mock_get_flavors.start()

        self.assertEqual(None,
                         self.aai_ep._refresh_cache())

    def test_get_aai_rel_link(self):

        relatonship_response_file = './conductor/tests/unit/data/plugins/inventory_provider/relationship_list.json'
        relatonship_response = json.loads(open(relatonship_response_file).read())
        related_to = "service-instance"

        self.assertEqual("relationship-link",
                         self.aai_ep._get_aai_rel_link(relatonship_response, related_to))

    def test_get_flavor(self):
        flavors_json_file = './conductor/tests/unit/data/plugins/inventory_provider/_request_get_flavors.json'
        flavors_json = json.loads(open(flavors_json_file).read())

        response = mock.MagicMock()
        response.json.return_value = None

        self.mock_get_request = mock.patch.object(AAI, '_request',
                                                  return_value=response)
        self.mock_get_request.start()

        flavors_info = self.aai_ep._get_flavors("mock-cloud-owner",
                                                "mock-cloud-region-id")
        self.assertEqual(None, flavors_info)

        response.status_code = 200
        response.ok = True
        response.json.return_value = flavors_json

        flavors_info = self.aai_ep._get_flavors("mock-cloud-owner",
                                                "mock-cloud-region-id")
        self.assertEqual(2, len(flavors_info['flavor']))

    def test_resolve_complex_info_link_for_v_server(self):
        TraigeTranslator.collectDroppedCandiate = mock.MagicMock(return_value=None)
        triage_translator_data = None
        demand_name = 'vPGN'
        service_type = 'vFW'
        cloud_owner = 'CloudOwner'
        cloud_region_id = 'RegionOne'
        v_server_file = './conductor/tests/unit/data/plugins/inventory_provider/vfmodule_vserver.json'
        v_server = json.loads(open(v_server_file).read())
        region_response_file = './conductor/tests/unit/data/plugins/inventory_provider/vfmodule_region.json'
        region_response = json.loads(open(region_response_file).read())

        candidate_id = 'some_id'
        location_id = 'some_location_id'
        inventory_type = 'service'

        response = mock.MagicMock()
        response.status_code = 200
        response.ok = True
        response.json.return_value = region_response

        self.mock_get_request = mock.patch.object(AAI, '_request', return_value=response)
        self.mock_get_request.start()

        link_rl_data = self.aai_ep.resolve_complex_info_link_for_v_server(candidate_id, v_server, None,
                                                                          cloud_region_id, service_type,
                                                                          demand_name, triage_translator_data)
        self.assertEqual(None, link_rl_data)

        complex_link = {"link": "/aai/v14/cloud-infrastructure/complexes/complex/clli1", "d_value": 'clli1'}
        link_rl_data = self.aai_ep.resolve_complex_info_link_for_v_server(candidate_id, v_server, cloud_owner,
                                                                          cloud_region_id, service_type,
                                                                          demand_name, triage_translator_data)
        self.assertEqual(complex_link, link_rl_data)

    def test_build_complex_info_for_candidate(self):
        TraigeTranslator.collectDroppedCandiate = mock.MagicMock(return_value=None)
        triage_translator_data = None
        demand_name = 'vPGN'
        service_type = 'vFW'
        complex_file = './conductor/tests/unit/data/plugins/inventory_provider/vfmodule_complex.json'
        complex_response = json.loads(open(complex_file).read())

        candidate = dict()
        candidate['candidate_id'] = 'some_id'
        candidate['location_id'] = 'some_location_id'
        candidate['inventory_type'] = 'service'
        initial_candidate = copy.deepcopy(candidate)
        complex_list_empty = dict()
        complex_list = list()
        complex_list.append({"link": "/aai/v14/cloud-infrastructure/complexes/complex/clli1", "d_value": 'clli1'})
        complex_list.append({"link": "/aai/v14/cloud-infrastructure/complexes/complex/clli2", "d_value": 'clli2'})

        self.mock_get_complex = mock.patch.object(AAI, '_get_complex', return_value=complex_response)
        self.mock_get_complex.start()

        self.aai_ep.build_complex_info_for_candidate(candidate['candidate_id'], candidate['location_id'], None, complex_list_empty, candidate['inventory_type'], demand_name,
                                                     triage_translator_data)
        self.assertEqual(initial_candidate, candidate)
        self.assertEqual(1, TraigeTranslator.collectDroppedCandiate.call_count)

        self.aai_ep.build_complex_info_for_candidate(candidate['candidate_id'], candidate['location_id'], None, complex_list, candidate['inventory_type'], demand_name,
                                                     triage_translator_data)
        self.assertEqual(initial_candidate, candidate)
        self.assertEqual(2, TraigeTranslator.collectDroppedCandiate.call_count)

        complex_list.pop()
        self.aai_ep.build_complex_info_for_candidate(candidate['candidate_id'], candidate['location_id'], None, complex_list, candidate['inventory_type'], demand_name,
                                                     triage_translator_data)

        self.assertEqual(self.aai_ep.build_complex_info_for_candidate(candidate['candidate_id'], candidate['location_id'], None, complex_list, candidate['inventory_type'], demand_name,
                                                     triage_translator_data), {'city': u'example-city-val-27150', 'country': u'example-country-val-94173',
                                     'region': u'example-region-val-13893', 'longitude': u'32.89948', 'state': u'example-state-val-59487',
                                     'physical_location_id': 'clli1', 'latitude': u'example-latitude-val-89101',
                                     'complex_name': u'clli1'})
        self.assertEqual(2, TraigeTranslator.collectDroppedCandiate.call_count)

    def test_resolve_vnf_parameters(self):
        TraigeTranslator.collectDroppedCandiate = mock.MagicMock(return_value=None)
        triage_translator_data = None
        demand_name = 'vPGN'
        service_type = 'vFW'
        candidate = dict()
        candidate_id = 'some_id'
        location_id = 'some_location_id'
        candidate['inventory_type'] = 'service'

        generic_vnf_list_file = './conductor/tests/unit/data/plugins/inventory_provider/vfmodule_service_generic_vnf_list.json'
        good_vnf = json.loads(open(generic_vnf_list_file).read())[0]
        bad_generic_vnf_list_file = './conductor/tests/unit/data/plugins/inventory_provider/bad_generic_vnf_list.json'
        bad_vnf = json.loads(open(bad_generic_vnf_list_file).read())[0]
        region_response_file = './conductor/tests/unit/data/plugins/inventory_provider/vfmodule_region.json'
        region_response = json.loads(open(region_response_file).read())

        regions = list()
        regions.append(region_response)
        self.mock_get_regions = mock.patch.object(AAI, 'resolve_cloud_regions_by_cloud_region_id',
                                                  return_value=regions)
        self.mock_get_regions.start()

        good_cloud_info = self.aai_ep.resolve_cloud_for_vnf(candidate_id, location_id, good_vnf, service_type,
                                                                 demand_name, triage_translator_data)
        bad_cloud_info = self.aai_ep.resolve_cloud_for_vnf(candidate_id, location_id, bad_vnf, service_type,
                                                                 demand_name, triage_translator_data)
        self.assertEqual("CloudOwner", good_cloud_info['cloud_owner'])
        self.assertEqual("RegionOne", good_cloud_info['location_id'])
        self.assertEqual("1", good_cloud_info['cloud_region_version'])

        self.assertIsNone(bad_cloud_info)

        v_server_links = list()
        v_server_links.append("/aai/v14/cloud-infrastructure/cloud-regions/cloud-region/CloudOwner/RegionOne/tenants/\
tenant/3c6c471ada7747fe8ff7f28e100b61e8/vservers/vserver/00bddefc-126e-4e4f-a18d-99b94d8d9a30")
        v_server_links.append("/aai/v14/cloud-infrastructure/cloud-regions/cloud-region/CloudOwner2/RegionOne2/tenants/\
tenant/3c6c471ada7747fe8ff7f28e100b61e8/vservers/vserver/00bddefc-126e-4e4f-a18d-99b94d8d9a31")
        self.assertEqual(v_server_links, self.aai_ep.resolve_v_server_links_for_vnf(bad_vnf))

        customer_id = 'Demonstration'
        self.assertEqual(customer_id,
                         self.aai_ep.resolve_global_customer_id_for_vnf(candidate_id, location_id, good_vnf, customer_id, service_type,
                                                                        demand_name,
                                                                        triage_translator_data).get('d_value'))
        self.assertEqual("3e8d118c-10ca-4b4b-b3db-089b5e9e6a1c",
                         self.aai_ep.resolve_service_instance_id_for_vnf(candidate_id, location_id, good_vnf, customer_id, service_type,
                                                                         demand_name,
                                                                         triage_translator_data).get('d_value'))
        self.assertIsNone(self.aai_ep.resolve_service_instance_id_for_vnf(candidate_id, location_id, bad_vnf, customer_id, service_type,
                                                                          demand_name, triage_translator_data))

    def test_add_passthrough_parameters(self):
        triage_translator_data = None

        candidate = dict()
        candidate['candidate_id'] = 'some_id'
        candidate['location_id'] = 'some_location_id'
        candidate['inventory_type'] = 'service'

        parameters = dict()
        parameters['param_one'] = "value"
        parameters['param_two'] = "value"

        candidate_info = copy.deepcopy(candidate)
        candidate_info['passthrough_attributes'] = dict()
        candidate_info['passthrough_attributes']['param_one'] = "value"
        candidate_info['passthrough_attributes']['param_two'] = "value"

        self.aai_ep.add_passthrough_attributes(candidate, parameters, 'demand')
        self.assertDictEqual(candidate, candidate_info)

    def test_match_candidate_by_list(self):
        TraigeTranslator.collectDroppedCandiate = mock.MagicMock(return_value=None)
        triage_translator_data = None

        candidate = dict()
        candidate['candidate_id'] = 'some_id'
        candidate['location_id'] = 'some_location_id'
        candidate['inventory_type'] = 'service'

        candidate_list_empty = list()
        candidate_list = list()
        candidate_info = copy.deepcopy(candidate)
        candidate_info['candidate_id'] = list()
        candidate_info['candidate_id'].append(candidate['candidate_id'])
        candidate_list.append(candidate_info)

        self.assertFalse(self.aai_ep.match_candidate_by_list(candidate, candidate_list_empty, True, 'demand',
                                                             triage_translator_data)),
        self.assertEqual(0, TraigeTranslator.collectDroppedCandiate.call_count)
        self.assertTrue(self.aai_ep.match_candidate_by_list(candidate, candidate_list, True, 'demand',
                                                            triage_translator_data))
        self.assertEqual(1, TraigeTranslator.collectDroppedCandiate.call_count)
        self.assertTrue(self.aai_ep.match_candidate_by_list(candidate, candidate_list, False, 'demand',
                                                            triage_translator_data))
        self.assertEqual(1, TraigeTranslator.collectDroppedCandiate.call_count)
        self.assertFalse(self.aai_ep.match_candidate_by_list(candidate, candidate_list_empty, False, 'demand',
                                                             triage_translator_data))
        self.assertEqual(2, TraigeTranslator.collectDroppedCandiate.call_count)

    def test_match_hpa(self):
        flavor_json_file = \
            './conductor/tests/unit/data/plugins/inventory_provider/hpa_flavors.json'
        flavor_json = json.loads(open(flavor_json_file).read())
        feature_json_file = \
            './conductor/tests/unit/data/plugins/inventory_provider/hpa_req_features.json'
        feature_json = json.loads(open(feature_json_file).read())
        candidate_json_file = './conductor/tests/unit/data/candidate_list.json'
        candidate_json = json.loads(open(candidate_json_file).read())
        candidate_json['candidate_list'][1]['flavors'] = flavor_json

        flavor_map = {
            "directives": [],
            "flavor_map": {"flavor-id": "f5aa2b2e-3206-41b6-80d5-cf041b098c43",
                           "flavor-name": "flavor-cpu-pinning-ovsdpdk-instruction-set",
                           "score": 0}}
        self.assertEqual(flavor_map,
                         match_hpa(candidate_json['candidate_list'][1],
                                               feature_json[0]))

        flavor_map = {"flavor_map": {"flavor-id": "f5aa2b2e-3206-41b6-80d5-cf041b098c43",
                                     "flavor-name": "flavor-cpu-ovsdpdk-instruction-set",
                                     "score": 10},
                      "directives": []}
        self.assertEqual(flavor_map,
                         match_hpa(candidate_json['candidate_list'][1],
                                               feature_json[1]))
        flavor_map = {"flavor_map": {"flavor-id": "f5aa2b2e-3206-41b6-80d5-cf6t2b098c43",
                                     "flavor-name": "flavor-ovsdpdk-cpu-pinning-sriov-NIC-Network-set",
                                     "score": 13},
                      "directives": [{
                          "type": "sriovNICNetwork_directives",
                          "attributes": [
                              {
                                  "attribute_name": "A",
                                  "attribute_value": "a"
                              }
                          ]
                      }]}
        self.assertEqual(flavor_map,
                         match_hpa(candidate_json['candidate_list'][1],
                                               feature_json[2]))
        self.assertEqual(None, match_hpa(candidate_json['candidate_list'][1],
                                                     feature_json[3]))
        flavor_map = {"flavor_map": {"flavor-id": "f5aa2b2e-3206-41b6-19d5-cf6t2b098c43",
                                     "flavor-name": "flavor-ovsdpdk-cpu-pinning-double-sriov-NIC-Network-set",
                                     "score": 6},
                      "directives": [
                          {
                              "type": "sriovNICNetwork_directives",
                              "attributes": [
                                  {
                                      "attribute_name": "A",
                                      "attribute_value": "a"
                                  }
                              ]
                          },
                          {
                              "type": "sriovNICNetwork_directives",
                              "attributes": [
                                  {
                                      "attribute_name": "B",
                                      "attribute_value": "b"
                                  }
                              ]
                          }]
                      }
        self.assertEqual(flavor_map, match_hpa(candidate_json['candidate_list'][1],
                                                           feature_json[4]))
        self.assertEqual(None, match_hpa(candidate_json['candidate_list'][1],
                                                     feature_json[5]))

    def test_filter_nssi_candidates(self):
        nssi_response_file = './conductor/tests/unit/data/plugins/inventory_provider/nssi_response.json'
        nssi_response = json.loads(open(nssi_response_file).read())
        nssi_candidates_file = './conductor/tests/unit/data/plugins/inventory_provider/nssi_candidate.json'
        nssi_candidates = json.loads(open(nssi_candidates_file).read())

        service_role = 'nssi'
        second_level_filter = dict()
        second_level_filter['service-role'] = service_role
        default_attributes = dict()
        default_attributes['creation_cost'] =1
        self.assertEqual(nssi_candidates, self.aai_ep.filter_nxi_candidates(nssi_response, second_level_filter,
                                                                            default_attributes, "true", service_role))

        nssi_response['service-instance'][0]['service-role'] = 'service'

        self.assertEqual([], self.aai_ep.filter_nxi_candidates(nssi_response, second_level_filter, default_attributes,
                                                               "true", service_role))

        self.assertEqual([], self.aai_ep.filter_nxi_candidates(None, second_level_filter, default_attributes,
                                                               "true", service_role))

        self.assertEqual([], self.aai_ep.filter_nxi_candidates(None, None, default_attributes, "true", service_role))

        self.assertEqual(nssi_candidates, self.aai_ep.filter_nxi_candidates(nssi_response, None, default_attributes,
                                                                            "true", service_role))
        del nssi_candidates[0]['creation_cost']
        self.assertEqual(nssi_candidates, self.aai_ep.filter_nxi_candidates(nssi_response, None, None, "true",
                                                                            service_role))

    def test_resolve_demands_inventory_type_nssi(self):
        self.aai_ep.conf.HPA_enabled = True
        TraigeTranslator.getPlanIdNAme = mock.MagicMock(return_value=None)
        TraigeTranslator.addDemandsTriageTranslator = mock.MagicMock(return_value=None)

        plan_info = {
            'plan_name': 'name',
            'plan_id': 'id'
        }
        triage_translator_data = None

        demands_list_file = './conductor/tests/unit/data/plugins/inventory_provider/nssi_demand_list.json'
        demands_list = json.loads(open(demands_list_file).read())

        nssi_response_file = './conductor/tests/unit/data/plugins/inventory_provider/nssi_response.json'
        nssi_response = json.loads(open(nssi_response_file).read())
        nssi_candidates_file = './conductor/tests/unit/data/plugins/inventory_provider/nssi_candidate.json'
        nssi_candidates = json.loads(open(nssi_candidates_file).read())
        result = dict()
        result['embb_cn'] = nssi_candidates

        self.mock_get_nxi_candidates = mock.patch.object(AAI, 'get_nxi_candidates',
                                                         return_value=nssi_response)
        self.mock_get_nxi_candidates.start()

        self.assertEqual(result, self.aai_ep.resolve_demands(demands_list, plan_info=plan_info,
                                                             triage_translator_data=triage_translator_data))

    def test_filter_nsi_candidates(self):
        nsi_response_file = './conductor/tests/unit/data/plugins/inventory_provider/nsi_response.json'
        nsi_response = json.loads(open(nsi_response_file).read())
        nsi_candidates_file = './conductor/tests/unit/data/plugins/inventory_provider/nsi_candidate.json'
        nsi_candidates = json.loads(open(nsi_candidates_file).read())

        service_role = 'nsi'
        second_level_filter = dict()
        second_level_filter['service-role'] = service_role
        default_attributes = dict()
        default_attributes['creation_cost'] = 1

        self.assertEqual(nsi_candidates, self.aai_ep.filter_nxi_candidates(nsi_response, second_level_filter,
                                                                           default_attributes, "true", service_role))
        nsi_response['service-instance'][0]['service-role'] = 'service'

        self.assertEqual([], self.aai_ep.filter_nxi_candidates(nsi_response, second_level_filter, default_attributes,
                                                               "true", service_role))

    def test_resolve_demands_inventory_type_nsi(self):
        self.aai_ep.conf.HPA_enabled = True
        TraigeTranslator.getPlanIdNAme = mock.MagicMock(return_value=None)
        TraigeTranslator.addDemandsTriageTranslator = mock.MagicMock(return_value=None)

        plan_info = {
            'plan_name': 'name',
            'plan_id': 'id'
        }
        triage_translator_data = None

        demands_list_file = './conductor/tests/unit/data/plugins/inventory_provider/nsi_demand_list.json'
        demands_list = json.loads(open(demands_list_file).read())

        nsi_response_file = './conductor/tests/unit/data/plugins/inventory_provider/nsi_response.json'
        nsi_response = json.loads(open(nsi_response_file).read())
        nsi_candidates_file = './conductor/tests/unit/data/plugins/inventory_provider/nsi_candidate.json'
        nsi_candidates = json.loads(open(nsi_candidates_file).read())
        result = dict()
        result['embb_nst'] = nsi_candidates

        self.mock_get_nxi_candidates = mock.patch.object(AAI, 'get_nxi_candidates',
                                                         return_value=nsi_response)
        self.mock_get_nxi_candidates.start()
        self.maxDiff = None
        self.assertEqual(result, self.aai_ep.resolve_demands(demands_list, plan_info=plan_info,
                                                             triage_translator_data=triage_translator_data))


    def test_get_nst_candidates(self):
        nst_response_file = './conductor/tests/unit/data/plugins/inventory_provider/nst_response.json'
        nst_response = json.loads(open(nst_response_file).read())
        nst_candidates_file = './conductor/tests/unit/data/plugins/inventory_provider/nst_candidate.json'
        nst_candidates = json.loads(open(nst_candidates_file).read())


        second_level_filter=None

        default_attributes = dict()
        default_attributes['creation_cost'] = 1
        self.assertEqual("5d345ca8-1f8e-4f1e-aac7-6c8b33cc33e7", self.aai_ep.get_nst_candidates(nst_response, second_level_filter,
                                                                           default_attributes, "true", "nst").__getitem__(0).__getattribute__('candidate_id'))


    def test_resolve_demands_inventory_type_nst(self):
        self.aai_ep.conf.HPA_enabled = True
        TraigeTranslator.getPlanIdNAme = mock.MagicMock(return_value=None)
        TraigeTranslator.addDemandsTriageTranslator = mock.MagicMock(return_value=None)

        plan_info = {
            'plan_name': 'name',
            'plan_id': 'id'
        }
        triage_translator_data = None

        demands_list_file = './conductor/tests/unit/data/plugins/inventory_provider/nst_demand_list.json'
        demands_list = json.loads(open(demands_list_file).read())

        nst_response_file = './conductor/tests/unit/data/plugins/inventory_provider/nst_response.json'
        nst_response = json.loads(open(nst_response_file).read())
        nst_candidates_file = './conductor/tests/unit/data/plugins/inventory_provider/nst_candidate.json'
        nst_candidates = json.loads(open(nst_candidates_file).read())
        final_nst_candidates_file = './conductor/tests/unit/data/plugins/inventory_provider/final_nst_candidate.json'
        final_nst_candidates = json.loads(open(final_nst_candidates_file).read())
        result = dict()
        result['embb_nst'] = final_nst_candidates

        self.mock_get_nst_candidates = mock.patch.object(AAI, 'get_nst_response',
                                                         return_value=nst_response)
        self.mock_get_final_nst_candidates = mock.patch.object(SDC, 'get_sdc_response',
                                                         return_value=final_nst_candidates)
        self.mock_get_nst_candidates.start()
        self.mock_get_final_nst_candidates.start()
        self.maxDiff = None
        self.assertEqual(result, self.aai_ep.resolve_demands(demands_list, plan_info=plan_info,
                                                             triage_translator_data=triage_translator_data))

    def test_get_aai_data(self):
        nst_response_file = './conductor/tests/unit/data/plugins/inventory_provider/nst_response.json'
        nst_response = json.loads(open(nst_response_file).read())
        response = mock.MagicMock()
        response.status_code = 200
        response.ok = True
        response.json.return_value = nst_response
        self.mock_get_request = mock.patch.object(AAI, '_request', return_value=response)
        self.mock_get_request.start()
        filtering_attr={"model-role":"NST"}
        self.assertEquals(nst_response, self.aai_ep.get_nst_response(filtering_attr))
