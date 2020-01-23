#
# -------------------------------------------------------------------------
#   Copyright (c) 2018 Intel Corporation Intellectual Property
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

'''Multicloud Vim controller plugin'''

import time
import uuid

from conductor.common import rest
from conductor.data.plugins.vim_controller import base
from conductor.i18n import _LE, _LI
from oslo_config import cfg
from oslo_log import log

LOG = log.getLogger(__name__)

CONF = cfg.CONF

MULTICLOUD_OPTS = [
    cfg.StrOpt('server_url',
               default='http://msb.onap.org/api/multicloud',
               help='Base URL for Multicloud without a trailing slash.'),
    cfg.StrOpt('multicloud_rest_timeout',
               default='30',
               help='Timeout for Multicloud Rest Call'),
    cfg.StrOpt('multicloud_retries',
               default='3',
               help='Number of retry for Multicloud Rest Call'),
    cfg.StrOpt('server_url_version',
               default='v0',
               help='The version of Multicloud API.'),
    cfg.StrOpt('certificate_authority_bundle_file',
               default='certificate_authority_bundle.pem',
               help='Certificate Authority Bundle file in pem format. '
                    'Must contain the appropriate trust chain for the '
                    'Certificate file.'),
    cfg.BoolOpt('enable_https_mode', default = False, help='enable HTTPs mode for multicloud connection'),
]

CONF.register_opts(MULTICLOUD_OPTS, group='multicloud')


class MULTICLOUD(base.VimControllerBase):
    """Multicloud Vim controller"""

    def __init__(self):
        """Initializer"""
        self.conf = CONF
        self.base = self.conf.multicloud.server_url.rstrip('/')
        self.version = self.conf.multicloud.server_url_version.rstrip('/')
        self.timeout = self.conf.multicloud.multicloud_rest_timeout
        self.retries = self.conf.multicloud.multicloud_retries

    def initialize(self):
        LOG.info(_LI("**** Initializing Multicloud Vim controller *****"))
        self._init_rest_request()

    def name(self):
        """Return human-readable name."""
        return "MultiCloud"

    def _request(self, method='get', path='/', data=None,
                 context=None, value=None):
        """Performs HTTP request."""
        headers = {
            'X-FromAppId': 'CONDUCTOR',
            'X-TransactionId': str(uuid.uuid4()),
        }
        kwargs = {
            "method": method,
            "path": path,
            "headers": headers,
            "data": data,
        }

        start_time = time.time()
        response = self.rest.request(**kwargs)
        elapsed = time.time() - start_time
        LOG.debug("Total time for Multicloud request "
                  "({0:}: {1:}): {2:.3f} sec".format(context, value, elapsed))

        if response is None:
            LOG.error(_LE("No response from Multicloud ({}: {})").
                      format(context, value))
        elif response.status_code != 200:
            LOG.error(_LE("Multicloud request ({}: {}) returned HTTP "
                          "status {} {}, link: {}{}").
                      format(context, value,
                             response.status_code, response.reason,
                             self.base, path))
        return response

    def _init_rest_request(self):

        kwargs = {
            "server_url": self.base,
            "retries": self.retries,
            "log_debug": self.conf.debug,
            "read_timeout": self.timeout,
        }
        self.rest = rest.REST(**kwargs)
        if self.conf.multicloud.enable_https_mode:
            self.rest.server_url = self.base[:4]+'s'+self.base[4:]
            self.rest.session.verify =self.conf.multicloud.certificate_authority_bundle_file    

    def check_vim_capacity(self, vim_request):
        LOG.debug("Invoking check_vim_capacity api")
        path = '/{}/{}'.format(self.version, 'check_vim_capacity')

        data = {}
        data['vCPU'] = vim_request['vCPU']
        data['Memory'] = vim_request['Memory']['quantity']
        data['Storage'] = vim_request['Storage']['quantity']
        data['VIMs'] = vim_request['VIMs']
        response = self._request('post', path=path, data=data,
                                 context="vim capacity", value="all")
        LOG.debug("Response check_vim_capacity api - {}".format(response))
        if response is None or response.status_code != 200:
            return None

        body = response.json()

        if body:
            vims = body.get("VIMs")
            if vims is None:
                LOG.error(_LE(
                    "Unable to get VIMs with cpu-{}, memory-{}, disk-{}")
                          .format(data['vCPU'],
                                  data['Memory'],
                                  data['Storage']))

            return vims
        else:
            LOG.error(_LE("Unable to get VIMs from Multicloud with "
                          "requirement {}").format(data))
            return None
