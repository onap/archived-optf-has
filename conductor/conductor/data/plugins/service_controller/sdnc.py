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

from oslo_config import cfg
from oslo_log import log

from conductor.common import rest
from conductor.common.utils import cipherUtils
from conductor.data.plugins.service_controller import base
from conductor.i18n import _LE

LOG = log.getLogger(__name__)

CONF = cfg.CONF

SDNC_OPTS = [
    cfg.IntOpt('cache_refresh_interval',
               default=1440,
               help='Interval with which to refresh the local cache, '
                    'in minutes.'),
    cfg.StrOpt('table_prefix',
               default='sdnc',
               help='Data Store table prefix.'),
    cfg.StrOpt('server_url',
               default='https://controller:8443/restconf/',
               help='Base URL for SDN-C, up to and including the version.'),
    cfg.StrOpt('username',
               help='Basic Authentication Username'),
    cfg.StrOpt('password',
               help='Basic Authentication Password'),
    cfg.StrOpt('sdnc_rest_timeout',
               default='30',
               help='Timeout for SDNC Rest Call'),
    cfg.StrOpt('sdnc_retries',
               default='3',
               help='Retry Numbers for SDNC Rest Call'),
]

CONF.register_opts(SDNC_OPTS, group='sdnc')


class SDNC(base.ServiceControllerBase):
    """SDN Service Controller"""

    def __init__(self):
        """Initializer"""

        # FIXME(jdandrea): Pass this in to init.
        self.conf = CONF

        self.base = self.conf.sdnc.server_url.rstrip('/')
        self.password = cipherUtils.AESCipher.get_instance().decrypt(self.conf.sdnc.password)
        self.timeout = self.conf.sdnc.sdnc_rest_timeout
        self.verify = False
        self.retries = self.conf.sdnc.sdnc_retries
        self.username = self.conf.sdnc.username

        kwargs = {
            "server_url": self.base,
            "retries": self.retries,
            "username": self.username,
            "password": self.password,
            "log_debug": self.conf.debug,
            "read_timeout": self.timeout,
        }
        self.rest = rest.REST(**kwargs)

        # Not sure what info from SDNC is cacheable
        self._sdnc_cache = {}

    def initialize(self):
        """Perform any late initialization."""
        # self.filter_candidates([])
        pass

    def name(self):
        """Return human-readable name."""
        return "SDN-C"

    def _request(self, method='get', path='/', data=None,
                 context=None, value=None):
        """Performs HTTP request."""
        kwargs = {
            "method": method,
            "path": path,
            "data": data,
        }

        # TODO(jdandrea): Move timing/response logging into the rest helper?
        start_time = time.time()
        response = self.rest.request(**kwargs)
        elapsed = time.time() - start_time
        LOG.debug("Total time for SDN-C request "
                  "({0:}: {1:}): {2:.3f} sec".format(context, value, elapsed))

        if response is None:
            LOG.error(_LE("No response from SDN-C ({}: {})").
                      format(context, value))
            raise Exception('SDN-C query {} timed out'.format(path))
        elif response.status_code != 200:
            LOG.error(_LE("SDN-C request ({}: {}) returned HTTP "
                          "status {} {}, link: {}{}").
                      format(context, value,
                             response.status_code, response.reason,
                             self.base, path))
        return response

    def reserve_candidates(self, candidate_list, request):
        try:
            LOG.debug("Request to reservation {} ".format(request))
            return candidate_list

        except Exception as exc:
            LOG.error("Reservation error: {}".
                      format(exc))
            return

    def filter_candidates(self, request, candidate_list,
                          constraint_name, constraint_type, request_type):
        """Reduce candidate list based on SDN-C intelligence"""
        selected_candidates = []
        return selected_candidates
