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
import stevedore

from conductor.conf import service_controller
from conductor.i18n import _LI

LOG = log.getLogger(__name__)

service_controller.register_extension_manager_opts()


class Manager(stevedore.named.NamedExtensionManager):
    """Manage Service Controller extensions."""

    def __init__(self, conf, namespace):
        super(Manager, self).__init__(
            namespace, conf.service_controller.extensions,
            invoke_on_load=True, name_order=True)
        LOG.info(_LI("Loaded service controller extensions: %s"), self.names())

    def initialize(self):
        """Initialize enabled service controller extensions."""
        for extension in self.extensions:
            LOG.info(_LI("Initializing service controller extension '%s'"),
                     extension.name)
            extension.obj.initialize()
