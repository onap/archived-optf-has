import json
import mock
import unittest



from oslo_config import cfg
import conductor.data.plugins.inventory_provider.sdc as sdc
from conductor.data.plugins.inventory_provider.sdc import SDC
from conductor.data.plugins.inventory_provider.candidates.nst_candidate import NST



class TestSDC(unittest.TestCase):

    def setUp(self):
        cfg.CONF.set_override('password', '4HyU6sI+Tw0YMXgSHr5sJ5C0UTkeBaxXoxQqWuSVFugls7sQnaAXp4zMfJ8FKFrH', 'aai')
        CONF = cfg.CONF
        CONF.register_opts(sdc.SDC_OPTS, group='sdc')
        self.conf = CONF
        self.sdc_ep = SDC()

    def tearDown(self):
        mock.patch.stopall()

    def test_get_sdc_response(self):
        nst_candidates_file = './conductor/tests/unit/data/plugins/inventory_provider/nst_candidate.json'
        nst_candidates = json.loads(open(nst_candidates_file).read())
        info={}
        candidates=[]
        for nst_candidate in nst_candidates:
            info["candidate_id"]=nst_candidate.get("candidate_id")
            info['inventory_provider']=nst_candidate.get("inventory_provider")
            info['inventory_type']=nst_candidate.get("inventory_type")
            info['uniqueness']=nst_candidate.get("uniqueness")
            info['cost']=nst_candidate.get("cost")
            candidate= NST(instance_info=nst_candidate.get('instance_info'), model_ver=nst_candidate.get('model_ver'), info=info,
                           default_fields=nst_candidate.get('default_fields'),profile_info=nst_candidate.get('profile_info'))
            candidates.append(candidate)
        final_nst_candidates_file = './conductor/tests/unit/data/plugins/inventory_provider/final_nst_candidate.json'
        final_nst_candidates = json.loads(open(final_nst_candidates_file).read())
        response = mock.MagicMock()
        response.content = None
        ff = open('./conductor/tests/unit/data/plugins/inventory_provider/newembbnst.csar',"rb")
        file_res = ff.read()
        response.status_code = 200
        response.ok = True
        response.content=file_res
        self.mock_get_request = mock.patch.object(SDC, 'get_nst_template',
                                                  return_value=response)
        self.mock_get_request.start()
        self.maxDiff=None
        self.assertEqual(final_nst_candidates,
                         self.sdc_ep.get_sdc_response(candidates))




    def test_get_nst_prop_dict(self):
        nst_properties_file = './conductor/tests/unit/data/plugins/inventory_provider/nst_properties.json'
        nst_candidates = json.loads(open(nst_properties_file).read())
        nst_output_file = './conductor/tests/unit/data/plugins/inventory_provider/nst_prop_dict.json'
        nst_output = json.loads(open(nst_output_file).read())
        self.assertEqual(nst_output,
                             self.sdc_ep.get_nst_prop_dict(nst_candidates))


    def test_sdc_versioned_path(self):

        self.assertEqual("/{}/catalog/services/5d345ca8-1f8e-4f1e-aac7-6c8b33cc33e7/toscaModel".format(self.conf.sdc.server_url_version),
                         self.sdc_ep._sdc_versioned_path("/catalog/services/5d345ca8-1f8e-4f1e-aac7-6c8b33cc33e7/toscaModel"))





