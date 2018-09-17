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

import json

import yaml


def load_config_file(config_file, child_name="dockerConfiguration"):
    """
    Load YAML/JSON configuration from a file
    :param config_file:  path to config file (.yaml or .json).
    :param child_name: if present, return only that child node
    :return: config (all or specific child node)
    """
    with open(config_file, 'r') as fid:
        res = {}
        if config_file.endswith(".yaml"):
            res = yaml.load(fid)
        elif config_file.endswith(".json") or config_file.endswith("json"):
            res = json.load(fid)
    return res.get(child_name, res) if child_name else res
