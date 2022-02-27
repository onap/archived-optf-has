import json
import mock
import unittest

from unittest.mock import patch, Mock
from oslo_config import cfg
import conductor.data.plugins.inventory_provider.dcae as dcae
from conductor.data.plugins.inventory_provider.dcae import DCAE



class TestDCAE(unittest.TestCase):
    
    def setUp(self): 
        CONF = cfg.CONF
        CONF.register_opts(dcae.DCAE_OPTS, group='dcae')
        self.conf = CONF
        self.dcae_ep = DCAE()
    
    
    def tearDown(self):
        mock.patch.stopall()
    
    
    def test_get_dcae_response(self):
        nssi_candidate_file = './conductor/tests/unit/data/plugins/inventory_provider/nssi_candidate.json'
        uLThptDiff = 70
        dLThptDiff = 73
        nssi_candidates = json.loads(open(nssi_candidate_file).read())
        candidates=[]
        for nssi_candidate in nssi_candidates:
            inventory_type=nssi_candidate.get("inventory_type")
            if inventory_type == 'nssi':
                candidates.extend(nssi_candidates)
        final_nssi_candidates_file = './conductor/tests/unit/data/plugins/inventory_provider/nssi_candidate_updated.json'
        final_nssi_candidates = json.loads(open(final_nssi_candidates_file).read())
        response = mock.MagicMock()
        response.content = None
        ff = open('./conductor/tests/unit/data/plugins/inventory_provider/dcae_response.json', "rb")
        file_res = ff.read()
        response.status_code = 200
        response.ok = True
        response.content=file_res
        self.mock_get_request = mock.patch.object(DCAE, 'get_dcae_response',
                return_value=response)
        self.mock_get_request.start()
        self.maxDiff=None
        response1 = mock.MagicMock()
        response1.status_code = 200
        response1.ok = True
        response1.json.return_value = 100
        self.mock_get_dLThpt = mock.patch.object(DCAE, 'get_dLThpt', return_value=response1)
        self.mock_get_dLThpt.start()
        self.mock_get_uLThpt = mock.patch.object(DCAE, 'get_uLThpt', return_value=response1)
        self.mock_get_uLThpt.start()
        self.dcae_ep.get_difference = Mock(return_value = 70)
        self.assertEqual(final_nssi_candidates,
                self.dcae_ep.capacity_filter(candidates))
        
        
    def test_get_difference(self):
        a = 20
        b = 10
        difference = a-b
        self.assertEqual(difference, self.dcae_ep.get_difference(a,b))
        
        
    def test_get_uLThpt(self):
        uLThpt = 30
        candidate_id = "cdad9f49-4201-4e3a-aac1-b0f27902c299"
        ff = open('./conductor/tests/unit/data/plugins/inventory_provider/dcae_response.json')
        file_res = ff.read()
        self.assertEqual(uLThpt, self.dcae_ep.get_uLThpt(file_res,candidate_id))
    
    
    def test_get_dLThpt(self):
        dLThpt = 27
        candidate_id = "cdad9f49-4201-4e3a-aac1-b0f27902c299"
        ff = open('./conductor/tests/unit/data/plugins/inventory_provider/dcae_response.json')
        file_res = ff.read()
        self.assertEqual(dLThpt, self.dcae_ep.get_dLThpt(file_res,candidate_id))











