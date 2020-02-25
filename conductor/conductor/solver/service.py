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

import collections

import conductor.common.prometheus_metrics as PC
import cotyledon
import json
import time
import traceback
import json
import socket
import json
from oslo_config import cfg
from oslo_log import log

from conductor.common.models import plan, region_placeholders, country_latency, group_rules, groups
from conductor.common.models import order_lock
from conductor.common.models import order_lock_history
from conductor.common.music import api
from conductor.common.music import messaging as music_messaging
from conductor.common.music.model import base
from conductor.i18n import _LE, _LI
from conductor import messaging
from conductor import service
from conductor.solver.optimizer import optimizer
from conductor.solver.request import parser
from conductor.solver.utils import constraint_engine_interface as cei
from conductor.common.utils import conductor_logging_util as log_util
from conductor.common.models.order_lock import OrderLock
from conductor.common.models import triage_tool
from conductor.common.models.triage_tool import TriageTool

# To use oslo.log in services:
#
# 0. Note that conductor.service.prepare_service() bootstraps this.
#    It's set up within conductor.cmd.SERVICENAME.
# 1. Add "from oslo_log import log"
# 2. Also add "LOG = log.getLogger(__name__)"
# 3. For i18n support, import appropriate shortcuts as well:
#    "from i18n import _, _LC, _LE, _LI, _LW  # noqa"
#    (that's for primary, critical, error, info, warning)
# 4. Use LOG.info, LOG.warning, LOG.error, LOG.critical, LOG.debug, e.g.:
#    "LOG.info(_LI("Something happened with {}").format(thingie))"
# 5. Do NOT put translation wrappers around any LOG.debug text.
# 6. Be liberal with logging, especially in the absence of unit tests!
# 7. Calls to print() are verboten within the service proper.
#    Logging can be redirected! (In a CLI-side script, print() is fine.)
#
# Usage: http://docs.openstack.org/developer/oslo.i18n/usage.html

LOG = log.getLogger(__name__)

# To use oslo.config in services:
#
# 0. Note that conductor.service.prepare_service() bootstraps this.
#    It's set up within conductor.cmd.SERVICENAME.
# 1. Add "from oslo_config import cfg"
# 2. Also add "CONF = cfg.CONF"
# 3. Set a list of locally used options (SOLVER_OPTS is fine).
#    Choose key names thoughtfully. Be technology-agnostic, avoid TLAs, etc.
# 4. Register, e.g. "CONF.register_opts(SOLVER_OPTS, group='solver')"
# 5. Add file reference to opts.py (may need to use itertools.chain())
# 6. Run tox -e genconfig to build a new config template.
# 7. If you want to load an entire config from a CLI you can do this:
#    "conf = service.prepare_service([], config_files=[CONFIG_FILE])"
# 8. You can even use oslo_config from a CLI and override values on the fly,
#    e.g., "CONF.set_override('hostnames', ['music2'], 'music_api')"
#    (leave the third arg out to use the DEFAULT group).
# 9. Loading a config from a CLI is optional. So long as all the options
#    have defaults (or you override them as needed), it should all work.
#
# Docs: http://docs.openstack.org/developer/oslo.config/

CONF = cfg.CONF

SOLVER_OPTS = [
    cfg.IntOpt('workers',
               default=1,
               min=1,
               help='Number of workers for solver service. '
                    'Default value is 1.'),
    cfg.IntOpt('solver_timeout',
               default=480,
               min=1,
               help='The timeout value for solver service. '
                    'Default value is 480 seconds.'),
    cfg.BoolOpt('concurrent',
                default=False,
                help='Set to True when solver will run in active-active '
                     'mode. When set to False, solver will restart any '
                     'orphaned solving requests at startup.'),
    cfg.IntOpt('timeout',
               default=600,
               min=1,
               help='Timeout for detecting a VM is down, and other VMs can pick the plan up. '
                    'This value should be larger than solver_timeout'
                    'Default value is 10 minutes. (integer value)'),
    cfg.IntOpt('max_solver_counter',
               default=1,
               min=1)
]

CONF.register_opts(SOLVER_OPTS, group='solver')

# Pull in service opts. We use them here.
OPTS = service.OPTS
CONF.register_opts(OPTS)


class SolverServiceLauncher(object):
    """Launcher for the solver service."""
    def __init__(self, conf):

        self.conf = conf

        # Set up Music access.
        self.music = api.API()
        self.music.keyspace_create(keyspace=conf.keyspace)

        # Dynamically create a plan class for the specified keyspace
        self.Plan = base.create_dynamic_model(
            keyspace=conf.keyspace, baseclass=plan.Plan, classname="Plan")
        self.OrderLock =base.create_dynamic_model(
            keyspace=conf.keyspace, baseclass=order_lock.OrderLock, classname="OrderLock")
        self.OrderLockHistory = base.create_dynamic_model(
            keyspace=conf.keyspace, baseclass=order_lock_history.OrderLockHistory, classname="OrderLockHistory")
        self.RegionPlaceholders = base.create_dynamic_model(
            keyspace=conf.keyspace, baseclass=region_placeholders.RegionPlaceholders, classname="RegionPlaceholders")
        self.CountryLatency = base.create_dynamic_model(
            keyspace=conf.keyspace, baseclass=country_latency.CountryLatency, classname="CountryLatency")
        self.TriageTool = base.create_dynamic_model(
            keyspace=conf.keyspace, baseclass=triage_tool.TriageTool ,classname = "TriageTool")
        #self.Groups = base.create_dynamic_model(
        #    keyspace=conf.keyspace, baseclass=groups.Groups, classname="Groups")
        #self.GroupRules = base.create_dynamic_model(
        #    keyspace=conf.keyspace, baseclass=group_rules.GroupRules, classname="GroupRules")

        # Initialize Prometheus metrics Endpoint
        # Solver service uses index 1
        PC._init_metrics(1)

        if not self.Plan:
            raise
        if not self.OrderLock:
            raise
        if not self.OrderLockHistory:
            raise
        if not self.RegionPlaceholders:
            raise
        if not self.CountryLatency:
            raise
        if not self.TriageTool:
            raise
        #if not self.Groups:
        #    raise
        #if not self.GroupRules:
        #    raise

    def run(self):
        kwargs = {'plan_class': self.Plan,
                  'order_locks': self.OrderLock,
                  'order_locks_history': self.OrderLockHistory,
                  'region_placeholders': self.RegionPlaceholders,
                  'country_latency': self.CountryLatency,
                  'triage_tool': self.TriageTool
                  #'groups': self.Groups,
                  #'group_rules': self.GroupRules
                  }
        # kwargs = {'plan_class': self.Plan}
        svcmgr = cotyledon.ServiceManager()
        svcmgr.add(SolverService,
                   workers=self.conf.solver.workers,
                   args=(self.conf,), kwargs=kwargs)
        svcmgr.run()


class SolverService(cotyledon.Service):
    """Solver service."""

    # This will appear in 'ps xaf'
    name = "Conductor Solver"

    regions = collections.OrderedDict()
    countries = list()

    def __init__(self, worker_id, conf, **kwargs):
        """Initializer"""

        LOG.debug("%s" % self.__class__.__name__)
        super(SolverService, self).__init__(worker_id)
        self._init(conf, **kwargs)
        self.running = True

    def _init(self, conf, **kwargs):
        """Set up the necessary ingredients."""
        self.conf = conf
        self.kwargs = kwargs

        self.Plan = kwargs.get('plan_class')
        self.OrderLock = kwargs.get('order_locks')
        self.OrderLockHistory = kwargs.get('order_locks_history')
        #self.OrderLock =kwargs.get('order_locks')
        self.RegionPlaceholders = kwargs.get('region_placeholders')
        self.CountryLatency = kwargs.get('country_latency')
        self.TriageTool = kwargs.get('triage_tool')

        # self.Groups = kwargs.get('groups')
        #self.GroupRules = kwargs.get('group_rules')
        # Set up the RPC service(s) we want to talk to.
        self.data_service = self.setup_rpc(conf, "data")

        # Set up the cei and optimizer
        self.cei = cei.ConstraintEngineInterface(self.data_service)
        # self.optimizer = optimizer.Optimizer(conf)

        # Set up Music access.
        self.music = api.API()
        self.solver_owner_condition = {
            "solver_owner": socket.gethostname()
        }
        self.translated_status_condition = {
            "status": self.Plan.TRANSLATED
        }
        self.solving_status_condition = {
            "status": self.Plan.SOLVING
        }

        if not self.conf.solver.concurrent:
            self._reset_solving_status()

    def _gracefully_stop(self):
        """Gracefully stop working on things"""
        pass

    def current_time_seconds(self):
        """Current time in milliseconds."""
        return int(round(time.time()))

    def _reset_solving_status(self):
        """Reset plans being solved so they are solved again.

        Use this only when the solver service is not running concurrently.
        """

        plans = self.Plan.query.get_plan_by_col("status", self.Plan.SOLVING)
        for the_plan in plans:
            the_plan.status = self.Plan.TRANSLATED
            # Use only in active-passive mode, so don't have to be atomic
            the_plan.update()

    def _restart(self):
        """Prepare to restart the service"""
        pass

    def millisec_to_sec(self, millisec):
        """Convert milliseconds to seconds"""
        return millisec/1000

    def setup_rpc(self, conf, topic):
        """Set up the RPC Client"""
        # TODO(jdandrea): Put this pattern inside music_messaging?
        transport = messaging.get_transport(conf=conf)
        target = music_messaging.Target(topic=topic)
        client = music_messaging.RPCClient(conf=conf,
                                           transport=transport,
                                           target=target)
        return client

    def run(self):

        """Run"""
        LOG.debug("%s" % self.__class__.__name__)
        # TODO(snarayanan): This is really meant to be a control loop
        # As long as self.running is true, we process another request.

        while self.running:

            # Delay time (Seconds) for MUSIC requests.
            time.sleep(self.conf.delay_time)

            # plans = Plan.query().all()
            # Find the first plan with a status of TRANSLATED.
            # Change its status to SOLVING.
            # Then, read the "translated" field as "template".
            json_template = None
            p = None

            requests_to_solve = dict()
            regions_maps = dict()
            country_groups = list()

            # Instead of using the query.all() method, now creating an index for 'status'
            # field in conductor.plans table, and query plans by status columns
            translated_plans = self.Plan.query.get_plan_by_col("status", self.Plan.TRANSLATED)
            solving_plans = self.Plan.query.get_plan_by_col("status", self.Plan.SOLVING)


            # combine the plans with status = 'translated' and 'solving' together
            plans = translated_plans + solving_plans

            found_translated_template = False

            for p in plans:
                if p.status == self.Plan.TRANSLATED:
                    json_template = p.translation
                    found_translated_template = True
                    break
                elif p.status == self.Plan.SOLVING and \
                    (self.current_time_seconds() - self.millisec_to_sec(p.updated)) > self.conf.solver.timeout:
                    p.status = self.Plan.TRANSLATED
                    p.update(condition=self.solving_status_condition)
                    break

            if not json_template:
                if found_translated_template:
                    message = _LE("Plan {} status is translated, yet "
                                  "the translation wasn't found").format(p.id)
                    LOG.error(message)
                    p.status = self.Plan.ERROR
                    p.message = message
                    p.update(condition=self.translated_status_condition)
                continue

            if found_translated_template and p and p.solver_counter >= self.conf.solver.max_solver_counter:
                message = _LE("Tried {} times. Plan {} is unable to solve")\
                        .format(self.conf.solver.max_solver_counter, p.id)
                LOG.error(message)
                p.status = self.Plan.ERROR
                p.message = message
                p.update(condition=self.translated_status_condition)
                continue

            log_util.setLoggerFilter(LOG, self.conf.keyspace, p.id)

            p.status = self.Plan.SOLVING
            p.solver_counter += 1
            p.solver_owner = socket.gethostname()

            _is_updated = p.update(condition=self.translated_status_condition)
            if not _is_updated:
                continue

            # other VMs have updated the status and start solving the plan
            if 'FAILURE' in _is_updated:
                continue

            LOG.info(_LI("Sovling starts, changing the template status from translated to solving, "
                             "atomic update response from MUSIC {}").format(_is_updated))

            LOG.info(_LI("Plan {} with request id {} is solving by machine {}. Tried to solve it for {} times.").
                     format(p.id, p.name, p.solver_owner, p.solver_counter))

            _is_success = "FAILURE"
            request = parser.Parser()
            request.cei = self.cei
            request.request_id = p.name
            request.plan_id = p.id
            # getting the number of solutions need to provide
            num_solution = getattr(p, 'recommend_max', '1')
            if num_solution.isdigit():
                num_solution = int(num_solution)

            #TODO(inam/larry): move this part of logic inside of parser and don't apply it to distance_between
            try:
                # getting region placeholders from database and insert/put into regions_maps dictionary
                region_placeholders = self.RegionPlaceholders.query.all()
                for region in region_placeholders:
                    regions_maps.update(region.countries)

                # getting country groups from database and insert into the country_groups list
                customer_loc = ''
                location_list = json_template["conductor_solver"]["locations"]
                for location_id, location_info in location_list.items():
                    customer_loc = location_info['country']

                countries = self.CountryLatency.query.get_plan_by_col("country_name", customer_loc)
                LOG.info("Customer Location for Latency Reduction " + customer_loc)

                if len(countries) == 0:
                    LOG.info("country is not present is country latency table, looking for * wildcard entry")
                    countries = self.CountryLatency.query.get_plan_by_col("country_name","*")
                if len(countries) != 0:
                    LOG.info("Found '*' wild card entry in country latency table")
                else:
                    msg = "No '*' wild card entry found in country latency table. No solution will be provided"
                    LOG.info(msg)
                    p.message = msg

                for country in countries:
                    country_groups = country.groups

                LOG.info("Done getting Latency Country DB Groups ")
            except Exception as error_msg:
                LOG.error("Exception thrown while reading region_placeholders and country groups information "
                          "from database. Exception message: {}".format(error_msg))

            try:
                request.parse_template(json_template, country_groups, regions_maps)
                request.assgin_constraints_to_demands()
                requests_to_solve[p.id] = request
                opt = optimizer.Optimizer(self.conf, _requests=requests_to_solve)
                solution_list = opt.get_solution(num_solution)

            except Exception as err:
                message = _LE("Plan {} status encountered a "
                              "parsing error: {}").format(p.id, err)
                LOG.error(traceback.print_exc())
                p.status = self.Plan.ERROR
                p.message = message
                while 'FAILURE' in _is_success:
                    _is_success = p.update(condition=self.solver_owner_condition)
                    LOG.info(_LI("Encountered a parsing error, changing the template status from solving to error, "
                                 "atomic update response from MUSIC {}").format(_is_success))

                continue

            LOG.info("Preparing the recommendations ")
            # checking if the order is 'initial' or 'speed changed' one
            is_speed_change = False
            if request and request.request_type == 'speed changed':
                is_speed_change = True

            recommendations = []
            if not solution_list or len(solution_list) < 1:
                # when order takes too much time to solve
                if (int(round(time.time())) - self.millisec_to_sec(p.updated)) > self.conf.solver.solver_timeout:
                    message = _LI("Plan {} is timed out, exceed the expected "
                                  "time {} seconds").format(p.id, self.conf.solver.timeout)

                # when no solution found
                else:
                    message = _LI("Plan {} search failed, no "
                                  "recommendations found by machine {}").format(p.id, p.solver_owner)
                LOG.info(message)
                # Update the plan status
                p.status = self.Plan.NOT_FOUND
                p.message = message

                # Metrics to Prometheus
                m_svc_name = p.template['parameters'].get('service_name', 'N/A')
                PC.VNF_FAILURE.labels('ONAP', m_svc_name).inc()

                while 'FAILURE' in _is_success:
                    _is_success = p.update(condition=self.solver_owner_condition)
                    LOG.info(_LI("Plan serach failed, changing the template status from solving to not found, "
                                 "atomic update response from MUSIC {}").format(_is_success))
            else:
                # Assemble recommendation result JSON
                for solution in solution_list:
                    current_rec = dict()
                    for demand_name in solution:
                        resource = solution[demand_name]

                        if not is_speed_change:
                            is_rehome = "false"
                        else:
                            is_rehome = "false" if resource.get("existing_placement") == 'true' else "true"

                        location_id = "" if resource.get("cloud_region_version") == '2.5' else resource.get("location_id")

                        rec = {
                            # FIXME(shankar) A&AI must not be hardcoded here.
                            # Also, account for more than one Inventory Provider.
                            "inventory_provider": "aai",
                            "service_resource_id":
                                resource.get("service_resource_id"),
                            "candidate": {
                                "candidate_id": resource.get("candidate_id"),
                                "inventory_type": resource.get("inventory_type"),
                                "cloud_owner": resource.get("cloud_owner"),
                                "location_type": resource.get("location_type"),
                                "location_id": location_id,
                                "is_rehome": is_rehome,
                            },
                            "attributes": {
                                "physical-location-id":
                                    resource.get("physical_location_id"),
                                "cloud_owner": resource.get("cloud_owner"),
                                'aic_version': resource.get("cloud_region_version")},
                        }

                        if resource.get('vim-id'):
                            rec["candidate"]['vim-id'] = resource.get('vim-id')

                        if rec["candidate"]["inventory_type"] == "service":
                            rec["attributes"]["host_id"] = resource.get("host_id")
                            rec["attributes"]["service_instance_id"] = resource.get("candidate_id")
                            rec["candidate"]["host_id"] = resource.get("host_id")

                            if resource.get('vlan_key'):
                                rec["attributes"]['vlan_key'] = resource.get('vlan_key')
                            if resource.get('port_key'):
                                rec["attributes"]['port_key'] = resource.get('port_key')

                        if rec["candidate"]["inventory_type"] == "vfmodule":
                            rec["attributes"]["host_id"] = resource.get("host_id")
                            rec["attributes"]["service_instance_id"] = resource.get("service_instance_id")
                            rec["candidate"]["host_id"] = resource.get("host_id")

                            if resource.get('vlan_key'):
                                rec["attributes"]['vlan_key'] = resource.get('vlan_key')
                            if resource.get('port_key'):
                                rec["attributes"]['port_key'] = resource.get('port_key')

                            vf_module_data = rec["attributes"]
                            vf_module_data['nf-name'] = resource.get("nf-name")
                            vf_module_data['nf-id'] = resource.get("nf-id")
                            vf_module_data['nf-type'] = resource.get("nf-type")
                            vf_module_data['vnf-type'] = resource.get("vnf-type")
                            vf_module_data['vf-module-id'] = resource.get("vf-module-id")
                            vf_module_data['vf-module-name'] = resource.get("vf-module-name")
                            vf_module_data['ipv4-oam-address'] = resource.get("ipv4-oam-address")
                            vf_module_data['ipv6-oam-address'] = resource.get("ipv6-oam-address")
                            vf_module_data['vservers'] = resource.get("vservers")

                        elif rec["candidate"]["inventory_type"] == "cloud":
                            if resource.get("all_directives") and resource.get("flavor_map"):
                                rec["attributes"]["directives"] = \
                                    self.set_flavor_in_flavor_directives(
                                        resource.get("flavor_map"), resource.get("all_directives"))

                                # Metrics to Prometheus
                                m_vim_id = resource.get("vim-id")
                                m_hpa_score = resource.get("hpa_score", 0)
                                m_svc_name = p.template['parameters'].get(
                                    'service_name', 'N/A')
                                for vnfc, flavor in resource.get("flavor_map").iteritems():
                                    PC.VNF_COMPUTE_PROFILES.labels('ONAP',
                                                                   m_svc_name,
                                                                   demand_name,
                                                                   vnfc,
                                                                   flavor,
                                                                   m_vim_id).inc()

                                PC.VNF_SCORE.labels('ONAP', m_svc_name,
                                                    demand_name,
                                                    m_hpa_score).inc()

                            if resource.get('conflict_id'):
                                rec["candidate"]["conflict_id"] = resource.get("conflict_id")

                        if resource.get('passthrough_attributes'):
                            for key, value in resource.get('passthrough_attributes').items():
                                if key in rec["attributes"]:
                                    LOG.error('Passthrough attribute {} in demand {} already exist for candidate {}'.
                                              format(key, demand_name, rec['candidate_id']))
                                else:
                                    rec["attributes"][key] = value
                        # TODO(snarayanan): Add total value to recommendations?
                        # msg = "--- total value of decision = {}"
                        # LOG.debug(msg.format(_best_path.total_value))
                        # msg = "--- total cost of decision = {}"
                        # LOG.debug(msg.format(_best_path.total_cost))
                        current_rec[demand_name] = rec

                    recommendations.append(current_rec)

                # Update the plan with the solution
                p.solution = {
                    "recommendations": recommendations
                }

                # multiple spin-ups logic
                '''
                go through list of recommendations in the solution
                for cloud candidates, check if (cloud-region-id + e2evnfkey) is in the order_locks table
                if so, insert the row with status 'parked' in order_locks, changes plan status to 'pending' in plans table (or other status value)
                otherwise, insert the row with status 'locked' in order_locks, and change status to 'solved' in plans table - continue reservation
                '''

                # clean up the data/record in order_locks table, deleting all records that failed from MSO
                order_locks = self.OrderLock.query.all()
                for order_lock_record in order_locks:

                    plans = getattr(order_lock_record, 'plans')
                    for plan_id, plan_attributes in plans.items():
                        plan_dict = json.loads(plan_attributes)

                        if plan_dict.get('status', None) == OrderLock.FAILED:
                            order_lock_record.delete()
                            LOG.info(_LI("The order lock record {} with status {} is deleted (due to failure spinup from MSO) from order_locks table").
                                     format(order_lock_record, plan_dict.get('status')))
                            break

                inserted_order_records_dict = dict()
                available_dependenies_set = set()

                is_inserted_to_order_locks = True
                is_conflict_id_missing = False
                is_order_translated_before_spinup = False

                for solution in solution_list:

                    for demand_name, candidate in solution.items():
                        if candidate.get('inventory_type') == 'cloud':
                            conflict_id = candidate.get('conflict_id')
                            service_resource_id = candidate.get('service_resource_id')
                            # TODO(larry): add more logic for missing conflict_id in template
                            if not conflict_id:
                                is_conflict_id_missing = True
                                break

                            available_dependenies_set.add(conflict_id)
                            # check if conflict_id exists in order_locks table
                            order_lock_record = self.OrderLock.query.get_plan_by_col("id", conflict_id)
                            if order_lock_record:
                                is_spinup_completed = getattr(order_lock_record[0], 'is_spinup_completed')
                                spinup_completed_timestamp = getattr(order_lock_record[0], 'spinup_completed_timestamp')
                                if is_spinup_completed and spinup_completed_timestamp > p.translation_begin_timestamp:
                                    is_order_translated_before_spinup = True
                                    break
                                elif not is_spinup_completed:
                                    inserted_order_records_dict[conflict_id] = service_resource_id

                if is_conflict_id_missing:
                    message = _LE("Missing conflict identifier field for cloud candidates in the template, "
                                  "could not insert into order_locks table")
                    LOG.debug(message)
                    p.status = self.Plan.SOLVED

                elif is_order_translated_before_spinup:
                    message = _LE("Retriggering Plan {} due to the new order arrives before the "
                                  "spinup completion of the old order ").format(p.id)
                    LOG.debug(message)
                    p.rehome_plan()

                elif len(inserted_order_records_dict) > 0:

                    new_dependenies_set = available_dependenies_set - set(inserted_order_records_dict.keys())
                    dependencies = ','.join(str(s) for s in new_dependenies_set)

                    for conflict_id, service_resource_id in inserted_order_records_dict.items():
                        plan = {
                            p.id: {
                                "status": OrderLock.UNDER_SPIN_UP,
                                "created": self.current_time_millis(),
                                "updated": self.current_time_millis(),
                                "service_resource_id": service_resource_id
                            }
                        }

                        if dependencies:
                            plan[p.id]['dependencies'] = dependencies

                        order_lock_row = self.OrderLock(id=conflict_id, plans=plan)
                        response = order_lock_row.insert()

                        # TODO(larry): add more logs for inserting order lock record (insert/update)
                        LOG.info(_LI("Inserting the order lock record to order_locks table in MUSIC, "
                                     "conditional insert operation response from MUSIC {}").format(response))
                        if response and response.status_code == 200:
                            body = response.json()
                            LOG.info("Succcessfully inserted the record in order_locks table with "
                                     "the following response message {}".format(body))
                        else:
                            is_inserted_to_order_locks = False
                else:
                    for solution in solution_list:
                        for demand_name, candidate in solution.items():
                            if candidate.get('inventory_type') == 'cloud':
                                conflict_id = candidate.get('conflict_id')
                                service_resource_id = candidate.get('service_resource_id')

                                order_lock_record = self.OrderLock.query.get_plan_by_col("id", conflict_id)
                                if order_lock_record:
                                    deleting_record = order_lock_record[0]
                                    plans = getattr(deleting_record, 'plans')
                                    is_spinup_completed = getattr(deleting_record, 'is_spinup_completed')
                                    spinup_completed_timestamp = getattr(deleting_record, 'spinup_completed_timestamp')

                                    if is_spinup_completed:
                                        # persist the record in order_locks_history table
                                        order_lock_history_record = self.OrderLockHistory(conflict_id=conflict_id, plans=plans,
                                                                                          is_spinup_completed=is_spinup_completed,
                                                                                          spinup_completed_timestamp=spinup_completed_timestamp)
                                        LOG.debug("Inserting the history record with conflict id {} to order_locks_history table".format(conflict_id))
                                        order_lock_history_record.insert()
                                        # remove the older record
                                        LOG.debug("Deleting the order lock record {} from order_locks table".format(deleting_record))
                                        deleting_record.delete()

                                plan = {
                                    p.id: {
                                        "status": OrderLock.UNDER_SPIN_UP,
                                        "created": self.current_time_millis(),
                                        "updated": self.current_time_millis(),
                                        "service_resource_id": service_resource_id
                                    }
                                }
                                order_lock_row = self.OrderLock(id=conflict_id, plans=plan)
                                response = order_lock_row.insert()
                                # TODO(larry): add more logs for inserting order lock record (insert/update)
                                LOG.info(_LI("Inserting the order lock record to order_locks table in MUSIC, "
                                             "conditional insert operation response from MUSIC {}").format(response))
                                if response and response.status_code == 200:
                                    body = response.json()
                                    LOG.info("Succcessfully inserted the record in order_locks table "
                                             "with the following response message {}".format(body))
                                else:
                                    is_inserted_to_order_locks = False

                if not is_inserted_to_order_locks:
                    message = _LE("Plan {} status encountered an "
                                  "error while inserting order lock message to MUSIC.").format(p.id)
                    LOG.error(message)
                    p.status = self.Plan.ERROR
                    p.message = message

                elif p.status == self.Plan.SOLVING:
                    if len(inserted_order_records_dict) > 0:
                        LOG.info(_LI("The plan with id {} is parked in order_locks table, waiting for MSO release calls").
                                 format(p.id))
                        p.status = self.Plan.WAITING_SPINUP
                    else:
                        LOG.info(_LI("The plan with id {} is inserted in order_locks table.").
                                 format(p.id))
                        p.status = self.Plan.SOLVED

            while 'FAILURE' in _is_success and (self.current_time_seconds() - self.millisec_to_sec(p.updated)) <= self.conf.solver.timeout:
                _is_success = p.update(condition=self.solver_owner_condition)
                LOG.info(_LI("Plan search complete, changing the template status from solving to {}, "
                                 "atomic update response from MUSIC {}").format(p.status, _is_success))

            LOG.info(_LI("Plan {} search complete, {} solution(s) found by machine {}").
                     format(p.id, len(solution_list), p.solver_owner))
            LOG.debug("Plan {} detailed solution: {}".
                      format(p.id, p.solution))
            LOG.info("Plan name: {}".format(p.name))

    def terminate(self):
        """Terminate"""
        LOG.debug("%s" % self.__class__.__name__)
        self.running = False
        self._gracefully_stop()
        super(SolverService, self).terminate()

    def reload(self):
        """Reload"""
        LOG.debug("%s" % self.__class__.__name__)
        self._restart()

    def current_time_millis(self):
        """Current time in milliseconds."""
        return int(round(time.time() * 1000))

    def set_flavor_in_flavor_directives(self, flavor_map, directives):
        '''
        Insert the flavor name inside the flavor_map into flavor_directives
        :param flavor_map: flavor map get
        :param directives: All the directives get from request
        '''
        keys = list(flavor_map.keys())     # Python 3 Conversion -- dict object to list object
        for ele in directives.get("directives"):
            for item in ele.get("directives"):
                if "flavor_directives" in item.get("type"):
                    for attr in item.get("attributes"):
                        attr["attribute_value"] = flavor_map.get(attr["attribute_name"]) \
                            if attr.get("attribute_name") in keys else ""
        return directives
