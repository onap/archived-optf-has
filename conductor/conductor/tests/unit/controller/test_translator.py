#
# ------------------------------------------------------------------------
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
"""Test classes for translator"""

import mock
import os
import unittest
import uuid

import yaml
from conductor import __file__ as conductor_root
from conductor.controller.translator import Translator
from conductor.controller.translator import TranslatorException
from conductor.data.plugins.triage_translator.triage_translator import TraigeTranslator
from mock import patch
from oslo_config import cfg


def get_template():
    template_name = 'some_template'
    path = os.path.abspath(conductor_root)
    dir_path = os.path.dirname(path)
    template_file = dir_path + '/tests/data/' + template_name + '.yaml'
    fd = open(template_file, "r")
    template = yaml.load(fd)
    return template


class TestNoExceptionTranslator(unittest.TestCase):
    @patch('conductor.common.music.model.base.Base.table_create')
    def setUp(self, mock_table_create):
        cfg.CONF.set_override('keyspace', 'conductor')
        cfg.CONF.set_override('keyspace', 'conductor_rpc', 'messaging_server')
        cfg.CONF.set_override('concurrent', True, 'controller')
        cfg.CONF.set_override('certificate_authority_bundle_file', '../AAF_RootCA.cer', 'music_api')
        conf = cfg.CONF
        self.Translator = Translator(
            conf, 'some_template', str(uuid.uuid4()), get_template())

    def test_create_correct_components(self):
        self.Translator.create_components()
        self.assertIsNotNone(self.Translator._version)
        self.assertIsNotNone(self.Translator._parameters)
        self.assertIsNotNone(self.Translator._constraints)
        self.assertIsNotNone(self.Translator._demands)
        self.assertIsNotNone(self.Translator._locations)
        self.assertIsNotNone(self.Translator._reservations)
        self.assertIsNotNone(self.Translator._optmization)
        self.assertIsInstance(self.Translator._version, str)

    def test_error_version_validation(self):
        self.Translator._version = "2016-11-02"
        self.assertRaises(TranslatorException,
                          self.Translator.validate_components, )

    def test_error_format_validation(self):
        self.Translator._version = "2016-11-01"
        self.Translator._locations = ""
        self.Translator._demands = ""
        self.Translator._constraints = ""
        self.Translator._reservations = ""
        self.Translator._optmization = ""
        self.Translator._parameters = ""
        self.assertRaises(TranslatorException,
                          self.Translator.validate_components, )

    def test_validation_complete(self):
        self.Translator._demands = {'vG': ''}
        self.Translator._version = "2016-11-01"
        self.Translator._locations = {'custom_loc': {'longitude': ''}}
        self.Translator._constraints = {'vG': {
            'demands': 'vG',
            'properties': {'location': 'custom_loc'}}}
        self.Translator._parameters = {}
        self.Translator._optmization = {}
        self.Translator._reservations = {}
        self.Translator.validate_components()
        self.assertTrue(self.Translator._valid)

    @patch('conductor.controller.translator.Translator._parse_parameters')
    def test_parse_parameters(self, mock_parse):
        self.Translator._locations = ''
        self.Translator._demands = ''
        self.Translator._constraints = ''
        self.Translator._reservations = ''
        self.Translator.parse_parameters()
        mock_parse.assert_called()

    def test_parse_parameter(self):
        self.Translator.create_components()
        rtn = self.Translator._parse_parameters(
            self.Translator._locations, "locations")
        location = {'customer_loc': {
            'latitude': 32.89748, 'longitude': -97.040443}}
        self.assertEquals(rtn, location)

    @patch('conductor.common.music.messaging.component.RPCClient.call')
    def test_parse_locations(self, mock_call):
        locations = {'customer_loc': {
            'latitude': 32.89748, 'longitude': -97.040443}
        }
        mock_call.return_value = {'resolved_location': {
            'latitude': 32.89748, 'longitude': -97.040443}}
        self.assertEquals(
            self.Translator.parse_locations(locations), locations)

    def test_parse_error_format_demands(self):
        demands = ""
        self.assertRaises(TranslatorException,
                          self.Translator.parse_demands, demands)

    @patch('conductor.common.music.messaging.component.RPCClient.call')
    def test_parse_demands_with_candidate(self, mock_call):
        TraigeTranslator.thefinalCallTrans = mock.MagicMock(return_value=None)
        demands = {
            "vGMuxInfra": [{
                "inventory_provider": "aai",
                "inventory_type": "service",
                "customer_id": "some_company",
                "service_type": "5G",
                "candidates": [{
                    "candidate_id": []

                }],
                "required_candidates": [{
                    "candidate_id": "1a9983b8-0o43-4e16-9947-c3f37234536d"
                }]
            }]
        }
        self.Translator._plan_id = ""
        self.Translator._plan_name = ""
        mock_call.return_value = {'resolved_demands': {"vGMuxInfra": [{
            'inventory_provider': 'aai',
            'inventory_type': 'service',
            'customer_id': 'some_company',
            'service_type': '5G',
            "candidates": {
                "candidate_id": []
            }
        }]
        }}
        rtn = {'vGMuxInfra': {'candidates': [{'candidate_id': [],
                                              'cost': 0,
                                              'inventory_provider': 'aai'},
                                             {'candidates': {'candidate_id': []},
                                              'customer_id': 'some_company',
                                              'inventory_provider': 'aai',
                                              'inventory_type': 'service',
                                              'service_type': '5G'}]}}

        self.assertEquals(self.Translator.parse_demands(demands), rtn)

    @patch('conductor.common.music.messaging.component.RPCClient.call')
    def test_parse_demands_inventory_type_vfmodule(self, mock_call):
        TraigeTranslator.thefinalCallTrans = mock.MagicMock(return_value=None)
        demands = {
            "vFW-SINK": [{
                "service_resource_id": "vFW-SINK-XX",
                "inventory_provider": "aai",
                "inventory_type": "vfmodule",
                "vlan_key": "vlan_key",
                "port_key": "vlan_port",
                "excluded_candidates": [{
                    "candidate_id": ["e765d576-8755-4145-8536-0bb6d9b1dc9a"],
                    "inventory_type": "vfmodule"
                }],
                "attributes": {
                    "prov-status": "ACTIVE",
                    "global-customer-id": "Demonstration",
                    "model-version-id": "763731df-84fd-494b-b824-01fc59a5ff2d",
                    "model-invariant-id": "e7227847-dea6-4374-abca-4561b070fe7d",
                    "orchestration-status": ["active"],
                    "cloud-region-id": {
                        "get_param": "chosen_region"
                    },
                    "service_instance_id": {
                        "get_param": "service_id"
                    }
                },
                "service_type": "vFW-SINK-XX"
            }]
        }
        self.Translator._plan_id = ""
        self.Translator._plan_name = ""
        mock_call.return_value = {'resolved_demands': {
            "vFW-SINK": [{
                "service_resource_id": "vFW-SINK-XX",
                "inventory_provider": "aai",
                "inventory_type": "vfmodule",
                "vlan_key": "vlan_key",
                "port_key": "vlan_port",
                "excluded_candidates": [{
                    "candidate_id": ["e765d576-8755-4145-8536-0bb6d9b1dc9a"],
                    "inventory_type": "vfmodule"
                }],
                "attributes": {
                    "prov-status": "ACTIVE",
                    "global-customer-id": "Demonstration",
                    "model-version-id": "763731df-84fd-494b-b824-01fc59a5ff2d",
                    "model-invariant-id": "e7227847-dea6-4374-abca-4561b070fe7d",
                    "orchestration-status": ["active"],
                    "cloud-region-id": {
                        "get_param": "chosen_region"
                    },
                    "service_instance_id": {
                        "get_param": "service_id"
                    }
                },
                "service_type": "vFW-SINK-XX"
            }]
        }}
        rtn = {
            "vFW-SINK": {
                "candidates": [{
                    "excluded_candidates": [{
                        "candidate_id": ["e765d576-8755-4145-8536-0bb6d9b1dc9a"],
                        "inventory_type": "vfmodule"
                    }],
                    "port_key": "vlan_port",
                    "service_resource_id": "vFW-SINK-XX",
                    "vlan_key": "vlan_key",
                    "service_type": "vFW-SINK-XX",
                    "attributes": {
                        "cloud-region-id": {
                            "get_param": "chosen_region"
                        },
                        "model-version-id": "763731df-84fd-494b-b824-01fc59a5ff2d",
                        "service_instance_id": {
                            "get_param": "service_id"
                        },
                        "orchestration-status": ["active"],
                        "global-customer-id": "Demonstration",
                        "prov-status": "ACTIVE",
                        "model-invariant-id": "e7227847-dea6-4374-abca-4561b070fe7d"
                    },
                    "inventory_provider": "aai",
                    "inventory_type": "vfmodule"
                }]
            }
        }

        self.assertEquals(self.Translator.parse_demands(demands), rtn)

    @patch('conductor.common.music.messaging.component.RPCClient.call')
    def test_parse_demands_without_candidate(self, mock_call):
        TraigeTranslator.thefinalCallTrans = mock.MagicMock(return_value=None)
        demands = {
            "vGMuxInfra": [{
                "inventory_provider": "aai",
                "inventory_type": "service",
                "customer_id": "some_company",
                "service_type": "5G",
                "excluded_candidates": [{
                    "candidate_id": "1ac71fb8-ad43-4e16-9459-c3f372b8236d"
                }],
                "required_candidates": [{
                    "candidate_id": "1a9983b8-0o43-4e16-9947-c3f37234536d"
                }]
            }
            ]}
        self.Translator._plan_id = ""
        self.Translator._plan_name = ""
        mock_call.return_value = {'resolved_demands': {"vGMuxInfra": [{
            "inventory_provider": "aai",
            "inventory_type": "service",
            "customer_id": "some_company",
            "service_type": "5G",
            "excluded_candidates": [{
                "candidate_id:1ac71fb8-ad43-4e16-9459-c3f372b8236d"
            }],
            "required_candidates": [{
                "candidate_id": "1a9983b8-0o43-4e16-9947-c3f37234536d"}]

        }]
        }}
        rtn = {'vGMuxInfra': {'candidates': [{
            'customer_id': 'some_company',
            'excluded_candidates': [set([
                'candidate_id:1ac71fb8-ad43-4e16-9459-c3f372b8236d'])],
            'inventory_provider': 'aai',
            'inventory_type': 'service',
            'required_candidates': [{
                'candidate_id': '1a9983b8-0o43-4e16-9947-c3f37234536d'
            }],
            'service_type': '5G'}]}}

        self.assertEquals(self.Translator.parse_demands(demands), rtn)

    def test_parse_constraints(self):
        constraints = {'constraint_loc': {
            'type': 'distance_to_location',
            'demands': ['vG'],
            'properties': {'distance': '< 100 km',
                           'location': 'custom_loc'}}}

        rtn = {'constraint_loc_vG': {
            'demands': 'vG',
            'name': 'constraint_loc',
            'properties': {'distance': {'operator': '<',
                                        'units': 'km',
                                        'value': 100.0},
                           'location': 'custom_loc'},
            'type': 'distance_to_location'}}
        self.assertEquals(self.Translator.parse_constraints(constraints), rtn)

    def test_parse_hpa_constraints(self):
        hpa_constraint = {
            "hpa_constraint": {
                "type": "hpa",
                "demands": [
                    "vG"
                ],
                "properties": {
                    "evaluate": [
                        {'id': 'vg_0',
                         'type': 'vnfc',
                         'directives': [
                             {
                                 "type": "flavor_directives",
                                 "attributes": [
                                     {
                                         "attribute_name": "label_0",
                                         "attribute_value": ""
                                     }
                                 ]
                             }
                         ],
                         'flavorProperties': [{
                             'hpa-feature': 'BasicCapabilities',
                             'hpa-version': 'v1',
                             'architecture': 'generic',
                             'mandatory': 'False',
                             'directives': [],
                             'score': '5',
                             'hpa-feature-attributes': [
                                 {
                                     'hpa-attribute-key': 'numVirtualCpu',
                                     'hpa-attribute-value': '4',
                                     'operator': '='
                                 },
                                 {
                                     'hpa-attribute-key': 'virtualMemSize',
                                     'hpa-attribute-value': '4',
                                     'operator': '=',
                                     'unit': 'GB'
                                 }
                             ]
                         }], }
                    ]
                }}}
        rtn = {
            'hpa_constraint_vG': {
                'demands': 'vG',
                'name': 'hpa_constraint',
                'properties': {'evaluate': [{
                    'flavorProperties': [
                        {'architecture': 'generic',
                         'mandatory': 'False',
                         'score': '5',
                         'directives': [],
                         'hpa-feature': 'BasicCapabilities',
                         'hpa-feature-attributes': [
                             {
                                 'hpa-attribute-key': 'numVirtualCpu',
                                 'hpa-attribute-value': '4',
                                 'operator': '='
                             },
                             {
                                 'hpa-attribute-key': 'virtualMemSize',
                                 'hpa-attribute-value': '4',
                                 'operator': '=',
                                 'unit': 'GB'
                             }
                         ],
                         'hpa-version': 'v1'}],
                    'id': 'vg_0',
                    'type': 'vnfc',
                    'directives': [
                        {
                            'type': 'flavor_directives',
                            'attributes': [
                                {
                                    'attribute_name': 'label_0',
                                    'attribute_value': ''
                                }
                            ]
                        }
                    ]
                }]},
                'type': 'hpa'
            }
        }

        self.assertEquals(self.Translator.parse_constraints(hpa_constraint),
                          rtn)

        hpa_constraint_2 = {
            "hpa_constraint": {
                "type": "hpa",
                "demands": [
                    "vG"
                ],
                "properties": {
                    "evaluate": [
                        {'id': 'vg_0',
                         'type': 'vnfc',
                         'directives': [
                            {
                                'type': 'flavor_directives',
                                'attributes': [
                                    {
                                        'attribute_name': 'label_0',
                                        'attribute_value': ''
                                    }
                                ]
                            }
                         ],
                         'flavorProperties': [{
                             'hpa-feature': 'BasicCapabilities',
                             'hpa-version': 'v1',
                             'architecture': 'generic',
                             'mandatory': 'True',
                             'directives': [],
                             'hpa-feature-attributes': [
                                 {
                                     'hpa-attribute-key': 'numVirtualCpu',
                                     'hpa-attribute-value': '4',
                                     'operator': '='
                                 },
                                 {
                                     'hpa-attribute-key': 'virtualMemSize',
                                     'hpa-attribute-value': '4',
                                     'operator': '=',
                                     'unit': 'GB'
                                 }
                             ]
                         }], }
                    ]
                }}}
        rtn_2 = {
            'hpa_constraint_vG': {
                'demands': 'vG',
                'name': 'hpa_constraint',
                'properties': {'evaluate': [{
                    'flavorProperties': [
                        {'architecture': 'generic',
                         'mandatory': 'True',
                         'directives': [],
                         'hpa-feature': 'BasicCapabilities',
                         'hpa-feature-attributes': [
                             {
                                 'hpa-attribute-key': 'numVirtualCpu',
                                 'hpa-attribute-value': '4',
                                 'operator': '='
                             },
                             {
                                 'hpa-attribute-key': 'virtualMemSize',
                                 'hpa-attribute-value': '4',
                                 'operator': '=',
                                 'unit': 'GB'
                             }
                         ],
                         'hpa-version': 'v1'}],
                    'id': 'vg_0',
                    'type': 'vnfc',
                    'directives': [
                        {
                            'type': 'flavor_directives',
                            'attributes': [
                                {
                                    'attribute_name': 'label_0',
                                    'attribute_value': ''
                                }
                            ]
                        }
                    ]}]},
                'type': 'hpa'
            }
        }

        self.assertEquals(self.Translator.parse_constraints(hpa_constraint_2),
                          rtn_2)

    def test_parse_hpa_constraints_format_validation(self):
        hpa_constraint_1 = {
            "hpa_constraint": {
                "type": "hpa",
                "demands": [
                    "vG"
                ],
                "properties": {
                    "evaluate": [{'id': 'xx',
                                  'flavorProperties': []}]
                }
            }
        }
        hpa_constraint_2 = {
            "hpa_constraint": {
                "type": "hpa",
                "demands": [
                    "vG"
                ],
                "properties": {
                    "evaluate": [
                        {'id': 'xx',
                         'type': 'xx',
                         'flavorProperties': [
                             {
                                 'hpa-feature': '',
                                 'hpa-version': '',
                                 'architecture': '',
                                 'mandatory': '',
                                 'hpa-feature-attributes': [''],
                             }
                         ]}
                    ]
                }
            }
        }

        hpa_constraint_3 = {
            "hpa_constraint": {
                "type": "hpa",
                "demands": [
                    "vG"
                ],
                "properties": {
                    "evaluate": [
                        {
                            "id": "xx",
                            "type": 'xx',
                            "directives": [],
                            "flavorProperties": [
                                {
                                    "hpa-feature": "BasicCapabilities",
                                    "hpa-version": "v1",
                                    "architecture": "generic",
                                    "mandatory": "False",
                                    "score": "5",
                                    "hpa-feature-attributes": [
                                        {
                                            "hpa-attribute-key": "numVirtualCpu",
                                            "hpa-attribute-value": "4"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        }

        hpa_constraint_4 = {
            "hpa_constraint": {
                "type": "hpa",
                "demands": [
                    "vG"
                ],
                "properties": {
                    "evaluate": [{'id': 'xx',
                                  "type": 'xx',
                                  "directives": [],
                                  'flavorProperties': [{
                                      'hpa-feature': '',
                                      'architecture': '',
                                      'mandatory': '',
                                      'hpa-feature-attributes': [''],
                                  }]}]
                }
            }
        }

        hpa_constraint_5 = {
            "hpa_constraint": {
                "type": "hpa",
                "demands": [
                    "vG"
                ],
                "properties": {
                    "evaluate": [
                        {'flavorLabel': 'xx',
                         'flavorProperties': [
                             {
                                 'hpa-feature': 'BasicCapabilities',
                                 'hpa-version': 'v1',
                                 'architecture': 'generic',
                                 'mandatory': 'False',
                                 'hpa-feature-attributes': [
                                     {
                                         'hpa-attribute-key': 'numVirtualCpu',
                                         'hpa-attribute-value': '4',

                                     },
                                 ]
                             }
                         ], }
                    ]
                }
            }
        }

        self.assertRaises(TranslatorException,
                          self.Translator.parse_constraints, hpa_constraint_1)
        self.assertRaises(TranslatorException,
                          self.Translator.parse_constraints, hpa_constraint_2)
        self.assertRaises(TranslatorException,
                          self.Translator.parse_constraints, hpa_constraint_3)
        self.assertRaises(TranslatorException,
                          self.Translator.parse_constraints, hpa_constraint_4)
        self.assertRaises(TranslatorException,
                          self.Translator.parse_constraints, hpa_constraint_5)

    def test_parse_vim_fit_constraint(self):
        vim_fit_constraint = {
            "check_cloud_capacity": {
                "type": "vim_fit",
                "demands": [
                    "vG"
                ],
                "properties": {
                    "controller": "multicloud",
                    "request": {
                        "vCPU": 10,
                        "Memory": {
                            "quantity": "10",
                            "unit": "GB"
                        },
                        "Storage": {
                            "quantity": "100",
                            "unit": "GB"
                        }
                    }
                }
            }
        }
        expected_response = {
            "check_cloud_capacity_vG" : {
                "type": "vim_fit",
                "demands": "vG",
                "name": "check_cloud_capacity",
                "properties": {
                    "controller": "multicloud",
                    "request": {
                        "vCPU": 10,
                        "Memory": {
                            "quantity": "10",
                            "unit": "GB"
                        },
                        "Storage": {
                            "quantity": "100",
                            "unit": "GB"
                        }
                    }
                }
            }
        }
        vim_fit_constraint2 = {
            "check_cloud_capacity": {
                "type": "vim_fit",
                "demands": [
                    "vG"
                ],
                "properties": {
                    "vim-controller": "multicloud"
                }
            }
        }
        self.maxDiff = None
        self.assertEquals(expected_response, self.Translator.parse_constraints(
            vim_fit_constraint))
        self.assertRaises(TranslatorException,
                          self.Translator.parse_constraints,
                          vim_fit_constraint2)

    @patch('conductor.controller.translator.Translator.create_components')
    def test_parse_optimization(self, mock_create):
        expected_parse = {'goal': 'min',
                          'operands': [{'function': 'distance_between',
                                        'function_param': ['customer_loc', 'vGMuxInfra'],
                                        'operation': 'product',
                                        'weight': 1.0},
                                       {'function': 'distance_between',
                                        'function_param': ['customer_loc', 'vG'],
                                        'operation': 'product',
                                        'weight': 1.0}],
                          'operation': 'sum'
                          }

        opt = {'minimize': {
            'sum': [{'distance_between': ['customer_loc', 'vGMuxInfra']},
                    {'product': [{'distance_between': ['customer_loc', 'vG']},
                                 {'aic_version': ['']},
                                 {'sum':
                                      [{'product':
                                            [{'distance_between':
                                                  ['customer_loc', 'vG']}]
                                        }]},
                                 ]
                     }

                    ]}}
        self.Translator._demands = {'vG': '',
                                    'vGMuxInfra': '',
                                    'customer_loc': ''}
        self.Translator._locations = {'vG': '',
                                      'vGMuxInfra': '',
                                      'customer_loc': ''}
        self.assertEquals(
            self.Translator.parse_optimization(
                opt), expected_parse)

    @patch('conductor.controller.translator.Translator.create_components')
    def test_parse_optimization_multi_objective(self, mock_create):
        hpa_json_file = './conductor/tests/unit/controller/hpa_constraints.json'
        hpa_json = yaml.safe_load(open(hpa_json_file).read())
        expected_parse = {'goal': 'min',
                          'operands': [{'function': 'distance_between',
                                        'function_param': ['customer_loc',
                                                           'vGMuxInfra'],
                                        'operation': 'product',
                                        'weight': 2.0},
                                       {'function': 'distance_between',
                                        'function_param': ['customer_loc',
                                                           'vG'],
                                        'operation': 'product',
                                        'weight': 4.0},
                                       {'function': 'hpa_score',
                                        'function_param': ['vG'],
                                        'operation': 'product',
                                        'weight': 8.0},
                                       ],
                          'operation': 'sum'
                          }

        opt = {'minimize': {
            'sum': [{'product': [2.0, {'distance_between': ['customer_loc', 'vGMuxInfra']}]},
                    {'product': [4.0, {'distance_between': ['customer_loc', 'vG']}]},
                    {'product': [8.0, {'hpa_score': ['vG']}]}
                    ]}}
        self.Translator._demands = {'vG': '',
                                    'vGMuxInfra': '',
                                    'customer_loc': ''}
        self.Translator._locations = {'vG': '',
                                      'vGMuxInfra': '',
                                      'customer_loc': ''}
        self.Translator._constraints = hpa_json["HAS_Template"]["constraints"]
        self.maxDiff = None
        self.assertEquals(
            self.Translator.parse_optimization(
                opt), expected_parse)

        # No HPA Policy test
        non_hpa_dict = dict(hpa_json["HAS_Template"]["constraints"])
        non_hpa_dict.pop("hpa_constraint_vG")
        self.Translator._constraints = non_hpa_dict
        self.maxDiff = None
        self.assertRaises(TranslatorException,
                          self.Translator.parse_optimization, opt)

        # HPA Policy Exists but not for the demand in objective function
        hpa_wrong_demand_dict = dict(hpa_json["HAS_Template"]["constraints"])
        hpa_wrong_demand_dict["hpa_constraint_vG"]["demands"] = ["vGMuxInfra"]
        self.Translator._constraints = hpa_wrong_demand_dict
        self.maxDiff = None
        self.assertRaises(TranslatorException,
                          self.Translator.parse_optimization, opt)

    @patch('conductor.controller.translator.Translator.create_components')
    def test_parse_reservation(self, mock_create):
        expected_resv = {
            'counter': 0,
            'demands': {
                'instance_vG': {
                    'demands': 'vG',
                    'name': 'instance',
                    'properties': {}
                }
            },
            'service_model': 'null'
        }
        self.Translator._demands = {'vG': 'null'}
        resv = {
            'service_model': 'null',
            'service_candidates': {
                'instance': {
                    'demands': {
                        'vG': 'null'
                    }
                }
            }
        }
        self.assertEquals(
            self.Translator.parse_reservations(resv), expected_resv)

    @patch('conductor.controller.translator.Translator.parse_constraints')
    @patch('conductor.controller.translator.Translator.parse_reservations')
    @patch('conductor.controller.translator.Translator.parse_demands')
    @patch('conductor.controller.translator.Translator.parse_optimization')
    @patch('conductor.controller.translator.Translator.parse_locations')
    def test_do_translation(self, mock_loc, mock_opt,
                            mock_dmd, mock_resv, mock_cons):
        expected_format = {
            "conductor_solver": {
                "version": '',
                "plan_id": '',
                "locations": {},
                "request_type": '',
                "demands": {},
                "constraints": {},
                "objective": {},
                "reservations": {},
            }
        }
        self.Translator._valid = True
        self.Translator._version = ''
        self.Translator._plan_id = ''
        self.Translator._parameters = {}
        self.Translator._locations = {}
        self.Translator._demands = {}
        self.Translator._constraints = {}
        self.Translator._optmization = {}
        self.Translator._reservations = {}
        mock_loc.return_value = {}
        mock_resv.return_value = {}
        mock_dmd.return_value = {}
        mock_opt.return_value = {}
        mock_cons.return_value = {}
        self.Translator.do_translation()
        self.assertEquals(self.Translator._translation, expected_format)

    @patch('conductor.controller.translator.Translator.create_components')
    @patch('conductor.controller.translator.Translator.validate_components')
    @patch('conductor.controller.translator.Translator.do_translation')
    @patch('conductor.controller.translator.Translator.parse_parameters')
    def test_translate(self, mock_parse, mock_do_trans,
                       mock_valid, mock_create):
        self.Translator.translate()
        self.assertEquals(self.Translator._ok, True)

    def tearDown(self):
        patch.stopall()


if __name__ == '__main__':
    unittest.main()
