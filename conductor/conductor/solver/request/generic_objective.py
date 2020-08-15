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

from conductor.solver.request import functions
from conductor.solver.utils.utils import OPERATOR_FUNCTIONS

GOALS = {'minimize': 'min',
         'maximize': 'max'}


def get_method_class(function_name):
    module_name = getattr(functions, function_name)
    return getattr(module_name, dir(module_name)[0])


def get_normalized_value(value, start, end):
    return (value - start) / (end - start)


class GenericObjective(object):

    def __init__(self, objective_function):
        self.goal = GOALS[objective_function.get('goal')]
        self.operation_function = objective_function.get('operation_function')
        self.operand_list = []    # keeping this for compatibility with the solver

    def compute(self, _decision_path, _request):
        value = self.compute_operation_function(self.operation_function, _decision_path, _request)
        _decision_path.cumulated_value = value
        _decision_path.total_value = \
            _decision_path.cumulated_value + \
            _decision_path.heuristic_to_go_value

    def compute_operation_function(self, operation_function, _decision_path, _request):
        operator = operation_function.get('operator')
        operands = operation_function.get('operands')

        result_list = []

        for operand in operands:
            if 'operation_function' in operand:
                value = self.compute_operation_function(operand.get('operation_function'),
                                                        _decision_path, _request)
            else:
                function_name = operand.get('function')
                function_class = get_method_class(function_name)
                function = function_class(function_name)
                args = function.get_args_from_params(_decision_path, _request,
                                                     operand.get('params'))
                value = function.compute(*args)

            if 'normalization' in operand:
                normalization = operand.get('normalization')
                value = get_normalized_value(value, normalization.get('start'),
                                             normalization.get('end'))

            if 'weight' in operand:
                value = value * operand.get("weight")

            result_list.append(value)

        return OPERATOR_FUNCTIONS.get(operator)(result_list)
