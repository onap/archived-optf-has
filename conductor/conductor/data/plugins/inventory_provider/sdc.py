#
# -------------------------------------------------------------------------
#   Copyright (C) 2020 Wipro Limited.
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
from conductor.data.plugins.inventory_provider.utils import csar
from conductor.i18n import _LE
import os
from oslo_config import cfg
from oslo_log import log
import time
import uuid


LOG = log.getLogger(__name__)

CONF = cfg.CONF

SDC_OPTS = [
    cfg.StrOpt('table_prefix',
               default='sdc',
               help='Data Store table prefix.'),
    cfg.StrOpt('server_url',
               default='https://controller:8443/sdc',
               help='Base URL for SDC, up to and not including '
                    'the version, and without a trailing slash.'),
    cfg.StrOpt('sdc_rest_timeout',
               default='30',
               help='Timeout for SDC Rest Call'),
    cfg.StrOpt('sdc_retries',
               default='3',
               help='Number of retry for SDC Rest Call'),
    cfg.StrOpt('server_url_version',
               default='v1',
               help='The version of SDC in v# format.'),
    # TODO(larry): follow-up with ONAP people on this (SDC basic auth username and password?)
    cfg.StrOpt('certificate_file',
               default='certificate.pem',
               help='SSL/TLS certificate file in pem format. '
                    'This certificate must be registered with the A&AI '
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
               help='Username for SDC.'),
    cfg.StrOpt('password',
               default='',
               help='Password for SDC.'),
    cfg.StrOpt('temp_path',
               default=',',
               help="path to store nst templates")
]

CONF.register_opts(SDC_OPTS, group='sdc')


class SDC(object):
    """SDC Inventory Provider"""

    def __init__(self):
        """Initializer"""

        self.conf = CONF

        self.base = self.conf.sdc.server_url.rstrip('/')
        self.version = self.conf.sdc.server_url_version.rstrip('/')
        self.cert = self.conf.sdc.certificate_file
        self.key = self.conf.sdc.certificate_key_file
        self.verify = self.conf.sdc.certificate_authority_bundle_file
        self.timeout = self.conf.sdc.sdc_rest_timeout
        self.retries = self.conf.sdc.sdc_retries
        self.username = self.conf.sdc.username
        self.password = self.conf.sdc.password
        self._init_python_request()

    def initialize(self):

        """Perform any late initialization."""
        # Initialize the Python requests
        # self._init_python_request()

    def _sdc_versioned_path(self, path):
        """Return a URL path with the SDC version prepended"""
        return '/{}/{}'.format(self.version, path.lstrip('/'))

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

        # TODO(jdandrea): Move timing/response logging into the rest helper?
        start_time = time.time()
        response = self.rest.request(**kwargs)
        elapsed = time.time() - start_time
        LOG.debug("Total time for SDC request "
                  "({0:}: {1:}): {2:.3f} sec".format(context, value, elapsed))

        if response is None:
            LOG.error(_LE("No response from SDC ({}: {})").
                      format(context, value))
        elif response.status_code != 200:
            LOG.error(_LE("SDC request ({}: {}) returned HTTP "
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

    def update_candidates(self, candidates):
        absfilepath = self.conf.sdc.temp_path
        candidateslist = []
        for candidate in candidates:
            model_ver_obj = candidate.model_ver_info
            model_name = model_ver_obj['model_name']
            self.model_version_id = candidate.candidate_id
            response = self.get_nst_template(self.model_version_id)
            filepath = os.path.join(absfilepath, "{}.csar".format(self.model_version_id))
            if not os.path.exists(absfilepath):
                os.makedirs(absfilepath)
            f = open(filepath, "wb")
            file_res = response.content
            f.write(file_res)
            obj = csar.SDCCSAR(filepath, model_name)
            nst_temp_prop = obj.validate()
            nst_properties = self.get_nst_prop_dict(nst_temp_prop)
            candidate.profile_info = nst_properties
            finalcandidate = candidate.convert_nested_dict_to_dict()
            candidateslist.append(finalcandidate)
        return candidateslist

    def get_nst_prop_dict(self, nst_properties):
        properties_dict = dict()
        for key in list(nst_properties):
            temp_dict = nst_properties[key]
            for temp_key in list(temp_dict):
                if "default" in temp_key:
                    properties_dict[key] = temp_dict[temp_key]
        return properties_dict

    def get_nst_template(self, ver_id):
        raw_path = "/catalog/services/{}/toscaModel".format(ver_id)
        path = self._sdc_versioned_path(raw_path)
        sdc_response = self._request('get', path, data=None)
        if sdc_response is None or sdc_response.status_code != 200:
            return None
        if sdc_response:
            return sdc_response
