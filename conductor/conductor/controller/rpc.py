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

import uuid


class ControllerRPCEndpoint(object):
    """Controller Endpoint"""

    def __init__(self, conf, plan_class):
        self.conf = conf
        self.Plan = plan_class

    def plan_create(self, ctx, arg):
        """Create a plan"""
        name = arg.get('name', str(uuid.uuid4()))
        timeout = arg.get('timeout', self.conf.controller.timeout)
        recommend_max = arg.get('limit', self.conf.controller.limit)
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
            plans = self.Plan.query.filter_by(id=plan_id)
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
            plans = self.Plan.query.filter_by(id=plan_id)
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
