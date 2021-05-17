#
# -------------------------------------------------------------------------
#   Copyright (c) 2015-2018 AT&T Intellectual Property
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

import csv
import collections
import json
from conductor.common.models import region_placeholders
from conductor.common.music import api


class LatencyDataLoader(object):

    def __init__(self):
        rph = region_placeholders.RegionPlaceholders()
        music = api.API()
        print("Music version %s" % music.version())

    # load data into region place holder
    def load_into_rph(self, json_data):
        datamap = collections.OrderedDict()
        group_map = collections.OrderedDict()
        datamap = json.loads(json_data)

        # for i, j in enumerate(datamap):
        #    group_map[j['group']] = j['countries']

        music = api.API()

        # for row in group_map:
        # music.row_create()

        kwargs = {'keyspace': 'conductor_inam', 'table': 'region_placeholders', 'pk_name': 'id'}
        for row in enumerate(datamap):
            kwargs['pk_value'] = id(row)
            kwargs['values'] = {'region_name': row['group'], 'countries': row['countries']}
            music.row_create(**kwargs)

        print(group_map)

    def load_into_country_letancy(self, json_data):
        datamap = collections.OrderedDict()
        group_map = collections.OrderedDict()
        datamap = json.loads(json_data)

        # for i, j in enumerate(datamap):
        #    group_map[j['group']] = j['countries']

        music = api.API()

        # for row in group_map:
        #   music.row_create()

        kwargs = {'keyspace': 'conductor_inam', 'table': 'country_latency', 'pk_name': 'id'}
        for row in enumerate(datamap):
            kwargs['pk_value'] = id(row)
            kwargs['values'] = {'country_name': row['country_name'], 'groups': row['groups']}
            music.row_create(**kwargs)

        print(group_map)

# json_string = '[{"group": "EMEA-CORE1",  "countries" : "FRA|DEU|NLD|GBR1"},' \
#              '{"group": "EMEA-CORE2",  "countries" : "FRA|DEU|NLD|GBR2"},' \
#              '{"group": "EMEA-CORE3",  "countries" : "FRA|DEU|NLD|GBR3"},' \
#              '{"group": "EMEA-CORE4",  "countries" : "FRA|DEU|NLD|GBR4"}]'

# test = LatencyDataLoader()
# test.parseJSON(json_string)
