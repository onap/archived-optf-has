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

import copy
import json
import unicodedata

from conductor.common.models.triage_tool import TriageTool
from conductor.common.music.model import base
from oslo_config import cfg
try:
    from StringIO import StringIO ## for Python 2
except ImportError:
    from io import StringIO ## for Python 3

CONF = cfg.CONF
io = StringIO()


class TriageLatency(object):

    def __init__(self):
        self.TriageTool = base.create_dynamic_model(
            keyspace=CONF.keyspace, baseclass=TriageTool, classname="TriageTool")
        self.optimzation={}
        self.latency_dropped = []


    def takeOpimaztionType(self, optimation_type):
        self.optimzation['opimization_type'] = optimation_type

    def latencyDroppedCandiate(self, candidate_id, demand_id, reason):
        candiate_dropped = {}
        candiate_dropped['demand_id'] = demand_id
        candiate_dropped['candidate_id'] = candidate_id
        candiate_dropped['reason'] = reason
        self.latency_dropped.append(candiate_dropped)

    def updateTriageLatencyDB(self, plan_id, request_id):
        if self.optimzation['opimization_type'] == "distance_between":
            optimization_type = self.optimzation['opimization_type']
            op = json.dumps(optimization_type)
            triage_dropped_list = self.TriageTool.query.get_plan_by_col("id", plan_id)
            triageRowUpdate = triage_dropped_list[0]
            triageRowUpdate.optimization_type = op
            triageRowUpdate.update()
        elif self.optimzation['opimization_type'] == "latency_between":
            latency_dropped = {}
            optimization_type = self.optimzation['opimization_type']
            latency_dropped['dropped_cadidtes'] = self.latency_dropped
            op= json.dumps(optimization_type)
            triageRowUpdate = self.TriageTool.query.get_plan_by_col("id", plan_id)[0]
            triageRowUpdate.optimization_type = op
            copy_translator = copy.copy(triageRowUpdate.triage_translator)
            copy_tra = unicodedata.normalize('NFKD', copy_translator).encode('ascii', 'ignore')
            cop_ta = json.loads(copy_tra)
            for tt in cop_ta['translator_triage']['dropped_candidates']:
                for tl in latency_dropped['dropped_cadidtes']:
                    if tt['name'] == tl['demand_id']:
                        tt['translator_triage']['lantency_dropped'].append(tl)

            triaL = json.dumps(latency_dropped)
            triageRowUpdate.triage_translator = triaL
            triageRowUpdate.update()
