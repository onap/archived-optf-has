import json
from oslo_config import cfg
import copy
from conductor.common.models.triage_tool import TriageTool
from conductor.common.music.model import base
from StringIO import StringIO
CONF = cfg.CONF
io = StringIO()
from json import loads
from ast import literal_eval
from collections import MutableMapping
import ast
import unicodedata
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
            triageRowUpdate = self.TriageTool.query.get_plan_by_col("id", plan_id)[0]
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
