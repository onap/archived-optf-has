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
from pecan import hooks

from conductor.common.music import messaging as music_messaging
from conductor import messaging

LOG = log.getLogger(__name__)


class ConfigHook(hooks.PecanHook):
    """Attach the configuration object to the request.

    That allows controllers to get it.
    """

    def __init__(self, conf):
        super(ConfigHook, self).__init__()
        self.conf = conf

    def on_route(self, state):
        state.request.cfg = self.conf


class MessagingHook(hooks.PecanHook):
    """Create and attach a controller RPC client to the request."""

    def __init__(self, conf):
        super(MessagingHook, self).__init__()
        topic = "controller"
        transport = messaging.get_transport(conf=conf)
        target = music_messaging.Target(topic=topic)
        self.controller = \
            music_messaging.RPCClient(conf=conf,
                                      transport=transport,
                                      target=target)

    def on_route(self, state):
        state.request.controller = self.controller


# NOTE: We no longer use ModelHook, since the API should be asking
# the controller (via RPC) for info about plans, not requesting them directly.