#
# -------------------------------------------------------------------------
#   Copyright (c) 2015-2018 AT&T Intellectual Property
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

from conductor.solver.utils import utils


class LatencyBetween(object):
    def __init__(self, _type):
        self.func_type = _type

        self.loc_a = None
        self.loc_z = None
        self.region_group = None

    def compute(self, _loc_a, _loc_z):
        latency = utils.compute_latency_score(_loc_a, _loc_z, self.region_group)

        return latency

    def get_args_from_params(self, decision_path, request, params):
        demand = params.get('demand')
        location = params.get('location')

        resource = decision_path.decisions[demand]
        loc_a = request.cei.get_candidate_location(resource)
        loc_z = request.location.get(location)

        return loc_a, loc_z
