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

from conductor.solver.request import parser
from conductor.solver.simulators.a_and_ai import region_generator as gen


class RequestSimulator(object):

    def __init__(self, conf):
        self.conf = conf

        self.requests = {}

        self.region_generator = gen.RegionGenerator(self.conf)
        self.region_generator.set_regions()

    def generate_requests(self, template=None, data=None):
        if template is not None:
            # shouldn't need a region generator if the template is provided
            request = parser.Parser()
        else:
            request = parser.Parser(self.region_generator)
        # request.parse_data_file(data)
        # request.get_data_engine_interface()
        request.parse_dhv_template(template)
        request.assgin_constraints_to_demands()
        self.requests["dhv"] = request

    def load_regions(self, data_file=None):
        self.region_generator.set_regions(data_file)
