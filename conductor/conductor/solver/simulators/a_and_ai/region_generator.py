#!/bin/python

import csv
import os
from oslo_log import log
import random
import sys

from conductor.solver.resource import region as reg

LOG = log.getLogger(__name__)


class RegionGenerator(object):

    def __init__(self, conf):
        path = os.path.abspath(__file__)
        self.data_path = os.path.dirname(path)

        self.invalid_region_list = \
            ['LIMAOHRA', 'BFTNOHRS', 'DBLNIRDBDC0', 'DBLNIRBEDC0']
        self.regions = {}
        self.zones = {}

        self.most_longitude = sys.float_info.min
        self.least_longitude = sys.float_info.max
        self.most_latitude = sys.float_info.min
        self.least_latitude = sys.float_info.max

        self.conf = conf

    def set_regions(self, _index=100):
        self.read_regions(_index)

        for rid in self.regions:
            region = self.regions[rid]
            if region.location[1] > self.most_longitude:
                self.most_longitude = region.location[1]
            if region.location[1] < self.least_longitude:
                self.least_longitude = region.location[1]
            if region.location[0] > self.most_latitude:
                self.most_latitude = region.location[0]
            if region.location[0] < self.least_latitude:
                self.least_latitude = region.location[0]

    def create_nodes(self):
        with open('./nodes.csv', 'rU') as clli_list:
            clli_reader = csv.reader(clli_list, delimiter=',')
            for row in clli_reader:
                node_name = row[0].strip()
                longitude = float(row[1])
                latitude = float(row[2])

                if longitude == 0.0 and latitude == 0.0:
                    continue
                if node_name in self.invalid_region_list:
                    continue

                node = reg.Region(node_name)
                node.location = (latitude, longitude)

                if node.region_id not in self.regions.keys():
                    self.regions[node.region_id] = node
                else:
                    LOG.debug("error: duplicated region = %s" % node.region_id)

    def read_regions(self, _index=100):
        self.regions.clear()
        self.zones.clear()

        if _index == 100:
            with open(self.data_path +
                      '/extended_100_regions.csv', 'rU') as region_list:
                region_reader = csv.reader(region_list, delimiter=',')
                for row in region_reader:
                    region_id = row[0].strip()
                    region_type = row[1].strip()
                    latitude = float(row[2])
                    longitude = float(row[3])
                    area = row[4].strip()
                    zone_name = row[5].strip()
                    cost = int(row[6])
                    prop = row[7]

                    if zone_name not in self.zones.keys():
                        zone = reg.Zone(zone_name)
                        zone.zone_type = "update"
                        zone.region_list.append(region_id)
                        self.zones[zone_name] = zone
                    else:
                        zone = self.zones[zone_name]
                        zone.region_list.append(region_id)

                    if region_id not in self.regions.keys():
                        region = reg.Region(region_id)
                        region.region_type = region_type
                        region.location = (latitude, longitude)
                        region.address["country_code"] = area
                        region.zones[zone_name] = self.zones[zone_name]
                        region.cost = cost
                        region.properties["sriov"] = prop
                        self.regions[region_id] = region
                    else:
                        LOG.debug("error")
        else:
            LOG.debug("error no file exist")

    def set_region_type(self, _num_of_large=100, _num_of_medium=1000):
        if _num_of_large > 0:
            sampled_large_region_ids = random.sample(
                self.regions.keys(), _num_of_large)
            for rid in self.regions:
                region = self.regions[rid]
                if rid in sampled_large_region_ids:
                    region.region_type = 'L'

        if _num_of_medium > 0:
            sampled_medium_region_ids = random.sample(
                self.regions.keys(), _num_of_medium)
            for rid in self.regions:
                region = self.regions[rid]
                if region.region_type is None:
                    if rid in sampled_medium_region_ids:
                        region.region_type = 'M'
                    else:
                        region.region_type = 'S'

    def set_address(self):
        for rid in self.regions:
            region = self.regions[rid]
            if region.location[1] > self.most_longitude:
                self.most_longitude = region.location[1]
            if region.location[1] < self.least_longitude:
                self.least_longitude = region.location[1]
            if region.location[0] > self.most_latitude:
                self.most_latitude = region.location[0]
            if region.location[0] < self.least_latitude:
                self.least_latitude = region.location[0]

        longitude_range = self.most_longitude - self.least_longitude
        latitude_range = self.most_latitude - self.least_latitude

        longitude_bound = self.least_longitude + (longitude_range / 2.0)
        latitude_bound = self.most_latitude - (latitude_range / 2.0)

        for rid in self.regions:
            region = self.regions[rid]
            if region.location[1] >= self.least_longitude and \
                    region.location[1] < longitude_bound and \
                    region.location[0] <= self.most_latitude and \
                    region.location[0] > latitude_bound:
                region.address["country_code"] = 'US'
            elif region.location[1] >= self.least_longitude and \
                    region.location[1] < longitude_bound and \
                    region.location[0] <= latitude_bound and \
                    region.location[0] >= self.least_latitude:
                region.address["country_code"] = 'SA'
            elif region.location[1] >= longitude_bound and \
                    region.location[1] <= self.most_longitude and \
                    region.location[0] <= self.most_latitude and \
                    region.location[0] > latitude_bound:
                region.address["country_code"] = 'EU'
            elif region.location[1] >= longitude_bound and \
                    region.location[1] <= self.most_longitude and \
                    region.location[0] <= latitude_bound and \
                    region.location[0] >= self.least_latitude:
                region.address["country_code"] = 'ASIA'
            else:
                LOG.debug("error while setting address")

    def set_zone(self):
        sampled_region_list = random.sample(
            self.regions.keys(), len(self.regions) / 2)
        for rid in self.regions:
            region = self.regions[rid]
            if rid in sampled_region_list:
                region.zones["zone1"] = "zone1"
            else:
                region.zones["zone2"] = "zone2"

    def set_cost(self):
        max_large_region = 10
        max_medium_region = 20
        max_small_region = 30

        for rid in self.regions:
            region = self.regions[rid]
            if region.region_type == 'L':
                region.cost = random.randint(1, max_large_region)
            elif region.region_type == 'M':
                region.cost = random.randint(max_large_region,
                                             max_medium_region)
            else:
                region.cost = random.randint(max_medium_region,
                                             max_small_region)

    def set_properties(self):
        sampled_region_list = random.sample(
            self.regions.keys(), len(self.regions) / 3 * 2)
        for rid in self.regions:
            region = self.regions[rid]
            if rid in sampled_region_list:
                region.properties["sriov"] = True
            else:
                region.properties["sriov"] = False

    def sample(self, _num_of_us=70, _num_of_eu=20, _num_of_asia=10):
        us_list = []
        eu_list = []
        asia_list = []
        for rid in self.regions:
            region = self.regions[rid]
            if region.address["country_code"] == 'US':
                us_list.append(rid)
            elif region.address["country_code"] == 'EU':
                eu_list.append(rid)
            elif region.address["country_code"] == 'ASIA':
                asia_list.append(rid)

        if _num_of_us > 0:
            sampled_us = random.sample(us_list, _num_of_us)
            for rid in self.regions:
                if self.regions[rid].address["country_code"] == 'US' and \
                   rid not in sampled_us:
                    del self.regions[rid]

        if _num_of_eu > 0:
            sampled_eu = random.sample(eu_list, _num_of_eu)
            for rid in self.regions:
                if self.regions[rid].address["country_code"] == 'EU' and \
                   rid not in sampled_eu:
                    del self.regions[rid]

        if _num_of_asia > 0:
            sampled_asia = random.sample(asia_list, _num_of_asia)
            for rid in self.regions:
                if self.regions[rid].address["country_code"] == 'ASIA' and \
                   rid not in sampled_asia:
                    del self.regions[rid]

    def print_regions(self, _type, _area):
        count = 1
        for rid in self.regions:
            region = self.regions[rid]
            if region.region_type == _type:
                if region.address["country_code"] == _area:
                    msg = "{} id = {}, loc = {}, " + \
                          "zones = {}, cost = {}, prop = {}"
                    LOG.debug(msg.format(count, rid,
                              region.location, region.zones.keys(),
                              region.cost, region.properties["sriov"]))
                    count += 1

    def write_regions(self):
        csvfile = open('./extended_100_regions.csv', 'wb')
        region_writer = csv.writer(csvfile, delimiter=',')
        for rid in self.regions:
            region = self.regions[rid]
            s = []
            s.append(rid)
            s.append(region.region_type)
            s.append(region.location[0])
            s.append(region.location[1])
            s.append(region.address["country_code"])
            s.append(region.zones.keys()[0])
            s.append(region.cost)
            s.append(region.properties["sriov"])
            region_writer.writerow(s)
        csvfile.close()


# for unit test
if __name__ == "__main__":
    rg = RegionGenerator()
    """
    rg.create_nodes()
    rg.set_region_type()
    rg.set_address()
    rg.set_zone()
    rg.set_cost()
    rg.set_properties()
    rg.sample()
    rg.write_regions()
    """
    rg.read_regions()

    LOG.debug("--- large size region")
    LOG.debug("- US")
    rg.print_regions('L', 'US')
    # LOG.debug("- SA")
    # rg.print_regions('L', 'SA')
    LOG.debug("- EU")
    rg.print_regions('L', 'EU')
    LOG.debug("- ASIA")
    rg.print_regions('L', 'ASIA')

    LOG.debug("--- medium size region")
    LOG.debug("- US")
    rg.print_regions('M', 'US')
    # LOG.debug("- SA")
    # rg.print_regions('M', 'SA')
    LOG.debug("- EU")
    rg.print_regions('M', 'EU')
    LOG.debug("- ASIA")
    rg.print_regions('M', 'ASIA')

    LOG.debug("--- small size region")
    LOG.debug("- US")
    rg.print_regions('S', 'US')
    # LOG.debug("- SA")
    # rg.print_regions('S', 'SA')
    LOG.debug("- EU")
    rg.print_regions('S', 'EU')
    LOG.debug("- ASIA")
    rg.print_regions('S', 'ASIA')
