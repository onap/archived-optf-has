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

import unittest
import collections
from conductor.solver.request.functions import latency_between



__author__ = "Inam Soomro (inam@research.att.com)"
__email__ = "inam@research.att.com"




class TestLatencyBetween(unittest.TestCase):
    #lb = latency_between.LatencyBetween("latency_between")

    def setUp(self):
        self.lb = latency_between.LatencyBetween("latency_between")
        self.loc_a = None
        self.loc_z = None
        #self.lb.region_group = collections.OrderedDict([('USA', 0),('CAN', 0),('MEX', 0),('DEU', 1),('GBR', 1)])

    def test_compute_latency_between_zero(self):
        lon = 0.0
        lat = 0.0
        loc = 'USA'
        loc_a = (float(lat), float(lon), str(loc))
        loc_z = (float(lat), float(lon), str(loc))
        self.lb.region_group = collections.OrderedDict([('USA', 0), ('CAN', 0), ('MEX', 0), ('DEU', 1), ('GBR', 1)])
        expectedoutput = 0.0
        output = self.lb.compute(loc_a, loc_z)
        self.assertEqual(output,expectedoutput)


    def test_compute_latency_between_nonzero(self):
        lon = 0.0
        lat = 0.0
        loc = 'USA'
        loc_a = (float(lat), float(lon), str(loc))
        loc_z = (float(lat), float(140), str(loc))
        self.lb.region_group = collections.OrderedDict([('USA', 0), ('CAN', 0), ('MEX', 0), ('DEU', 1), ('GBR', 1)])
        expectedoutput = 15567.2897302
        output = self.lb.compute(loc_a,loc_z)
        self.assertGreaterEqual(output, 0.0)

    def test_compute_latency_between_gtzero(self):
        lon = 0.0
        lat = 0.0
        loc = 'USA'
        loc_a = (float(lat), float(lon), str(loc))
        loc_z = (float(lat), float(140), str(loc))
        self.lb.region_group = collections.OrderedDict([('DEU', 0), ('GBR', 0),('USA', 1), ('CAN', 1), ('MEX', 1)])
        expectedoutput = 35567.2897302
        output = self.lb.compute(loc_a,loc_z)
        self.assertGreaterEqual(output,0.0)







