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


"""Cloud region"""


class Region(object):

    def __init__(self, _rid=None):
        self.name = _rid

        self.status = "active"

        '''general region properties'''
        # S (i.e., medium_lite), M (i.e., medium), or L (i.e., large)
        self.region_type = None
        # (latitude, longitude)
        self.location = None

        '''
        placemark:

        country_code (e.g., US),
        postal_code (e.g., 07920),
        administrative_area (e.g., NJ),
        sub_administrative_area (e.g., Somerset),
        locality (e.g., Bedminster),
        thoroughfare (e.g., AT&T Way),
        sub_thoroughfare (e.g., 1)
        '''
        self.address = {}

        self.zones = {}  # Zone instances (e.g., disaster and/or update)
        self.cost = 0.0

        '''abstracted resource capacity status'''
        self.capacity = {}

        self.allocated_demand_list = []

        '''other opaque metadata such as cloud_version, sriov, etc.'''
        self.properties = {}

        '''known neighbor regions to be used for constraint solving'''
        self.neighbor_list = []  # a list of Link instances

        self.last_update = 0

    '''update resource capacity after allocating demand'''

    def update_capacity(self):
        pass

    '''for logging'''

    def get_json_summary(self):
        pass


class Zone(object):

    def __init__(self, _zid=None):
        self.name = _zid
        self.zone_type = None  # disaster or update

        self.region_list = []  # a list of region names

    def get_json_summary(self):
        pass


class Link(object):

    def __init__(self, _region_name):
        self.destination_region_name = _region_name

        self.distance = 0.0
        self.nw_distance = 0.0
        self.latency = 0.0
        self.bandwidth = 0.0

    def get_json_summary(self):
        pass
