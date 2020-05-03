import unittest
import yaml
import conductor.data.plugins.file_system.filereader as filereader
from conductor.data.plugins.inventory_provider import extensions as ip_ext
from conductor.data.plugins.service_controller import extensions as sc_ext
from conductor.data.plugins.file_system import extensions as fs_ext
from conductor.data.plugins.vim_controller import extensions as vc_ext
from conductor.data.service import DataEndpoint
from oslo_config import cfg


class TestConfig(unittest.TestCase):

    def setUp(self):
        cli_opts = [
            cfg.BoolOpt('debug',
                        short='d',
                        default=False,
                        help='Print debugging output.'),
        ]
        cfg.CONF.register_cli_opts(cli_opts)
        self.filereader_ep = filereader.FILEREADER()
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

    def test_get_candidates(self):
        request_json_file = './conductor/tests/unit/data/demands_NST.json'
        result_json_file = './conductor/tests/unit/data/result_NST.json'
        res_json = yaml.safe_load(open(result_json_file).read())
        req_json = yaml.safe_load(open(request_json_file).read())
        plan_info = req_json["plan_info"]
        demands = req_json["demands"]
        triage_translator_data = req_json["triage_translator_data"]
        dataFilePath = './conductor/data/plugins/file_system/NST.json'
        actual_result = self.filereader_ep.get_candidates(demands, plan_info=plan_info,
                                                      triage_translator_data=triage_translator_data, dataFilePath = dataFilePath)
        expected_result = res_json['response']['resolved_demands']
        self.assertEqual(actual_result, expected_result)


if __name__ == "__main__":
    unittest.main()
