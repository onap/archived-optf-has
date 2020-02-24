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

import itertools

import six


class ThresholdException(Exception):
    pass


def is_number(input):
    """Returns True if the value is a number"""
    try:
        if type(input) is int or type(input) is float:
            return True
        elif isinstance(input, six.string_types) and float(input):
            return True
    except ValueError:
        pass
    return False


class Threshold(object):
    OPERATORS = ['=', '<', '>', '<=', '>=']
    UNITS = {
        'currency': {
            'USD': 1.0,
        },
        'time': {
            'ms': 1.0,
            'sec': 1000.0,
        },
        'distance': {
            'km': 1.0,
            'mi': 1.609344,
        },
        'throughput': {
            'Kbps': 0.001,
            'Mbps': 1.0,
            'Gbps': 1000.0,
        },
    }

    def __init__(self, expression, base_unit):
        if not isinstance(expression, six.string_types):
            raise ThresholdException("Expression must be a string")
        if not isinstance(base_unit, six.string_types):
            raise ThresholdException("Base unit must be a string")
        if base_unit not in self.UNITS:
            raise ThresholdException(
                "Base unit {} unsupported, must be one of: {}".format(
                    base_unit, ', '.join(list(self.UNITS.keys()))))

        self._expression = expression
        self._base_unit = base_unit
        self._parse()

    def __repr__(self):
        """Object representation"""
        return "<Threshold expression: '{}', base_unit: '{}', " \
               "parts: {}>".format(self.expression, self.base_unit, self.parts)

    def _all_units(self):
        """Returns a single list of all supported units"""
        unit_lists = [list(self.UNITS[k].keys()) for k in list(self.UNITS.keys())]
        return list(itertools.chain.from_iterable(unit_lists))

    def _default_for_base_unit(self, base_unit):
        """Returns the default unit (1.0 multiplier) for a given base unit

        Returns None if not found.
        """
        units = self.UNITS.get(base_unit)
        if units:
            for name, multiplier in units.items():
                if multiplier == 1.0:
                    return name
        return None

    def _multiplier_for_unit(self, unit):
        """Returns the multiplier for a given unit

        Returns None if not found.
        """
        return self.UNITS.get(self.base_unit).get(unit)

    def _reset(self):
        """Resets parsed components"""
        self._operator = None
        self._value = None
        self._min_value = None
        self._max_value = None
        self._unit = None
        self._parsed = False

    def _parse(self):
        """Parses the expression into parts"""
        self._reset()
        parts = self.expression.split()
        for part in parts:
            # Is it an operator?
            if not self.operator and part in self.OPERATORS:
                if self.value:
                    raise ThresholdException(
                        "Value {} encountered before operator {} "
                        "in expression '{}'".format(
                            self.value, part, self.expression))
                if self.has_range:
                    raise ThresholdException(
                        "Range {}-{} encountered before operator {} "
                        "in expression '{}'".format(
                            self.min_value, self.max_value,
                            part, self.expression))
                if self.unit:
                    raise ThresholdException(
                        "Unit '{}' encountered before operator {} "
                        "in expression '{}'".format(
                            self.unit, part, self.expression))

                self._operator = part

            # Is it a lone value?
            elif not self.value and is_number(part):
                if self.has_range:
                    raise ThresholdException(
                        "Range {}-{} encountered before value {} "
                        "in expression '{}'".format(
                            self.min_value, self.max_value,
                            part, self.expression))
                if self.unit:
                    raise ThresholdException(
                        "Unit '{}' encountered before value {} "
                        "in expression '{}'".format(
                            self.unit, part, self.expression))
                self._value = float(part)
                if not self.operator:
                    self._operator = '='

            # Is it a value range?
            elif not self.has_range and part.count('-') == 1:
                part1, part2 = part.split('-')
                if is_number(part1) and is_number(part2):
                    if self.operator and self.operator != '=':
                        raise ThresholdException(
                            "Operator {} not supported with range {} "
                            "in expression '{}'".format(
                                self.operator, part, self.expression))
                    if self.value:
                        raise ThresholdException(
                            "Value {} encountered before range {} "
                            "in expression '{}'".format(
                                self.value, part, self.expression))
                    if self.unit:
                        raise ThresholdException(
                            "Unit '{}' encountered before range {} "
                            "in expression '{}'".format(
                                self.unit, part, self.expression))
                    self._min_value = min(float(part1), float(part2))
                    self._max_value = max(float(part1), float(part2))
                    if not self.operator:
                        self._operator = '='

            # Is it a unit?
            elif part in self._all_units():
                if not self.value and not self.has_range:
                    if not self.value:
                        raise ThresholdException(
                            "Value {} encountered before unit {} "
                            "in expression '{}'".format(
                                self.value, part, self.expression))
                    else:
                        raise ThresholdException(
                            "Range {}-{} encountered before unit {} "
                            "in expression '{}'".format(
                                self.min_value, self.max_value,
                                part, self.expression))
                self._unit = part

            # Well then, we don't know.
            else:
                raise ThresholdException(
                    "Unknown part '{}' in expression '{}'".format(
                        part, self._expression))

        if not self.has_range and not self._value:
            raise ThresholdException(
                "Value/range missing in expression '{}'".format(
                    self._expression))

        if self._unit:
            # Convert from stated units to default.
            multiplier = self._multiplier_for_unit(self._unit)
            if self.value:
                self._value = self._value * multiplier
            if self.has_range:
                self._min_value = self._min_value * multiplier
                self._max_value = self._max_value * multiplier

        # Always use the default unit.
        self._unit = self._default_for_base_unit(self._base_unit)

        self._parsed = True

    @property
    def base_unit(self):
        """Returns the original base unit"""
        return self._base_unit

    @property
    def expression(self):
        """Returns the original expression"""
        return self._expression

    @property
    def has_range(self):
        """Returns True if a minimum/maximum value range exists"""
        return self.min_value and self.max_value

    @property
    def max_value(self):
        """Returns the detected maximum value, if any"""
        return self._max_value

    @property
    def min_value(self):
        """Returns the detected minimum value, if any"""
        return self._min_value

    @property
    def operator(self):
        """Returns the operator"""
        return self._operator

    @property
    def parsed(self):
        """Returns True if the expression was successfully parsed"""
        return self._parsed

    @property
    def parts(self):
        """Returns the expression as a dictionary of parts"""
        result = {}
        if self.parsed:
            result['operator'] = self.operator
            if self.has_range:
                result['value'] = {
                    'min': self.min_value,
                    'max': self.max_value,
                }
            else:
                result['value'] = self.value
            result['units'] = self.unit
        return result

    @property
    def unit(self):
        """Returns the units"""
        return self._unit

    @property
    def value(self):
        """Returns the detected value, if any"""
        return self._value
