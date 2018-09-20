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

from oslo_log import log
from pecan import secure

from conductor.api.controllers import error
from conductor.api.controllers.v1 import plans
from conductor.api.controllers.v1 import release_orders
from conductor.api.controllers.v1 import latency_reduction_loader
from conductor.api.controllers.v1 import latency_country_rules_loader
from conductor.api.controllers.v1 import triage
from conductor.i18n import _
import pecan


LOG = log.getLogger(__name__)


class V1Controller(secure.SecureController):
    """Version 1 API controller root."""

    plans = plans.PlansController()
    triage_tool = triage.TriageController()
    load_latency_rules = latency_reduction_loader.LatencyLoaderController()
    load_latency_country_rules = latency_country_rules_loader.LatencyCountryRulesLoaderController()

    @classmethod
    def check_permissions(cls):
        """SecureController permission check callback"""
        return True
        # error('/errors/unauthorized', msg)

    @pecan.expose(generic=True, template='json')
    def index(self):
        """Catchall for unallowed methods"""
        message = _('The %s method is not allowed.') % pecan.request.method
        kwargs = {}
        error('/errors/not_allowed', message, **kwargs)

#TODO(larry): understand pecan and change the following code
pecan.route(V1Controller, 'release-orders', release_orders.LocksController())
