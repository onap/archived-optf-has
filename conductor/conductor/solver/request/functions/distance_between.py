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

from conductor.solver.utils import utils


class DistanceBetween(object):

    def __init__(self, _type):
        self.func_type = _type

        self.loc_a = None
        self.loc_z = None

    def compute(self, _loc_a, _loc_z):
        distance = utils.compute_air_distance(_loc_a, _loc_z)

        return distance

    def get_args_from_params(self, decision_path, request, params):
        demand = params.get('demand')
        location = params.get('location')

        resource = decision_path.decisions[demand]
        loc_a = request.cei.get_candidate_location(resource)
        loc_z = request.location.get(location)

        return loc_a, loc_z
