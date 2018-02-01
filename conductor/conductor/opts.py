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

import itertools

import conductor.api.app
import conductor.common.music.api
import conductor.common.music.messaging.component
import conductor.conf.inventory_provider
import conductor.conf.service_controller
import conductor.controller.service
import conductor.controller.translator_svc
import conductor.data.plugins.inventory_provider.aai
import conductor.data.plugins.service_controller.sdnc
import conductor.reservation.service
import conductor.service
import conductor.solver.service


def list_opts():
    return [
        ('DEFAULT', itertools.chain(
            conductor.api.app.OPTS,
            conductor.service.OPTS)),
        ('api', conductor.api.app.API_OPTS),
        ('controller', itertools.chain(
            conductor.controller.service.CONTROLLER_OPTS,
            conductor.controller.translator_svc.CONTROLLER_OPTS)),
        # ('data', conductor.data.plugins.inventory_provider.aai.DATA_OPTS),
        ('inventory_provider', itertools.chain(
            conductor.conf.inventory_provider.
            INV_PROVIDER_EXT_MANAGER_OPTS)),
        ('aai', conductor.data.plugins.inventory_provider.aai.AAI_OPTS),
        ('service_controller', itertools.chain(
            conductor.conf.service_controller.
            SVC_CONTROLLER_EXT_MANAGER_OPTS)),
        ('sdnc', conductor.data.plugins.service_controller.sdnc.SDNC_OPTS),
        ('messaging_server',
         conductor.common.music.messaging.component.MESSAGING_SERVER_OPTS),
        ('music_api', conductor.common.music.api.MUSIC_API_OPTS),
        ('solver', conductor.solver.service.SOLVER_OPTS),
        ('reservation', conductor.reservation.service.reservation_OPTS),
    ]
