#
# -------------------------------------------------------------------------
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
from jsonschema import validate
from jsonschema import ValidationError
from oslo_log import log

from conductor.controller.translator import Translator
from conductor.controller.translator_utils import OPTIMIZATION_FUNCTIONS
from conductor.controller.translator_utils import TranslatorException

LOG = log.getLogger(__name__)


class GenericObjectiveTranslator(Translator):

    def __init__(self, conf, plan_name, plan_id, template, opt_schema):
        super(GenericObjectiveTranslator, self).__init__(conf, plan_name, plan_id, template)
        self.translator_version = 'GENERIC'
        self.opt_schema = opt_schema

    def parse_optimization(self, optimization):

        if not optimization:
            LOG.debug('No optimization object is provided '
                      'in the template')
            return

        self.validate(optimization)
        parsed = copy.deepcopy(optimization)
        self.parse_functions(parsed.get('operation_function'))
        return parsed

    def validate(self, optimization):
        try:
            validate(instance=optimization, schema=self.opt_schema)
        except ValidationError as ve:
            LOG.error('Optimization object is not valid')
            raise TranslatorException('Optimization object is not valid. '
                                      'Validation error: {}'.format(ve.message))

    def parse_functions(self, operation_function):
        operands = operation_function.get("operands")
        for operand in operands:
            if 'function' in operand:
                function = operand.get('function')
                params = operand.get('params')
                parsed_params = {}
                for keyword in OPTIMIZATION_FUNCTIONS.get(function):
                    if keyword in params:
                        value = params.get(keyword)
                        if keyword == "demand" and value not in list(self._demands.keys()):
                            raise TranslatorException('{} is not a valid demand name'.format(value))
                        parsed_params[keyword] = value
                    else:
                        raise TranslatorException('The function {} expect the param {},'
                                                  'but not found'.format(function, keyword))
                operand['params'] = parsed_params
            elif 'operation_function' in operand:
                self.parse_functions(operand.get('operation_function'))
