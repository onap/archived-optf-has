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

# from conductor.common.models import plan
# from conductor.common.music import api
from conductor.common.music import messaging as music_messaging
# from conductor.common.music.model import base
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

# class ModelHook(hooks.PecanHook):
#     """Create and attach dynamic model classes to the request."""
#
#     def __init__(self, conf):
#         super(ModelHook, self).__init__()
#
#         # TODO(jdandrea) Move this to DBHook?
#         music = api.API()
#         music.keyspace_create(keyspace=conf.keyspace)
#
#         # Dynamically create a plan class for the specified keyspace
#         self.Plan = base.create_dynamic_model(
#             keyspace=conf.keyspace, baseclass=plan.Plan, classname="Plan")
#
#     def before(self, state):
#         state.request.models = {
#             "Plan": self.Plan,
#         }


# class DBHook(hooks.PecanHook):
#
#     def __init__(self):
#         self.storage_connection = DBHook.get_connection('metering')
#         self.event_storage_connection = DBHook.get_connection('event')
#
#         if (not self.storage_connection
#            and not self.event_storage_connection):
#             raise Exception("API failed to start. Failed to connect to "
#                             "databases, purpose:  %s" %
#                             ', '.join(['metering', 'event']))
#
#     def before(self, state):
#         state.request.storage_conn = self.storage_connection
#         state.request.event_storage_conn = self.event_storage_connection
#
#     @staticmethod
#     def get_connection(purpose):
#         try:
#             return storage.get_connection_from_config(cfg.CONF, purpose)
#         except Exception as err:
#             params = {"purpose": purpose, "err": err}
#             LOG.exception(_LE("Failed to connect to db, purpose %(purpose)s "
#                               "retry later: %(err)s") % params)
#
#
# class NotifierHook(hooks.PecanHook):
#     """Create and attach a notifier to the request.
#     Usually, samples will be push to notification bus by notifier when they
#     are posted via /v2/meters/ API.
#     """
#
#     def __init__(self):
#         transport = messaging.get_transport()
#         self.notifier = oslo_messaging.Notifier(
#             transport, driver=cfg.CONF.publisher_notifier.homing_driver,
#             publisher_id="conductor.api")
#
#     def before(self, state):
#         state.request.notifier = self.notifier
#
#
# class TranslationHook(hooks.PecanHook):
#
#     def after(self, state):
#         # After a request has been done, we need to see if
#         # ClientSideError has added an error onto the response.
#         # If it has we need to get it info the thread-safe WSGI
#         # environ to be used by the ParsableErrorMiddleware.
#         if hasattr(state.response, 'translatable_error'):
#             state.request.environ['translatable_error'] = (
#                 state.response.translatable_error)
