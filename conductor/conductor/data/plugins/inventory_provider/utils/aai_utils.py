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

QUERY_PARAMS = {'service_instance': ["service-instance-id", "service-instance-name", "environment-context",
                                     "workload-context", "model-invariant-id", "model-version-id", "widget-model-id",
                                     "widget-model-version", "service-instance-location-id", "orchestration-status"],
                'nst': ["model-role"]
                }


def convert_hyphen_to_under_score(hyphened_dict):
    converted_dict = dict()
    if hyphened_dict:
        for key in hyphened_dict:
            if '-' in key:
                converted_dict[key.replace('-', '_').lower()] = hyphened_dict[key]
            else:
                converted_dict[key] = hyphened_dict[key]
        if 'resource_version' in converted_dict:
            converted_dict.pop('resource_version')
    return converted_dict


def add_query_params(filtering_attributes):
    if not filtering_attributes:
        return ''
    url = '?'
    for key, value in filtering_attributes.items():
        url = f'{url}{key}={value}&'
    return url


def add_query_params_and_depth(filtering_attributes, depth):
    url_with_query_params = add_query_params(filtering_attributes)
    if url_with_query_params:
        return f"{url_with_query_params}depth={depth}"
    else:
        return f"?depth={depth}"


def get_first_level_and_second_level_filter(filtering_attributes, aai_node):
    second_level_filters = dict()
    valid_query_params = QUERY_PARAMS.get(aai_node)
    for key in list(filtering_attributes):
        if key not in valid_query_params:
            second_level_filters[key] = filtering_attributes[key]
            del filtering_attributes[key]
    return second_level_filters


def get_inv_values_for_second_level_filter(second_level_filters, nssi_instance):
    if not second_level_filters:
        return None
    inventory_attributes = dict()
    for key in list(second_level_filters):
        inventory_attributes[key] = nssi_instance.get(key)
    return inventory_attributes


def get_instance_info(nxi_instance):
    nxi_dict = dict()
    nxi_dict['instance_id'] = nxi_instance.get('service-instance-id')
    nxi_dict['instance_name'] = nxi_instance.get('service-instance-name')
    if nxi_instance.get('workload-context'):
        nxi_dict['domain'] = nxi_instance.get('workload-context')
    return nxi_dict


def get_nst_info(nst_instance):
    nst_dict = {}
    nst_dict['model_invariant_id'] = nst_instance.get('model-invariant-id')
    nst_dict['model_type'] = nst_instance.get('model-type')
    nst_dict['model_role'] = nst_instance.get('model-role')
    return nst_dict


def get_model_ver_info(model_version):
    for key in list(model_version):
        if "model-elements" in key:
            del model_version["model-elements"]
    return model_version


def get_profiles(profile_instances, profile_type):
    profile_type_plural = profile_type + 's'
    return [x[profile_type_plural][profile_type][0] for x in profile_instances if x.get(profile_type_plural)]
