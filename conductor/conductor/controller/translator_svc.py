#
# -------------------------------------------------------------------------
#   Copyright (c) 2015-2017 AT&T Intellectual Property
#   Copyright (C) 2020 Wipro Limited.
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
import futurist
from oslo_config import cfg
from oslo_log import log

from conductor.common.config_loader import load_config_file
from conductor.common import db_backend
from conductor.common.music import messaging as music_messaging
from conductor.common.utils import conductor_logging_util as log_util
from conductor.controller.generic_objective_translator import GenericObjectiveTranslator
from conductor.controller.translator import Translator
from conductor.controller.translator_utils import TranslatorException
from conductor.controller.translator_utils import VERSIONS
from conductor.i18n import _LE
from conductor.i18n import _LI
from conductor import messaging


LOG = log.getLogger(__name__)

CONF = cfg.CONF

CONTROLLER_OPTS = [
    cfg.IntOpt('polling_interval',
               default=1,
               min=1,
               help='Time between checking for new plans. '
                    'Default value is 1.'),
    cfg.IntOpt('max_translation_counter',
               default=1,
               min=1),
    cfg.StrOpt('opt_schema_file',
               default='opt_schema.json',
               help='json schema file which will be used to validate the '
                    'optimization object for the new template version'),
]

CONF.register_opts(CONTROLLER_OPTS, group='controller')


class TranslatorService(cotyledon.Service):
    """Template Translator service.

    This service looks for untranslated templates and
    preps them for solving by the Solver service.
    """

    # This will appear in 'ps xaf'
    name = "Template Translator"

    def __init__(self, worker_id, conf, **kwargs):
        """Initializer"""
        LOG.debug("{}".format(self.__class__.__name__))
        super(TranslatorService, self).__init__(worker_id)
        self._init(conf, **kwargs)
        self.running = True

    def _init(self, conf, **kwargs):
        self.conf = conf
        self.Plan = kwargs.get('plan_class')
        self.kwargs = kwargs
        self.opt_schema = load_config_file(str(self.conf.controller.opt_schema_file))

        # Set up the RPC service(s) we want to talk to.
        self.data_service = self.setup_rpc(conf, "data")

        # Set up Music access.
        self.music = db_backend.get_client()

        self.translation_owner_condition = {
            "translation_owner": socket.gethostname()
        }

        self.template_status_condition = {
            "status": self.Plan.TEMPLATE
        }

        self.translating_status_condition = {
            "status": self.Plan.TRANSLATING
        }

        if not self.conf.controller.concurrent:
            self._reset_template_status()

    def _gracefully_stop(self):
        """Gracefully stop working on things"""
        pass

    def millisec_to_sec(self, millisec):
        """Convert milliseconds to seconds"""
        return millisec / 1000

    def _reset_template_status(self):
        """Reset plans being templated so they are translated again.

        Use this only when the translator service is not running concurrently.
        """
        plans = self.Plan.query.get_plan_by_col("status", self.Plan.TRANSLATING)
        for the_plan in plans:
            the_plan.status = self.Plan.TEMPLATE
            # Use only in active-passive mode, so don't have to be atomic
            the_plan.update()

    def _restart(self):
        """Prepare to restart the service"""
        pass

    def current_time_seconds(self):
        """Current time in milliseconds."""
        return int(round(time.time()))

    def setup_rpc(self, conf, topic):
        """Set up the RPC Client"""
        # TODO(jdandrea): Put this pattern inside music_messaging?
        transport = messaging.get_transport(conf=conf)
        target = music_messaging.Target(topic=topic)
        client = music_messaging.RPCClient(conf=conf,
                                           transport=transport,
                                           target=target)
        return client

    def translate(self, plan):
        """Translate the plan to a format the solver can use"""
        # Update the translation field and set status to TRANSLATED.
        try:
            LOG.info(_LI("Requesting plan {} translation").format(
                plan.id))
            template_version = plan.template.get("homing_template_version")
            if template_version in VERSIONS['BASE']:
                trns = Translator(self.conf, plan.name, plan.id, plan.template)
            elif template_version in VERSIONS['GENERIC']:
                trns = GenericObjectiveTranslator(self.conf, plan.name, plan.id, plan.template, self.opt_schema)
            else:
                raise TranslatorException(
                    "conductor_template_version must be one "
                    "of: {}".format(', '.join([x for v in VERSIONS.values() for x in v])))

            trns.translate()

            if trns.ok:
                plan.translation = trns.translation
                plan.status = self.Plan.TRANSLATED
                LOG.info(_LI(
                    "Plan {} translated. Ready for solving").format(
                    plan.id))
                LOG.info(_LI(
                    "Plan name: {}").format(
                    plan.name))
            else:
                plan.message = trns.error_message
                plan.status = self.Plan.ERROR
                LOG.error(_LE(
                    "Plan {} translation error encountered").format(
                    plan.id))

        except Exception as ex:
            template = "An exception of type {0} occurred, arguments:\n{1!r}"
            plan.message = template.format(type(ex).__name__, ex.args)
            plan.status = self.Plan.ERROR

        _is_success = 'FAILURE'
        while 'FAILURE' in _is_success and (self.current_time_seconds() - self.millisec_to_sec(plan.updated)) \
                <= self.conf.messaging_server.timeout:
            _is_success = plan.update(condition=self.translation_owner_condition)
            LOG.info(_LI("Changing the template status from translating to {}, "
                         "atomic update response from MUSIC {}").format(plan.status, _is_success))

    def __check_for_templates(self):
        """Wait for the polling interval, then do the real template check."""

        # Wait for at least poll_interval sec
        polling_interval = self.conf.controller.polling_interval
        time.sleep(polling_interval)
        # Look for plans with the status set to TEMPLATE

        # Instead of using the query.all() method, now creating an index for 'status'
        # field in conductor.plans table, and query plans by status columns
        template_plans = self.Plan.query.get_plan_by_col("status", self.Plan.TEMPLATE)
        translating_plans = self.Plan.query.get_plan_by_col("status", self.Plan.TRANSLATING)

        # combine the plans with status = 'template' and 'translating' together
        plans = template_plans + translating_plans

        for plan in plans:
            # If there's a template to be translated, do it!
            if plan.status == self.Plan.TEMPLATE:
                if plan.translation_counter >= self.conf.controller.max_translation_counter:
                    message = _LE("Tried {} times. Plan {} is unable to translate") \
                        .format(self.conf.controller.max_translation_counter, plan.id)
                    plan.message = message
                    plan.status = self.Plan.ERROR
                    plan.update(condition=self.template_status_condition)
                    LOG.error(message)
                    break
                else:
                    # change the plan status to "translating" and assign the current machine as translation owner
                    plan.status = self.Plan.TRANSLATING
                    plan.translation_counter += 1
                    plan.translation_owner = socket.gethostname()
                    plan.translation_begin_timestamp = int(round(time.time() * 1000))
                    _is_updated = plan.update(condition=self.template_status_condition)
                    log_util.setLoggerFilter(LOG, self.conf.keyspace, plan.id)
                    LOG.info(_LE("Plan {} is trying to update the status from 'template' to 'translating',"
                                 " get {} response from MUSIC").format(plan.id, _is_updated))
                    if not _is_updated:
                        break

                    if _is_updated and 'SUCCESS' in _is_updated:
                        self.translate(plan)
                break

            # TODO(larry): sychronized clock among Conducotr VMs, or use an offset
            elif plan.status == self.Plan.TRANSLATING and (self.current_time_seconds()
                                                           - self.millisec_to_sec(plan.updated)) \
                    > self.conf.messaging_server.timeout:
                plan.status = self.Plan.TEMPLATE
                plan.update(condition=self.translating_status_condition)
                break

            elif plan.timedout:
                # TODO(jdandrea): How to tell all involved to stop working?
                # Not enough to just set status.
                continue

    def run(self):
        """Run"""
        LOG.debug("{}".format(self.__class__.__name__))
        # Look for templates to translate from within a thread
        executor = futurist.ThreadPoolExecutor()

        while self.running:
            fut = executor.submit(self.__check_for_templates)
            fut.result()
        executor.shutdown()

    def terminate(self):
        """Terminate"""
        LOG.debug("{}".format(self.__class__.__name__))
        self.running = False
        self._gracefully_stop()
        super(TranslatorService, self).terminate()

    def reload(self):
        """Reload"""
        LOG.debug("{}".format(self.__class__.__name__))
        self._restart()
