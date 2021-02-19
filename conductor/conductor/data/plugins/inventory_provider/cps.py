#
# -------------------------------------------------------------------------
#   Copyright (C) 2021 Wipro Limited.
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
from conductor.common import rest
from conductor.i18n import _LE
from oslo_config import cfg
from oslo_log import log
import time
import uuid


LOG = log.getLogger(__name__)

CONF = cfg.CONF

CPS_OPTS = [
    cfg.StrOpt('table_prefix',
               default='cps',
               help='Data Store table prefix.'),
    cfg.StrOpt('server_url',
               default='https://controller:8443/cps',
               help='Base URL for CPS, up to and not including '
                    'the version, and without a trailing slash.'),
    cfg.StrOpt('cps_rest_timeout',
               default='30',
               help='Timeout for CPS Rest Call'),
    cfg.StrOpt('cps_retries',
               default='3',
               help='Number of retry for CPS Rest Call'),
    # TODO(larry): follow-up with ONAP people on this (CPS basic auth username and password?)
    cfg.StrOpt('certificate_file',
               default='certificate.pem',
               help='SSL/TLS certificate file in pem format. '
                    'This certificate must be registered with the CPS '
                    'endpoint.'),
    cfg.StrOpt('certificate_key_file',
               default='certificate_key.pem',
               help='Private Certificate Key file in pem format.'),
    cfg.StrOpt('certificate_authority_bundle_file',
               default='certificate_authority_bundle.pem',
               help='Certificate Authority Bundle file in pem format. '
                    'Must contain the appropriate trust chain for the '
                    'Certificate file.'),
    cfg.StrOpt('username',
               default='',
               help='Username for CPS.'),
    cfg.StrOpt('password',
               default='',
               help='Password for CPS.'),
    cfg.StrOpt('get_ta_list_url',
               default='',
               help="url to get ta_list")
]

CONF.register_opts(CPS_OPTS, group='cps')


class CPS(object):

    def __init__(self):
        """Initializer"""

        self.conf = CONF

        self.base = self.conf.cps.server_url.rstrip('/')
        self.cert = self.conf.cps.certificate_file
        self.key = self.conf.cps.certificate_key_file
        self.verify = self.conf.cps.certificate_authority_bundle_file
        self.timeout = self.conf.cps.cps_rest_timeout
        self.retries = self.conf.cps.cps_retries
        self.username = self.conf.cps.username
        self.password = self.conf.cps.password
        self._init_python_request()

    def _request(self, method='post', path='/', data=None,
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

        # TODO(jdandrea): Move timing/response logging into the rest helper?
        start_time = time.time()
        response = self.rest.request(**kwargs)
        elapsed = time.time() - start_time
        LOG.debug("Total time for CPS request "
                  "({0:}: {1:}): {2:.3f} sec".format(context, value, elapsed))

        if response is None:
            LOG.error(_LE("No response from CPS ({}: {})").
                      format(context, value))
        elif response.status_code != 200:
            LOG.error(_LE("CPS request ({}: {}) returned HTTP "
                          "status {} {}, link: {}{}").
                      format(context, value,
                             response.status_code, response.reason,
                             self.base, path))
        return response

    def _init_python_request(self):

        kwargs = {
            "server_url": self.base,
            "retries": self.retries,
            "username": self.username,
            "password": self.password,
            "read_timeout": self.timeout,
        }
        self.rest = rest.REST(**kwargs)

    def get_coveragearea_ta(self, args):
        response = self.get_cps_response(args)
        return response

    def get_cps_response(self, args):
        path = self.conf.cps.get_ta_list_url
        data = {}
        data['input'] = {'zone_id': args}
        cps_response = self._request('post', path, data=data)
        if cps_response is None or cps_response.status_code != 200:
            return None
        if cps_response:
            return cps_response.json()
