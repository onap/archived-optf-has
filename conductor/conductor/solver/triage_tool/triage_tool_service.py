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



