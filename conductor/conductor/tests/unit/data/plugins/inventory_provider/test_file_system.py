import unittest

from oslo_config import cfg

import conductor.data.plugins.file_system.config as config


class TestConfig(unittest.TestCase):

    def setUp(self):
        cli_opts = [
            cfg.BoolOpt('debug',
                        short='d',
                        default=False,
                        help='Print debugging output.'),
        ]
        cfg.CONF.register_cli_opts(cli_opts)
        self.config_ep = config.CONFIG()

    def test_get_candidates(self):
        plan_info = {
            'plan_name': 'nst_selection',
            'plan_id': 'id'
        }
        triage_translator_data = {'plan_id': None, 'plan_name': [None]}
        demands = {'NST': [{'inventory_provider': 'file_system', 'inventory_type': 'NST'}]}
        actual_result = self.config_ep.get_candidates(demands, plan_info=plan_info,
                                                      triage_translator_data=triage_translator_data)
        expected_result ={'NST': [{'candidate_id': 'NST1', 'NST_name': 'NST1', 'cost': 2, 'inventory_provider': 'file_system', 'inventory_type': 'NST', 'latency': 10, 'reliability': 100}, {'candidate_id': 'NST2', 'NST_name': 'NST2', 'cost': 2, 'inventory_provider': 'file_system', 'inventory_type': 'NST', 'latency': 1, 'reliability': 90}]}
        self.assertEqual(actual_result, expected_result)




if __name__ == "__main__":
    unittest.main()
