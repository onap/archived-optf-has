#!/usr/bin/env python

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
