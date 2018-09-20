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
import json
import unittest

import conductor.data.plugins.inventory_provider.aai as aai
import mock
from conductor.data.plugins.inventory_provider.aai import AAI
from conductor.data.plugins.triage_translator.triage_translator import TraigeTranslator
from oslo_config import cfg


class TestAAI(unittest.TestCase):

    def setUp(self):

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

    def test_resolve_demands(self):

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

        self.mock_get_regions = mock.patch.object(AAI, '_request', return_value=req_response)
        self.mock_get_regions.start()

        self.mock_get_complex = mock.patch.object(AAI, '_get_complex', return_value=complex_json)
        self.mock_get_complex.start()

        flavor_info = regions_response["region-name"]["flavors"]
        self.maxDiff = None
        self.assertEqual({u'demand_name': [
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

    def test_get_complex(self):

        complex_json_file = './conductor/tests/unit/data/plugins/inventory_provider/_request_get_complex.json'
        complex_json = json.loads(open(complex_json_file).read())

        response = mock.MagicMock()
        response.status_code = 200
        response.ok = True
        response.json.return_value = complex_json

        self.mock_get_request = mock.patch.object(AAI, '_request', return_value=response)
        self.mock_get_request.start()

        self.assertEqual({u'city': u'Middletown', u'latitude': u'28.543251', u'longitude': u'-81.377112', u'country': u'USA', u'region': u'SE'} ,
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

    # def test_match_hpa(self):
    #     flavor_json_file = \
    #        './conductor/tests/unit/data/plugins/inventory_provider/hpa_flavors.json'
    #     flavor_json = json.loads(open(flavor_json_file).read())
    #     feature_json_file = \
    #         './conductor/tests/unit/data/plugins/inventory_provider/hpa_req_features.json'
    #     feature_json = json.loads(open(feature_json_file).read())
    #     candidate_json_file = './conductor/tests/unit/data/candidate_list.json'
    #     candidate_json = json.loads(open(candidate_json_file).read())
    #     candidate_json['candidate_list'][1]['flavors'] = flavor_json
    #
    #     flavor_map = {"flavor-id": "f5aa2b2e-3206-41b6-80d5-cf041b098c43",
    #                   "flavor-name": "flavor-cpu-pinning-ovsdpdk-instruction-set"}
    #     self.assertEqual(flavor_map,
    #                      self.aai_ep.match_hpa(candidate_json['candidate_list'][1],
    #                                            feature_json[0]))
    #
    #     flavor_map = {"flavor-id": "f5aa2b2e-3206-41b6-80d5-cf041b098c43",
    #                   "flavor-name": "flavor-cpu-ovsdpdk-instruction-set" }
    #     self.assertEqual({},
    #          self.aai_ep.match_hpa(candidate_json['candidate_list'][1],
    #                                feature_json[1]))
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
                         self.aai_ep.match_hpa(candidate_json['candidate_list'][1],
                                               feature_json[0]))

        flavor_map = {"flavor_map": {"flavor-id": "f5aa2b2e-3206-41b6-80d5-cf041b098c43",
                                     "flavor-name": "flavor-cpu-ovsdpdk-instruction-set",
                                     "score": 10},
                      "directives": []}
        self.assertEqual(flavor_map,
                         self.aai_ep.match_hpa(candidate_json['candidate_list'][1],
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
                         self.aai_ep.match_hpa(candidate_json['candidate_list'][1],
                                               feature_json[2]))
        self.assertEqual(None, self.aai_ep.match_hpa(candidate_json['candidate_list'][1],
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
        self.assertEqual(flavor_map, self.aai_ep.match_hpa(candidate_json['candidate_list'][1],
                                                           feature_json[4]))
        self.assertEqual(None, self.aai_ep.match_hpa(candidate_json['candidate_list'][1],
                                                     feature_json[5]))


