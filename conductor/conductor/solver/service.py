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

import socket
import time

import cotyledon
from conductor import messaging
from conductor import service
from conductor.common.models import plan
from conductor.common.music import api
from conductor.common.music import messaging as music_messaging
from conductor.common.music.model import base
from conductor.i18n import _LE, _LI
from conductor.solver.optimizer import optimizer
from conductor.solver.request import parser
from conductor.solver.utils import constraint_engine_interface as cei
from oslo_config import cfg
from oslo_log import log

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

        if not self.Plan:
            raise

    def run(self):
        kwargs = {'plan_class': self.Plan}
        svcmgr = cotyledon.ServiceManager()
        svcmgr.add(SolverService,
                   workers=self.conf.solver.workers,
                   args=(self.conf,), kwargs=kwargs)
        svcmgr.run()


class SolverService(cotyledon.Service):
    """Solver service."""

    # This will appear in 'ps xaf'
    name = "Conductor Solver"

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
        plans = self.Plan.query.all()
        for the_plan in plans:
            if the_plan.status == self.Plan.SOLVING:
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
            plans = self.Plan.query.all()
            found_translated_template = False
            for p in plans:
                if p.status == self.Plan.TRANSLATED:
                    json_template = p.translation
                    found_translated_template = True
                    break
                elif p.status == self.Plan.SOLVING and \
                                (self.current_time_seconds() - self.millisec_to_sec(
                                    p.updated)) > self.conf.solver.timeout:
                    p.status = self.Plan.TRANSLATED
                    p.update(condition=self.solving_status_condition)
                    break
            if found_translated_template and not json_template:
                message = _LE("Plan {} status is translated, yet "
                              "the translation wasn't found").format(p.id)
                LOG.error(message)
                p.status = self.Plan.ERROR
                p.message = message
                p.update(condition=self.translated_status_condition)
                continue
            elif found_translated_template and p and p.solver_counter >= self.conf.solver.max_solver_counter:
                message = _LE("Tried {} times. Plan {} is unable to solve") \
                    .format(self.conf.solver.max_solver_counter, p.id)
                LOG.error(message)
                p.status = self.Plan.ERROR
                p.message = message
                p.update(condition=self.translated_status_condition)
                continue
            elif not json_template:
                continue

            p.status = self.Plan.SOLVING

            p.solver_counter += 1
            p.solver_owner = socket.gethostname()

            _is_updated = p.update(condition=self.translated_status_condition)
            # other VMs have updated the status and start solving the plan
            if 'FAILURE' in _is_updated:
                continue

            LOG.info(_LI("Plan {} with request id {} is solving by machine {}. Tried to solve it for {} times.").
                     format(p.id, p.name, p.solver_owner, p.solver_counter))

            _is_success = 'FAILURE | Could not acquire lock'

            request = parser.Parser()
            request.cei = self.cei
            try:
                request.parse_template(json_template)
                request.assgin_constraints_to_demands()
                requests_to_solve[p.id] = request
                opt = optimizer.Optimizer(self.conf, _requests=requests_to_solve, _begin_time=self.millisec_to_sec(p.updated))
                solution = opt.get_solution()

            except Exception as err:
                message = _LE("Plan {} status encountered a "
                              "parsing error: {}").format(p.id, err.message)
                LOG.error(message)
                p.status = self.Plan.ERROR
                p.message = message
                while 'FAILURE | Could not acquire lock' in _is_success:
                    _is_success = p.update(condition=self.solver_owner_condition)
                continue

            recommendations = []
            if not solution or not solution.decisions:
                if (int(round(time.time())) - self.millisec_to_sec(p.updated)) > self.conf.solver.solver_timeout:
                    message = _LI("Plan {} is timed out, exceed the expected "
                                  "time {} seconds").format(p.id, self.conf.solver.timeout)

                else:
                    message = _LI("Plan {} search failed, no "
                                  "recommendations found by machine {}").format(p.id, p.solver_owner)
                LOG.info(message)
                # Update the plan status
                p.status = self.Plan.NOT_FOUND
                p.message = message
                while 'FAILURE | Could not acquire lock' in _is_success:
                    _is_success = p.update(condition=self.solver_owner_condition)
            else:
                # Assemble recommendation result JSON
                for demand_name in solution.decisions:
                    resource = solution.decisions[demand_name]
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
                            "vim-id": resource.get("vim-id"),
                        },
                        "attributes": {
                            "physical-location-id":
                                resource.get("physical_location_id"),
                            "cloud_owner": resource.get("cloud_owner"),
                            'aic_version': resource.get("cloud_region_version")},
                    }
                    if rec["candidate"]["inventory_type"] == "service":
                        rec["attributes"]["host_id"] = resource.get("host_id")
                        rec["candidate"]["host_id"] = resource.get("host_id")

                    if rec["candidate"]["inventory_type"] == "cloud":
                        if resource.get("all_directives") and resource.get("flavor_map"):
                            rec["attributes"]["directives"] = self.set_flavor(resource.get("flavor_map"), resource.get(
                                "all_directives"))
                    # TODO(snarayanan): Add total value to recommendations?
                    # msg = "--- total value of decision = {}"
                    # LOG.debug(msg.format(_best_path.total_value))
                    # msg = "--- total cost of decision = {}"
                    # LOG.debug(msg.format(_best_path.total_cost))

                    recommendations.append({demand_name: rec})

                # Update the plan with the solution
                p.solution = {
                    "recommendations": recommendations
                }
                p.status = self.Plan.SOLVED
                while 'FAILURE | Could not acquire lock' in _is_success:
                    _is_success = p.update(condition=self.solver_owner_condition)
            LOG.info(_LI("Plan {} search complete, solution with {} "
                         "recommendations found by machine {}").
                     format(p.id, len(recommendations), p.solver_owner))
            LOG.debug("Plan {} detailed solution: {}".
                      format(p.id, p.solution))
            LOG.info("Plan name: {}".
                      format(p.name))

            # Check status, update plan with response, SOLVED or ERROR

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

    def set_flavor(self, flavor_map, directives):
        flavor_label = flavor_map.keys()
        for ele in directives.get("directives"):
            for item in ele.get("directives"):
                if "flavor_directives" in item.get("type"):
                    for attr in item.get("attributes"):
                        attr["attribute_value"] = flavor_map.get(attr["attribute_name"]) \
                            if attr.get("attribute_name") in flavor_label else ""
        return directives
