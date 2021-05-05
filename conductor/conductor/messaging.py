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

from oslo_config import cfg

from conductor.common import db_backend
from conductor.common.music.messaging import component

DEFAULT_URL = "__default__"
TRANSPORTS = {}

CONF = cfg.CONF

# Pull in messaging server opts. We use them here.
MESSAGING_SERVER_OPTS = component.MESSAGING_SERVER_OPTS
CONF.register_opts(MESSAGING_SERVER_OPTS, group='messaging_server')


def setup():
    """Messaging setup, if any"""
    # oslo_messaging.set_transport_defaults('conductor')
    pass


# TODO(jdandrea): Remove Music-specific aspects (keyspace -> namespace?)
# TODO(jdandrea): Make Music an oslo rpc backend (difficulty level: high?)
def get_transport(conf, url=None, optional=False, cache=True):
    """Initialise the Music messaging layer."""
    global TRANSPORTS
    cache_key = url or DEFAULT_URL
    transport = TRANSPORTS.get(cache_key)

    if not transport or not cache:
        try:
            # "Somebody set up us the API." ;)
            # Yes, we know an API is not a transport. Cognitive dissonance FTW!
            # TODO(jdandrea): try/except to catch problems
            keyspace = conf.messaging_server.keyspace
            transport = db_backend.get_client()
            transport.keyspace_create(keyspace=keyspace)
        except Exception:
            if not optional or url:
                # NOTE(sileht): oslo_messaging is configured but unloadable
                # so reraise the exception
                raise
            return None
        else:
            if cache:
                TRANSPORTS[cache_key] = transport
    return transport


def cleanup():
    """Cleanup the Music messaging layer."""
    global TRANSPORTS
    for url in TRANSPORTS:
        del TRANSPORTS[url]
