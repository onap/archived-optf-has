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

# Conductor imports

# Third-party library imports
from oslo_log import log

LOG = log.getLogger(__name__)


def  match_all_operator(big_list, small_list):
    '''
    Match ALL operator for HPA
    Check if smaller list is a subset of bigger list
    :param big_list: bigger list
    :param small_list: smaller list
    :return: True or False
    '''
    if not big_list or not small_list:
        return False

    big_set = set(big_list)
    small_set = set(small_list)

    return small_set.issubset(big_set)
