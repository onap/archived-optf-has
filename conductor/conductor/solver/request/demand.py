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


class Demand(object):

    def __init__(self, _name=None):
        self.name = _name

        # initial candidates (regions or services) for this demand
        # key = region_id (or service_id),
        # value = region (or service) instance
        self.resources = {}

        # applicable constraint checkers
        # a list of constraint instances to be applied
        self.constraint_list = []

        # to sort demands in the optimization process
        self.sort_base = -1


class Location(object):

    def __init__(self, _name=None):
        self.name = _name
        # clli, coordinates, or placemark
        self.loc_type = None

        # depending on type
        self.value = None

        # customer location country
        self.country = None