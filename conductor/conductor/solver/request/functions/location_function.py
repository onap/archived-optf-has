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


class LocationFunction(object):
    """Super class for functions that applies on locations."""

    def __init__(self):
        pass

    def get_args_from_params(self, decision_path, request, params):
        demand = params.get('demand')
        location = params.get('location')

        resource = decision_path.decisions[demand]
        loc_a = request.cei.get_candidate_location(resource)
        loc_z = request.location.get(location)

        return loc_a, loc_z
