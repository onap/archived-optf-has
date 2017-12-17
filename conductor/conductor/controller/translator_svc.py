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

import time

import cotyledon
import futurist
from oslo_config import cfg
from oslo_log import log

from conductor.common.music import api
from conductor.common.music import messaging as music_messaging
from conductor.controller import translator
from conductor.i18n import _LE, _LI
from conductor import messaging

LOG = log.getLogger(__name__)

CONF = cfg.CONF

CONTROLLER_OPTS = [
    cfg.IntOpt('polling_interval',
               default=1,
               min=1,
               help='Time between checking for new plans. '
                    'Default value is 1.'),
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
        LOG.debug("%s" % self.__class__.__name__)
        super(TranslatorService, self).__init__(worker_id)
        self._init(conf, **kwargs)
        self.running = True

    def _init(self, conf, **kwargs):
        self.conf = conf
        self.Plan = kwargs.get('plan_class')
        self.kwargs = kwargs

        # Set up the RPC service(s) we want to talk to.
        self.data_service = self.setup_rpc(conf, "data")

        # Set up Music access.
        self.music = api.API()

    def _gracefully_stop(self):
        """Gracefully stop working on things"""
        pass

    def _restart(self):
        """Prepare to restart the service"""
        pass

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
            trns = translator.Translator(
                self.conf, plan.name, plan.id, plan.template)
            trns.translate()
            if trns.ok:
                plan.translation = trns.translation
                plan.status = self.Plan.TRANSLATED
                LOG.info(_LI(
                    "Plan {} translated. Ready for solving").format(
                    plan.id))
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

        plan.update()

    def __check_for_templates(self):
        """Wait for the polling interval, then do the real template check."""

        # Wait for at least poll_interval sec
        polling_interval = self.conf.controller.polling_interval
        time.sleep(polling_interval)

        # Look for plans with the status set to TEMPLATE
        plans = self.Plan.query.all()
        for plan in plans:
            # If there's a template to be translated, do it!
            if plan.status == self.Plan.TEMPLATE:
                self.translate(plan)
                break
            elif plan.timedout:
                # Move plan to error status? Create a new timed-out status?
                # todo(snarayanan)
                continue

    def run(self):
        """Run"""
        LOG.debug("%s" % self.__class__.__name__)

        # Look for templates to translate from within a thread
        executor = futurist.ThreadPoolExecutor()
        while self.running:
            fut = executor.submit(self.__check_for_templates)
            fut.result()
        executor.shutdown()

    def terminate(self):
        """Terminate"""
        LOG.debug("%s" % self.__class__.__name__)
        self.running = False
        self._gracefully_stop()
        super(TranslatorService, self).terminate()

    def reload(self):
        """Reload"""
        LOG.debug("%s" % self.__class__.__name__)
        self._restart()
