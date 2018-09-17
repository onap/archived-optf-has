import json
import time
from oslo_log import log
from oslo_config import cfg
from conductor.common.models.plan import Plan
from conductor.common.models.triage_tool import TriageTool
from conductor.common.music.model import base

CONF = cfg.CONF
LOG = log.getLogger(__name__)
class TriageToolService(object):

    def __init__(self):
        self.Plan = base.create_dynamic_model(keyspace=CONF.keyspace, baseclass=Plan, classname="Plan")
        self.TriageTool = base.create_dynamic_model(
            keyspace=CONF.keyspace, baseclass=TriageTool, classname="TriageTool")


    # def get_order_by_req_id(self, name):
    #     return self.TriageTool.query.get(name)

    def _get_plans_by_id(self, id):

        triage_info = self.TriageTool.query.get_plan_by_col("id", id)
        triage_data = triage_info[0]
        return triage_data



