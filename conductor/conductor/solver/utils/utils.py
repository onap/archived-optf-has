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

from functools import reduce
import math
import operator
from oslo_log import log


LOG = log.getLogger(__name__)


OPERATIONS = {'gte': lambda x, y: x >= y,
              'lte': lambda x, y: x <= y,
              'gt': lambda x, y: x > y,
              'lt': lambda x, y: x < y,
              'eq': lambda x, y: x == y
              }                                # TODO(krishna): move to a common place

AGGREGATION_FUNCTIONS = {'sum': lambda x: reduce(operator.add, x),
                         'min': lambda x: reduce(lambda a, b: a if a < b else b, x),
                         'max': lambda x: reduce(lambda a, b: a if a < b else b, x),
                         'avg': lambda x: reduce(operator.add, x) / len(x)}

OPT_OPERATIONS = {'sum': operator.add,
                  'product': operator.mul,
                  'min': lambda a, b: a if a < b else b,
                  'max': lambda a, b: a if a > b else b}


def compute_air_distance(_src, _dst):
    """Compute Air Distance

    based on latitude and longitude
    input: a pair of (lat, lon)s
    output: air distance as km
    """
    distance = 0.0
    latency_score = 0.0

    if _src == _dst:
        return distance

    radius = 6371.0  # km


    dlat = math.radians(_dst[0] - _src[0])
    dlon = math.radians(_dst[1] - _src[1])
    a = math.sin(dlat / 2.0) * math.sin(dlat / 2.0) + \
        math.cos(math.radians(_src[0])) * \
        math.cos(math.radians(_dst[0])) * \
        math.sin(dlon / 2.0) * math.sin(dlon / 2.0)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    distance = radius * c

    return distance


def compute_latency_score(_src,_dst, _region_group):
    """Compute the Network latency score between src and dst"""
    earth_half_circumference = 20000
    region_group_weight = _region_group.get(_dst[2])

    if region_group_weight == 0 or region_group_weight is None :
        LOG.debug("Computing the latency score based on distance between : ")
        latency_score = compute_air_distance(_src,_dst)
    elif _region_group > 0 :
        LOG.debug("Computing the latency score ")
        latency_score = compute_air_distance(_src, _dst) + region_group_weight * earth_half_circumference
    LOG.debug("Finished Computing the latency score: "+str(latency_score))
    return latency_score


def convert_km_to_miles(_km):
    return _km * 0.621371


def convert_miles_to_km(_miles):
    return _miles / 0.621371
