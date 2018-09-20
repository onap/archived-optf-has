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

import json
import uuid
from conductor.solver.orders_lock.orders_lock_service import OrdersLockingService
from conductor.solver.triage_tool.triage_tool_service import TriageToolService
from oslo_log import log
from oslo_config import cfg

LOG = log.getLogger(__name__)

CONF = cfg.CONF


class ControllerRPCEndpoint(object):
    """Controller Endpoint"""

    def __init__(self, conf, plan_class):
        self.conf = conf
        self.Plan = plan_class
        self.OrdersLockingService = OrdersLockingService()
        self.TriageToolService = TriageToolService()

    def plan_create(self, ctx, arg):
        """Create a plan"""
        name = arg.get('name', str(uuid.uuid4()))
        LOG.info('Plan name: {}'.format(name))
        timeout = arg.get('timeout', self.conf.controller.timeout)
        recommend_max = arg.get('num_solution', self.conf.controller.limit)
        template = arg.get('template', None)
        status = self.Plan.TEMPLATE
        new_plan = self.Plan(name, timeout, recommend_max, template,
                             status=status)

        if new_plan:
            plan_json = {
                "plan": {
                    "name": new_plan.name,
                    "id": new_plan.id,
                    "status": status,
                }
            }
            rtn = {
                'response': plan_json,
                'error': False}
        else:
            # TODO(jdandrea): Catch and show the error here
            rtn = {
                'response': {},
                'error': True}
        return rtn

    def plans_delete(self, ctx, arg):
        """Delete one or more plans"""
        plan_id = arg.get('plan_id')
        if plan_id:
            plans = self.Plan.query.get_plan_by_col('id', plan_id)
        else:
            plans = self.Plan.query.all()
        for the_plan in plans:
            the_plan.delete()

        rtn = {
            'response': {},
            'error': False}
        return rtn

    def plans_get(self, ctx, arg):
        """Get one or more plans"""
        plan_id = arg.get('plan_id')
        if plan_id:
            plans = self.Plan.query.get_plan_by_col('id', plan_id)
        else:
            plans = self.Plan.query.all()

        plan_list = []
        for the_plan in plans:
            plan_json = {
                "name": the_plan.name,
                "id": the_plan.id,
                "status": the_plan.status,
            }
            if the_plan.message:
                plan_json["message"] = the_plan.message
            if the_plan.solution:
                recs = the_plan.solution.get('recommendations')
                if recs:
                    plan_json["recommendations"] = recs
            plan_list.append(plan_json)

        rtn = {
            'response': {"plans": plan_list},
            'error': False}
        return rtn

    def triage_get(self, ctx, arg):
        id = arg.get('id')
        if id:
            triage_data = self.TriageToolService._get_plans_by_id(id)
        if not  triage_data.triage_solver == None or type(triage_data.triage_solver) == "NoneType":
            triage_solver = json.loads(triage_data.triage_solver)
        else:
            triage_solver = triage_data.triage_solver

        triage_data_list =[]
        triage_data_json = {
            "id":triage_data.id,
            "name":triage_data.name,
            "solver_triage": triage_solver,
            "translator_triage":triage_data.triage_translator,
            "optimization_type": json.loads(triage_data.optimization_type)
        }
        if hasattr(triage_data, 'message'):
            triage_data_json["message"] = triage_data.message

        triage_data_list.append(triage_data_json)

        rtn = {
            'response': {"triageData": triage_data_list},
            'error': False}
        return rtn
    def release_orders(self, ctx, arg):
        rehome_decisions = []
        release_orders = arg.get("release-locks")
        LOG.info("Following Orders were received in this release call from MSO:{}".format(release_orders))

        for release_order in release_orders:
            rehome_decisions = self.OrdersLockingService.rehomes_for_service_resource(release_order['status'],
                                                                                      release_order['service-resource-id'],
                                                                                      rehome_decisions)

        self.OrdersLockingService.do_rehome(rehome_decisions)

        if not rehome_decisions:
            response_msg = "Orders have been released, but no plans are effected in Conductor"
        else:
            response_msg = rehome_decisions

        LOG.info(response_msg)
        rtn = {
            'response': {
                "status": "success",
                "message": response_msg
            }
        }
        return rtn