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
from conductor.common.models.order_lock import OrderLock
from conductor.common.music.model import base

CONF = cfg.CONF
LOG = log.getLogger(__name__)

class OrdersLockingService(object):

    def __init__(self):
        self.Plan = base.create_dynamic_model(keyspace=CONF.keyspace, baseclass=Plan, classname="Plan")
        self.OrderLock = base.create_dynamic_model(
            keyspace=CONF.keyspace, baseclass=OrderLock, classname="OrderLock")

    def get_order_by_resource_id(self, service_resource_id):
        return self.OrderLock.query.get(service_resource_id)

    def _get_plans_by_id(self, order_id):

        order_locks = self.OrderLock.query.get_plan_by_col("id", order_id)
        order_record = order_locks[0]
        if order_record:
            LOG.debug("Getting Order lock record {} based on conflict id {}".format(order_record, order_id))
            return getattr(order_record, 'plans')

    def _update_order_status(self, rehome_status, plans, order_lock):

        updated_plan_statuses = dict()
        for plan_id, plan_attributes in plans.items():
            # Convert the string into dictionary for plans field
            plan_dict = json.loads(plan_attributes)
            # Change the status to 'completed' if previous status is 'under_spin_up'
            # else change to 'rehome'

            if rehome_status == OrderLock.FAILED:
                new_status = OrderLock.FAILED
            else:
                if plan_dict.get('status') == OrderLock.UNDER_SPIN_UP:
                    new_status = OrderLock.COMPLETED
                else:
                    new_status = OrderLock.REHOME

            updated_fields = {
                "status": new_status,
                "updated": str(self.current_time_millis())
            }
            values = {
                "id": order_lock.id,
                "is_spinup_completed": True,
                "spinup_completed_timestamp": self.current_time_millis()
            }
            order_lock.update(plan_id, updated_fields, values)
            updated_plan_statuses[plan_id] = new_status

        return updated_plan_statuses

    # TODO(Saisree)
    def update_order_status_and_get_effected_plans(self, rehome_status, service_resource_id):
        # A music call to orders-lock table to update the status of the plans AND get this
        # list of effected plans for this service_sersource_id - hardcoded

        effected_plans = dict()
        order_locks = self.OrderLock.query.all()

        for order_lock_record in order_locks:

            plans = getattr(order_lock_record, 'plans')
            for plan_id, plan_attributes in plans.items():
                # Convert the string into dictionary for plans field
                plan_dict = json.loads(plan_attributes)

                # check if the service_resource_id is matched and the status is 'under spin-up'
                if plan_dict.get('service_resource_id', None) == service_resource_id and \
                    plan_dict.get('status', None) == OrderLock.UNDER_SPIN_UP:

                    # update the status of the plans in order_locks table
                    self._update_order_status(rehome_status, plans, order_lock_record)

                    # get the latest plans from order_locks table
                    effected_plans = self._get_plans_by_id(getattr(order_lock_record, 'id'))
                    break

        return effected_plans

    def _update_failed_plan(self, plan_id, service_resource_id):

        # update the waiting/pending plan status to 'error' with
        # proper error message if MSO spin-up fails
        p = self.Plan.query.get_plan_by_col("id", plan_id)[0]
        if p and p.status == p.WAITING_SPINUP:
            p.status = p.ERROR
            p.message = "Error due to failed cloud candidate " \
                        "spin-up in MSO (service_resource_id: {}).".format(service_resource_id)
            p.update()

    # TODO(Ikram)
    def rehomes_for_service_resource(self, rehome_status, service_resource_id, rehome_decisions):
        # Sample of expected output from this method is as follows
        # rehomes = {
        #            {"plan_id": "p1", "should_rehome": True},
        #            {"plan_id": "p2", "should_rehome": True},
        #            {"plan_id": "p3", "should_rehome": True}
        # }

        effected_plans = self.update_order_status_and_get_effected_plans(rehome_status, service_resource_id)
        LOG.debug("The effected plan list {} for service_resource_id"
                  " {} MSO release call".format(effected_plans, service_resource_id))

        if effected_plans:

            for plan_id, plan_attribute in effected_plans.items():
                rehome_this_plan = True
                rehome_decision_record = dict()
                # Should we take a decision just on the basis of this? What if the status of the plan was not
                # successfully set to 'rehome' but it actually DOES need a rehome based on the data from the order Q?

                #convert the string to JSON format
                plan = json.loads(plan_attribute)

                if plan['status'] == OrderLock.FAILED:
                    self._update_failed_plan(plan_id, service_resource_id)
                    continue

                elif plan['status'] != OrderLock.REHOME:
                    LOG.info("Though effected, but will not retrigger "
                             "the plan {}, since plan.status {} is not 'rehome'.".format(plan_id, plan['status']))
                    # What if the plan should be rehomed based on the Order Q data - this means, this infromation is stale
                    # Q must be clearned up - i.e. update plan status in the order Q to
                    # completed (or whatever plan.status is)
                    continue

                order_locks = self.OrderLock.query.all()

                # Go through the order_lock table
                for order_lock_record in order_locks:
                    plans = getattr(order_lock_record, 'plans')
                    if plan_id in plans:
                        # Convert the string into dictionary for plans field
                        plan_dict = json.loads(plans[plan_id])
                        # check if there is a record that is not able to 'rehome' (which means the status in order_locks.plans is not 'rehome' or 'under-spin-up'
                        if plan_dict.get('status', None) not in OrderLock.REHOMABLE:
                            rehome_this_plan = False
                            break

                rehome_decision_record['plan_id'] = plan_id
                rehome_decision_record['should_rehome'] = rehome_this_plan
                rehome_decisions.append(rehome_decision_record)

        return rehome_decisions

    def do_rehome(self, rehome_decisions):

        for decision in rehome_decisions:
            if decision.get('should_rehome'):
                LOG.info("Retriggering plan {}.".format(decision['plan_id']))
                self.retrigger_plan(decision['plan_id'])
            else:
                LOG.info("Will not retrigger plan {}.".format(decision['plan_id']))

    def retrigger_plan(self, plan_id):
        # update plan table set status to 'template' for plan_id
        plan = self.Plan.query.get_plan_by_col("id", plan_id)[0]
        plan.rehome_plan()
        plan.update()
        return

    def current_time_millis(self):
        """Current time in milliseconds."""
        return int(round(time.time() * 1000))