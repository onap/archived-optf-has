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

import cotyledon

from conductor.common import db_backend
from conductor.common.models import order_lock
from conductor.common.models import plan
from conductor.common.music import messaging as music_messaging
from conductor.common.music.model import base
from conductor.controller import rpc
from conductor.controller import translator_svc
from conductor import messaging
from conductor import service
from oslo_config import cfg
from oslo_log import log

LOG = log.getLogger(__name__)

CONF = cfg.CONF

CONTROLLER_OPTS = [
    cfg.IntOpt('timeout',
               default=10,
               min=1,
               help='Timeout for planning requests. '
                    'Default value is 10.'),
    cfg.IntOpt('limit',
               default=1,
               min=1,
               help='Maximum number of result sets to return. '
                    'Default value is 1.'),
    cfg.IntOpt('workers',
               default=1,
               min=1,
               help='Number of workers for controller service. '
                    'Default value is 1.'),
    cfg.BoolOpt('concurrent',
                default=False,
                help='Set to True when controller will run in active-active '
                     'mode. When set to False, controller will flush any '
                     'abandoned messages at startup. The controller always '
                     'restarts abandoned template translations at startup.'),
]

CONF.register_opts(CONTROLLER_OPTS, group='controller')

# Pull in service opts. We use them here.
OPTS = service.OPTS
CONF.register_opts(OPTS)


class ControllerServiceLauncher(object):
    """Launcher for the controller service."""
    def __init__(self, conf):
        self.conf = conf

        # Set up Music access.
        self.music = db_backend.get_client()
        self.music.keyspace_create(keyspace=conf.keyspace)

        # Dynamically create a plan class for the specified keyspace
        self.Plan = base.create_dynamic_model(
            keyspace=conf.keyspace, baseclass=plan.Plan, classname="Plan")
        self.OrderLock = base.create_dynamic_model(
            keyspace=conf.keyspace, baseclass=order_lock.OrderLock, classname="OrderLock")

        if not self.Plan:
            raise
        if not self.OrderLock:
            raise

    def run(self):
        transport = messaging.get_transport(self.conf)
        if transport:
            topic = "controller"
            target = music_messaging.Target(topic=topic)
            endpoints = [rpc.ControllerRPCEndpoint(self.conf, self.Plan), ]
            flush = not self.conf.controller.concurrent
            kwargs = {'transport': transport,
                      'target': target,
                      'endpoints': endpoints,
                      'flush': flush, }
            svcmgr = cotyledon.ServiceManager()
            svcmgr.add(music_messaging.RPCService,
                       workers=self.conf.controller.workers,
                       args=(self.conf,), kwargs=kwargs)

            kwargs = {'plan_class': self.Plan,
                      'order_locks': self.OrderLock}
            svcmgr.add(translator_svc.TranslatorService,
                       workers=self.conf.controller.workers,
                       args=(self.conf,), kwargs=kwargs)
            svcmgr.run()
