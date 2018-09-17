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

"""Existing service instance in a region"""


class Service(object):

    def __init__(self, _sid=None):
        self.name = _sid

        self.region = None

        self.status = "active"

        self.cost = 0.0

        """abstracted resource capacity status"""
        self.capacity = {}

        self.allocated_demand_list = []

        """other opaque metadata if necessary"""
        self.properties = {}

        self.last_update = 0

    """update resource capacity after allocating demand"""
    def update_capacity(self):
        pass

    """for logging"""
    def get_json_summary(self):
        pass
