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

from oslo_config import cfg
from oslo_log import log
import collections
from conductor.common.models.region_placeholders import RegionPlaceholders
from conductor.common.models.country_latency import CountryLatency
from conductor.common.music.model import base

CONF = cfg.CONF
LOG = log.getLogger(__name__)

class LatencyDataLoader(object):

    def __init__(self):
        self.Region_PlaceHolder = base.create_dynamic_model(keyspace=CONF.keyspace, baseclass=RegionPlaceholders, classname="RegionPlaceholders")
        self.Country_Latency = base.create_dynamic_model(keyspace=CONF.keyspace, baseclass=CountryLatency,classname="CountryLatency")

    # load data into region place holder
    def load_into_rph(self, data):
         LOG.debug("load_into_rph")
         datamap = collections.OrderedDict()
         group_map = collections.OrderedDict()
         datamap = data #= json.loads(json_data)

         region_placeholders = self.Region_PlaceHolder.query.all()
         regions_id_list = list()
         for region in region_placeholders:
             regions_id_list.append(region.id)

         LOG.debug("Removing all existing data from region place holders table")
         for region_id in regions_id_list:
             replace_holder_row = self.Region_PlaceHolder()
             LOG.debug("Removing "+region_id)
             response = replace_holder_row.delete(region_id)
             LOG.debug("Removed " +str(response) )



         for i, j in enumerate(datamap):
             group_map[j['group']] = j['countries']

         LOG.debug("inserting data into region place holders table")
         for k, v in group_map.items():
            group = k
            countries = {k:v}
            LOG.debug("inserting region "+group)
            replace_holder_row = self.Region_PlaceHolder(group,countries)
            response = replace_holder_row.insert()
            LOG.debug("inserted " + str(response))


    def load_into_country_letancy(self, data):
         LOG.debug("load_into_country_letancy")
         datamap = collections.OrderedDict() # Ordered Dict because the order of rows is important
         group_map = collections.OrderedDict()
         datamap = data#json.loads(data)


         #before inserting the new data, remove the existing data from the country_latency table
         country_latency_data = self.Country_Latency.query.all()
         country_id_list = list()
         for country in country_latency_data:
             country_id_list.append(country.id)

         LOG.debug("Removing all existing data from country latency table")
         for country_id in country_id_list:
             replace_holder_row = self.Country_Latency()
             LOG.debug("removing " + country_id)
             response = replace_holder_row.delete(country_id)
             LOG.debug("removed " + str(response))




         for i, j in enumerate(datamap):
             group_map[j['country_name']] = j['groups']

         LOG.debug("inserting data into country latency table")
         for k, v in group_map.items():
             country_name = k
             group = list()
             for g in v.split('|'):
                 group.append(g)

             groups = group
             LOG.debug("inserting country " + country_name)
             country_rules_holder_row = self.Country_Latency(country_name,groups)
             response = country_rules_holder_row.insert();
             LOG.debug("inserted " + str(response))






