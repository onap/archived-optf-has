#!/usr/bin/env python
#
# -------------------------------------------------------------------------
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

'''Utility functions for 
   Hardware Platform Awareness (HPA) constraint plugin'''

# python imports
import yaml
import operator

from conductor.i18n import _LE, _LI
# Third-party library imports
from oslo_log import log

LOG = log.getLogger(__name__)


class HpaMatchProvider(object):

    def __init__(self):
        pass

    def _is_cap_supported(self, flavor, cap):
        try:
            for elem in cap:
                flavor.remove(elem)
        except ValueError:
            return False
        # Found all capabilities in Flavor
        return True

        # Convert to bytes value using unit

    def _get_normalized_value(self, unit, value):

        if not value.isdigit():
            return value
        value = int(value)
        if unit == 'KB':
            value = value * 1024
        elif unit == 'MB':
            value = value * 1024 * 1024
        elif unit == 'GB':
            value = value * 1024 * 1024 * 1024
        return str(value)

    def _get_req_attribute(self, req_attr):

        c_op = req_attr['operator']
        c_value = req_attr['hpa-attribute-value']
        c_unit = None
        if 'unit' in req_attr:
            c_unit = req_attr['unit']

        if c_unit:
            c_value = self._get_normalized_value(c_unit, c_value)
        return c_value, c_op

    def _get_flavor_attribute(self, flavor_attr):
        attrib_value = yaml.load(flavor_attr['hpa-attribute-value'])
        f_unit = None
        for key, value in attrib_value.iteritems():
            if key == 'value':
                f_value = value
            elif key == 'unit':
                f_unit = value
        if f_unit:
            f_value = self._get_normalized_value(f_unit, f_value)
        return f_value

    def _get_operator(self, req_op):

        OPERATORS = ['=', '<', '>', '<=', '>=', 'ALL']

        if not req_op in OPERATORS:
            return None

        if req_op == ">":
            op = operator.gt
        elif req_op == ">=":
            op = operator.ge
        elif req_op == "<":
            op = operator.lt
        elif req_op == "<=":
            op = operator.le
        elif req_op == "=":
            op = operator.eq
        elif req_op == 'ALL':
            op = 'ALL'

        return op

    def _compare_attribute(self, flavor_attr, req_attr):

        req_value, req_op = self._get_req_attribute(req_attr)
        flavor_value = self._get_flavor_attribute(flavor_attr)

        # Compare operators only valid for Integers
        if req_op in ['<', '>', '<=', '>=']:
            if not c_value.isdigit() or not f_value.isdigit():
                return False

        op = self._get_operator(req_op)
        if not op:
            return False

        if req_op == 'ALL':
            return _match_all_operator(flavor_attr['hpa-attribute-value'], req_attr['hpa-attribute-value'])

        # if values are string compare them as strings
        if req_op == '=':
            if not req_value.isdigit() or not flavor_value.isdigit():
                if op(req_value, flavor_value):
                    return True
                else:
                    return False

                    # Only integers left to compare
        if req_op in ['<', '>', '<=', '>=', '=']:
            if op(int(req_value), int(flavor_value)):
                return True
            else:
                return False

        return False

        # for the feature get the capabilty feature attribute list

    def _get_flavor_cfa_list(self, feature, flavor_cap_list):
        for capability in CapabilityDataParser.get_item(flavor_cap_list, 'hpa-capability'):
            flavor_feature, feature_attributes = capability.get_fields()
            # One feature will match this condition as we have pre-filtered 
            if feature == flavor_feature:
                return feature_attributes

                # flavor has all the required capabilties

    # For each required capability find capability in flavor
    # and compare each attribute
    def _compare_feature_attributes(self, req_cap_list, flavor_cap_list):
        for capability in CapabilityDataParser.get_item(req_cap_list, 'features'):
            hpa_feature, req_cfa_list = capability.get_fields()
            flavor_cfa_list = self._get_flavor_cfa_list(hpa_feature, flavor_cap_list)
            for req_feature_attr in req_cfa_list:
                req_attr_key = req_feature_attr['hpa-attribute-key']
                # filter to get the attribute being compared
                flavor_feature_attr = \
                    filter(lambda ele: ele['hpa-attribute-key'] == req_attr_key, flavor_cfa_list)
                if not self._compare_attribute(flavor_feature_attr[0], req_feature_attr):
                    LOG.debug('Failed attritube match ( "{}" "{}").'.format(
                        flavor_feature_attr[0], req_feature_attr))
                    return False
        return True

        # Find the flavor which has all the required capabilities

    def match_flavor(self, candidate, req_cap_list):
        flavors_list = candidate['flavors']
        # Keys to find capability match
        hpa_keys = ['hpa-feature', 'architecture', 'hpa-version']
        req_filter_list = []
        for capability in CapabilityDataParser.get_item(req_cap_list, 'features'):
            hpa_list = {k: capability.item[k] for k in hpa_keys if k in capability.item}
            req_filter_list.append(hpa_list)

        for flavor in flavors_list['flavor']:
            flavor_filter_list = []
            flavor_cap_list = flavor['hpa-capabilities']
            for capability in CapabilityDataParser.get_item(flavor_cap_list, 'hpa-capability'):
                hpa_list = {k: capability.item[k] for k in hpa_keys if k in capability.item}
                flavor_filter_list.append(hpa_list)
            # if flavor has the matching capability compare attributes
            if self._is_cap_supported(flavor_filter_list, req_filter_list):
                if self._compare_feature_attributes(req_cap_list, flavor_cap_list):
                    LOG.info(_LI("Matching Flavor found '{}' for request - {}").
                             format(flavor['flavor-name'], req_cap_list))
                    return flavor['flavor-name']
                else:
                    LOG.info(_LI("Matching Flavor not found for request - {}").
                             format(req_cap_list))
                    return None


class CapabilityDataParser(object):
    """Helper class to parse  data"""

    def __init__(self, item):
        self.item = item

    @classmethod
    def get_item(cls, payload, key):
        try:
            features = (payload[key])
            for f in features:
                yield cls(f)
        except KeyError:
            LOG.info(_LI("invalid JSON "))

    def get_fields(self):
        return (self.get_feature(),
                self.get_feature_attributes())

    def get_feature_attributes(self):
        return self.item.get('hpa-feature-attributes')

    def get_feature(self):
        return self.item.get('hpa-feature')
