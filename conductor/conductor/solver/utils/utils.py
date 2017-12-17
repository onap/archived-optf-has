#!/usr/bin/env python
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


import math


def compute_air_distance(_src, _dst):
    """Compute Air Distance

    based on latitude and longitude
    input: a pair of (lat, lon)s
    output: air distance as km
    """
    distance = 0.0

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


def convert_km_to_miles(_km):
    return _km * 0.621371


def convert_miles_to_km(_miles):
    return _miles / 0.621371
