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
import mock
import conductor.data.plugins.inventory_provider.aai as aai
from conductor.data.plugins.inventory_provider.aai import AAI
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

        complex_json_file = './conductor/tests/unit/data/plugins/inventory_provider/_get_complex_host_name.json'
        complex_json = json.loads(open(complex_json_file).read())

        self.mock_get_request = mock.patch.object(AAI, '_request', return_value=req_response)
        self.mock_get_request.start()

        self.mock_get_complex = mock.patch.object(AAI, '_get_complex', return_value=complex_json)
        self.mock_get_complex.start()

        self.assertEqual({'country': u'USA', 'latitude': u'28.543251', 'longitude': u'-81.377112'} ,
                         self.aai_ep.resolve_host_location("host_name"))

    def test_resolve_demands(self):

        self.assertEqual({}, self.aai_ep.resolve_demands(dict()))

        demands_list_file = './conductor/tests/unit/data/plugins/inventory_provider/demand_list.json'
        demands_list = json.loads(open(demands_list_file).read())

        generic_vnf_list_file = './conductor/tests/unit/data/plugins/inventory_provider/generic_vnf_list.json'
        generic_vnf_list = json.loads(open(generic_vnf_list_file).read())

        regions_response_file = './conductor/tests/unit/data/plugins/inventory_provider/regions.json'
        regions_response = json.loads(open(regions_response_file).read())

        req_response = mock.MagicMock()
        req_response.status_code = 200
        req_response.ok = True
        req_response.json.return_value = generic_vnf_list

        self.mock_first_level_service_call = mock.patch.object(AAI, 'first_level_service_call', return_value=req_response)
        self.mock_first_level_service_call.start()

        self.mock_get_regions = mock.patch.object(AAI, '_get_regions', return_value=regions_response)
        self.mock_get_regions.start()

        self.maxDiff = None
        self.assertEqual({u'demand_name': [{'sriov_automation': 'false', 'longitude': u'30.12', 'inventory_type': 'cloud', 'inventory_provider': 'aai', 'cloud_owner': u'cloud-owner', 'cloud_region_version': u'1.0', 'service_resource_id': u'service-resource-id-123', 'city': u'Middletown', 'state': u'NJ', 'country': u'USA', 'existing_placement': 'false', 'location_type': 'att_aic', 'location_id': u'region-name', 'complex_name': u'complex-name', 'latitude': u'50.34', 'candidate_id': u'region-name', 'cost': 2.0, 'physical_location_id': u'complex-id', 'region': u'USA'}]} ,
                         self.aai_ep.resolve_demands(demands_list))


    #check_network_roles


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