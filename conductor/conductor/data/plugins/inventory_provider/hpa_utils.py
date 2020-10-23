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

"""Utility functions for
   Hardware Platform Awareness (HPA) constraint plugin"""

import operator
import yaml

from oslo_log import log

import conductor.common.prometheus_metrics as PC
from conductor.i18n import _LE
from conductor.i18n import _LI
from conductor.i18n import _LW


LOG = log.getLogger(__name__)


def match_all_operator(big_list, small_list):
    """Match ALL operator for HPA Check if smaller list is a subset of bigger list

    :param big_list: bigger list
    :param small_list: smaller list
    :return: True or False
    """
    if not big_list or not small_list:
        return False

    big_set = set(big_list)
    small_set = set(small_list)

    return small_set.issubset(big_set)


def get_candidates_with_hpa(arg):
    """RPC for getting candidates flavor mapping for matching hpa

    :param ctx: context
    :param arg: contains input passed from client side for RPC call
    :return: response candidate_list with matching label to flavor mapping
    """
    candidate_list = arg["candidate_list"]
    id = arg["id"]
    type = arg["type"]
    directives = arg["directives"]
    attr = directives[0].get("attributes")
    label_name = attr[0].get("attribute_name")
    flavorProperties = arg["flavorProperties"]
    discard_set = set()
    for i in range(len(candidate_list)):
        # perform this check only for cloud candidates
        if candidate_list[i]["inventory_type"] != "cloud":
            continue

        # Check if flavor mapping for current label_name already
        # exists. This is an invalid condition.
        if candidate_list[i].get("directives") and attr[0].get(
                "attribute_value") != "":
            LOG.error(_LE("Flavor mapping for label name {} already"
                          "exists").format(label_name))
            continue

        # RPC call to inventory provider for matching hpa capabilities
        result = match_hpa(candidate=candidate_list[i], features=flavorProperties)

        flavor_name = None
        if result:
            LOG.debug("Find results {}".format(result))
            flavor_info = result.get("flavor_map")
            req_directives = result.get("directives")
            LOG.debug("Get directives {}".format(req_directives))

        else:
            flavor_info = None
            LOG.info(
                _LW("No flavor mapping returned"
                    " for candidate: {}").format(
                    candidate_list[i].get("candidate_id")))

        # Metrics to Prometheus
        m_vim_id = candidate_list[i].get("vim-id")
        if not flavor_info:
            discard_set.add(candidate_list[i].get("candidate_id"))
            PC.HPA_CLOUD_REGION_UNSUCCESSFUL.labels('ONAP', 'N/A',
                                                    m_vim_id).inc()
        else:
            if not flavor_info.get("flavor-name"):
                discard_set.add(candidate_list[i].get("candidate_id"))
                PC.HPA_CLOUD_REGION_UNSUCCESSFUL.labels('ONAP', 'N/A',
                                                        m_vim_id).inc()
            else:
                if not candidate_list[i].get("flavor_map"):
                    candidate_list[i]["flavor_map"] = {}
                # Create flavor mapping for label_name to flavor
                flavor_name = flavor_info.get("flavor-name")
                flavor_id = flavor_info.get("flavor-id")
                candidate_list[i]["flavor_map"][label_name] = flavor_name
                candidate_list[i]["flavor_map"]["flavorId"] = flavor_id
                # Create directives if not exist already
                if not candidate_list[i].get("all_directives"):
                    candidate_list[i]["all_directives"] = {}
                    candidate_list[i]["all_directives"]["directives"] = []
                # Create flavor mapping and merge directives
                merge_directives(candidate_list, i, id, type, directives, req_directives)
                if not candidate_list[i].get("hpa_score"):
                    candidate_list[i]["hpa_score"] = 0
                candidate_list[i]["hpa_score"] += flavor_info.get("score")

                # Metrics to Prometheus
                PC.HPA_CLOUD_REGION_SUCCESSFUL.labels('ONAP', 'N/A',
                                                      m_vim_id).inc()

    # return candidates not in discard set
    candidate_list[:] = [c for c in candidate_list
                         if c['candidate_id'] not in discard_set]
    LOG.info(_LI(
        "Candidates with matching hpa capabilities: {}").format(candidate_list))
    return candidate_list


def merge_directives(candidate_list, index, id, type, directives, feature_directives):
    """Merge the flavor_directives with other diectives listed under hpa capabilities in the policy

    :param candidate_list: all candidates
    :param index: index number
    :param id: vfc name
    :param type: vfc type
    :param directives: directives for each vfc
    :param feature_directives: directives for hpa-features
    :return:
    """
    directive = {"id": id,
                 "type": type,
                 "directives": ""}
    flavor_id_attributes = {"attribute_name": "flavorId", "attribute_value": ""}
    for ele in directives:
        if "flavor_directives" in ele.get("type"):
            flag = True
            if len(ele.get("attributes")) <= 1:
                ele.get("attributes").append(flavor_id_attributes)
            break
        else:
            flag = False
    if not flag:
        LOG.error("No flavor directives found in {}".format(id))
    for item in feature_directives:
        if item and item not in directives:
            directives.append(item)
    directive["directives"] = directives
    candidate_list[index]["all_directives"]["directives"].append(directive)


def match_hpa(candidate, features):
    """Match HPA features requirement with the candidate flavors """
    hpa_provider = HpaMatchProvider(candidate, features)
    if hpa_provider.init_verify():
        directives = hpa_provider.match_flavor()
    else:
        directives = None
    return directives


class HpaMatchProvider(object):

    def __init__(self, candidate, req_cap_list):
        self.flavors_list = None
        if isinstance(candidate.get('flavors'), dict) \
                and candidate.get('flavors').get('flavor'):
            self.flavors_list = candidate.get('flavors').get('flavor')
        self.req_cap_list = req_cap_list
        self.m_vim_id = candidate.get('vim-id')

    # Find out whether there is flavor info inside the candidate
    def init_verify(self):
        if self.flavors_list is not None:
            return True
        else:
            return False

    # Find the flavor which has all the required capabilities
    def match_flavor(self):
        # Keys to find capability match
        hpa_keys = ['hpa-feature', 'architecture', 'hpa-version']
        req_filter_list = []
        for capability in CapabilityDataParser.get_item(self.req_cap_list,
                                                        None):
            if capability.item['mandatory'].lower() == 'true':
                hpa_list = {k: capability.item[k]
                            for k in hpa_keys if k in capability.item}
                if hpa_list not in req_filter_list:
                    req_filter_list.append(hpa_list)
        max_score = -1
        directives = None
        for flavor in self.flavors_list:
            flavor_filter_list = []
            try:
                flavor_cap_list = flavor['hpa-capabilities']
            except KeyError:
                LOG.info(_LI("hpa-capabilities not found in flavor "))
                # Metrics to Prometheus
                m_flavor_name = flavor['flavor-name']
                PC.HPA_FLAVOR_MATCH_UNSUCCESSFUL.labels('ONAP', 'N/A', 'N/A',
                                                        'N/A', self.m_vim_id,
                                                        m_flavor_name).inc()
                continue
            for capability in CapabilityDataParser.get_item(flavor_cap_list,
                                                            'hpa-capability'):
                hpa_list = {k: capability.item[k]
                            for k in hpa_keys if k in capability.item}
                flavor_filter_list.append(hpa_list)
            # if flavor has the matching capability compare attributes
            if self._is_cap_supported(flavor_filter_list, req_filter_list):
                match_found, score, req_directives = self._compare_feature_attributes(flavor_cap_list)
                if match_found:
                    LOG.info(_LI("Matching Flavor found '{}' for request - {}").
                             format(flavor['flavor-name'], self.req_cap_list))
                    # Metrics to Prometheus
                    m_flavor_name = flavor['flavor-name']
                    PC.HPA_FLAVOR_MATCH_SUCCESSFUL.labels('ONAP', 'N/A', 'N/A',
                                                          'N/A', self.m_vim_id,
                                                          m_flavor_name).inc()
                    if score > max_score:
                        max_score = score
                        flavor_map = {"flavor-id": flavor['flavor-id'],
                                      "flavor-name": flavor['flavor-name'],
                                      "score": max_score}
                        directives = {"flavor_map": flavor_map,
                                      "directives": req_directives}
                else:
                    # Metrics to Prometheus
                    m_flavor_name = flavor['flavor-name']
                    PC.HPA_FLAVOR_MATCH_UNSUCCESSFUL.labels('ONAP', 'N/A',
                                                            'N/A', 'N/A',
                                                            self.m_vim_id,
                                                            m_flavor_name).inc()
            else:
                # Metrics to Prometheus
                m_flavor_name = flavor['flavor-name']
                PC.HPA_FLAVOR_MATCH_UNSUCCESSFUL.labels('ONAP', 'N/A',
                                                        'N/A', 'N/A',
                                                        self.m_vim_id,
                                                        m_flavor_name).inc()
        return directives

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
        try:
            c_op = req_attr['operator']
            c_value = req_attr['hpa-attribute-value']
            c_unit = None
            if 'unit' in req_attr:
                c_unit = req_attr['unit']
        except KeyError:
            LOG.info(_LI("invalid JSON "))
            return None

        if c_unit:
            c_value = self._get_normalized_value(c_unit, c_value)
        return c_value, c_op

    def _get_flavor_attribute(self, flavor_attr):
        try:
            attrib_value = yaml.load(flavor_attr['hpa-attribute-value'])
        except Exception:
            return None

        f_unit = None
        f_value = None
        for key, value in attrib_value.items():
            if key == 'value':
                f_value = value
            elif key == 'unit':
                f_unit = value
        if f_unit:
            f_value = self._get_normalized_value(f_unit, f_value)
        return f_value

    def _get_operator(self, req_op):

        operator_list = ['=', '<', '>', '<=', '>=', 'ALL']

        if req_op not in operator_list:
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
            op = match_all_operator

        return op

    def _compare_attribute(self, flavor_attr, req_attr):

        req_value, req_op = self._get_req_attribute(req_attr)
        flavor_value = self._get_flavor_attribute(flavor_attr)

        if req_value is None or flavor_value is None:
            return False

        # Compare operators only valid for Integers
        if req_op in ['<', '>', '<=', '>=']:
            if not req_value.isdigit() or not flavor_value.isdigit():
                return False

        op = self._get_operator(req_op)
        if not op:
            return False

        if req_op == 'ALL':
            # All is valid only for lists
            if isinstance(req_value, list) and isinstance(flavor_value, list):
                return op(flavor_value, req_value)

        # if values are string compare them as strings
        if req_op == '=':
            if not req_value.isdigit() or not flavor_value.isdigit():
                return op(req_value, flavor_value)

        # Only integers left to compare
        if req_op in ['<', '>', '<=', '>=', '=']:
            return op(int(flavor_value), int(req_value))

        return False

    # for the feature get the capabilty feature attribute list
    def _get_flavor_cfa_list(self, feature, flavor_cap_list):
        feature_attr_list = []
        for capability in CapabilityDataParser.get_item(flavor_cap_list,
                                                        'hpa-capability'):
            flavor_feature, feature_attributes = capability.get_fields()
            # Multiple features that match this condition will be filtered
            if feature == flavor_feature:
                feature_attr_list.append(feature_attributes)
        return feature_attr_list

    # flavor has all the required capabilties
    # For each required capability find capability in flavor
    # and compare each attribute
    def _compare_feature_attributes(self, flavor_cap_list):
        score = 0
        directives = []
        for capability in CapabilityDataParser.get_item(self.req_cap_list, None):
            hpa_feature, req_cfa_list = capability.get_fields()
            feature_directive = capability.get_directives()
            if feature_directive:
                feature_directive[:] = [d for d in feature_directive
                                        if d.get("type") != ""]
                for item in feature_directive:
                    directives.append(item)
            flavor_cfa_list = self._get_flavor_cfa_list(hpa_feature, flavor_cap_list)
            req_flag = False
            if flavor_cfa_list is not None:
                for flavor_cfa in flavor_cfa_list:
                    flavor_flag = True
                    for req_feature_attr in req_cfa_list:
                        req_attr_key = req_feature_attr['hpa-attribute-key']
                        # filter to get the attribute being compared
                        flavor_feature_attr = \
                            filter(lambda ele: ele['hpa-attribute-key'] ==
                                   req_attr_key, flavor_cfa)
                        if not flavor_feature_attr:
                            flavor_flag = False
                        elif not self._compare_attribute(list(flavor_feature_attr)[0],
                                                         req_feature_attr):
                            flavor_flag = False
                    if not flavor_flag:
                        continue
                    else:
                        req_flag = True
                        break
            if not req_flag and capability.item['mandatory'].lower() == 'true':
                return False, 0, None
            if req_flag and capability.item['mandatory'].lower() == 'false':
                score = score + int(capability.item['score'])
        return True, score, directives


class CapabilityDataParser(object):
    """Helper class to parse  data"""

    def __init__(self, item):
        self.item = item

    @classmethod
    def get_item(cls, payload, key):
        try:
            if key is None:
                features = payload
            else:
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

    def get_directives(self):
        return self.item.get('directives')
