#
#
# -------------------------------------------------------------------------
#   Copyright (C) 2022 Wipro Limited.
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
from http.client import HTTPConnection
import json
import logging
from oslo_config import cfg
from oslo_log import log
import time
import uuid

LOG = log.getLogger(__name__)

log = logging.getLogger('urllib3')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)
HTTPConnection.debuglevel = 1

CONF = cfg.CONF

DCAE_OPTS = [
    cfg.StrOpt('table_prefix',
               default='dcae',
               help='Data Store table prefix.'),
    cfg.StrOpt('server_url',
               default='https://controller:8443/dcae',
               help='Base URL for DCAE, up to and not including '
               'the version, and without a trailing slash.'),
    cfg.StrOpt('dcae_rest_timeout',
               default='30',
               help='Timeout for DCAE Rest Call'),
    cfg.StrOpt('dcae_retries',
               default='3',
               help='Number of retry for DCAE Rest Call'),
    cfg.StrOpt('server_url_version',
               default='v1',
               help='The version of DCAE in v# format.'),
    cfg.StrOpt('certificate_file',
               default='certificate.pem',
               help='SSL/TLS certificate file in pem format.'
               'This certificate must be registered with the A&AI '
               'endpoint.'),
    cfg.StrOpt('certificate_key_file',
               default='certificate_key.pem',
               help='Private Certificate Key file in pem format.'),
    cfg.StrOpt('certificate_authority_bundle_file',
               default='',
               help='Certificate Authority Bundle file in pem format. '
               'Must contain the appropriate trust chain for the '
               'Certificate file.'),
    cfg.StrOpt('username',
               default='',
               help='Username for DCAE'),
    cfg.StrOpt('password',
               default='',
               help='Password for DCAE'),
    cfg.StrOpt('get_slice_config_url',
               default='',
               help="url to get slice configuration from DCAE")
]

CONF.register_opts(DCAE_OPTS, group='dcae')


class DCAE(object):

    """DCAE Inventory Provider"""

    def __init__(self):
        """Initializer"""
        self.conf = CONF
        self.base = self.conf.dcae.server_url.rstrip('/')
        self.version = self.conf.dcae.server_url_version.rstrip('/')
        self.cert = self.conf.dcae.certificate_file
        self.key = self.conf.dcae.certificate_key_file
        self.verify = self.conf.dcae.certificate_authority_bundle_file
        self.timeout = self.conf.dcae.dcae_rest_timeout
        self.retries = self.conf.dcae.dcae_retries
        self.username = self.conf.dcae.username
        self.password = self.conf.dcae.password
        self._init_python_request()

    def initialize(self):

        """Perform any late initialization."""
        # Initialize the Python requests
        # self._init_python_request()

    def _init_python_request(self):

        kwargs = {

            "server_url": self.base,

            "retries": self.retries,

            "username": self.username,

            "password": self.password,

            "read_timeout": self.timeout,

            "ca_bundle_file": self.verify,
        }

        self.rest = rest.REST(**kwargs)

    def _dcae_versioned_path(self, path):

        """Return a URL path with the DCAE version prepended"""
        return '/{}/{}'.format(self.version, path.lstrip('/'))

    def capacity_filter(self, candidates):
        candidatesList = {}
        updated_candidateList = []
        LOG.debug("from AAI ", candidates)
        for candidate in candidates:
            inventory_type = candidate.get('inventory_type')
            if inventory_type == 'nsi':
                candidate_id = candidate.get('instance_id')
            elif inventory_type == 'nssi':
                candidate_id = candidate.get('instance_id')
            else:
                LOG.debug("No candidate_id found")
            domain = candidate.get('domain')
            LOG.debug("domain from the candidate list is ", domain)
            response = self.get_dcae_response(candidate_id)
            LOG.debug(" DCAE response in capacity_filter() : ", response)
            # max_no_of_connections = self.get_max_no_of_connections(response)
            if response is not None:
                dLThpt = self.get_dLThpt(response, candidate_id)
                LOG.debug("dLThpt fetched from dcae response is", dLThpt)
                uLThpt = self.get_uLThpt(response, candidate_id)
                LOG.debug("uLThpt fetched from dcae response is", uLThpt)
                # max_no_of_pdu_sessions = self.get_max_no_of_pdu_sessions()
                if inventory_type == 'nsi':
                    uLThpt_ServiceProfile = candidate.get('ul_thpt_per_slice')
                    LOG.debug("uLThpt fetched from service profile is", uLThpt_ServiceProfile)
                    dLThpt_ServiceProfile = candidate.get('dl_thpt_per_slice')
                    LOG.debug("dLThpt fetched from service profile is", dLThpt_ServiceProfile)
                    uLThpt_difference = self.get_difference(uLThpt_ServiceProfile, uLThpt)
                    LOG.debug(" uLThpt_difference for nsi is ", uLThpt_difference)
                    dLThpt_difference = self.get_difference(dLThpt_ServiceProfile, dLThpt)
                    LOG.debug(" dLThpt_difference for nsi is ", dLThpt_difference)
                    candidate['uLThpt_difference'] = uLThpt_difference
                    candidate['dLThpt_difference'] = dLThpt_difference
                elif inventory_type == 'nssi' and (domain != 'TN_FH' and domain != 'TN_MH'):
                    uLThpt_SliceProfile = candidate.get('exp_data_rate_ul')
                    LOG.debug("uLThpt fetched from slice profile is", uLThpt_SliceProfile)
                    dLThpt_SliceProfile = candidate.get('exp_data_rate_dl')
                    LOG.debug("dLThpt fetched from slice profile is", dLThpt_SliceProfile)
                    uLThpt_difference = self.get_difference(uLThpt_SliceProfile, uLThpt)
                    LOG.debug(" uLThpt_difference for nssi is ", uLThpt_difference)
                    dLThpt_difference = self.get_difference(dLThpt_SliceProfile, dLThpt)
                    LOG.debug(" dLThpt_difference for nssi is ", dLThpt_difference)
                    candidate['uLThpt_difference'] = uLThpt_difference
                    candidate['dLThpt_difference'] = dLThpt_difference
                    # connections_difference = self.get_difference(max_no_of_pdu_sessions, max_no_of_connections)
                elif inventory_type == 'nssi' and (domain == 'TN_FH' and domain == 'TN_MH'):
                    uLThpt_difference = 10
                    dLThpt_difference = 10
                    candidate['uLThpt_difference'] = uLThpt_difference
                    candidate['dLThpt_difference'] = dLThpt_difference
                else:
                    LOG.debug("No difference attribute was added to the candidate")
            else:
                candidate = candidate
                LOG.debug("Returning original candidate list")
            candidatesList.update(candidate)
            LOG.debug("capacity filter ", candidatesList)
            updated_candidateList.append(candidatesList)
            LOG.debug("updated candidate list ", updated_candidateList)
        return updated_candidateList
        # def get_max_no_of_connections(self, response, candidate_id)
        #   responseJson = json.loads(response)
        #   maxNoConns = responseJson['sliceConfigDetails'][candidate_id]['aggregatedConfig']['maxNumberOfConns']
        #   return maxNoConns

    def get_uLThpt(self, response, candidate_id):
        responseJson = json.loads(response)
        configDetails = responseJson["sliceConfigDetails"]
        for i in range(len(configDetails)):
            if configDetails[i]["sliceIdentifiers"] == candidate_id:
                aggregatedConfig = configDetails[i]['aggregatedConfig']
                uLThpt = aggregatedConfig.get("ulthptPerSlice")
                LOG.debug(" uLthpt from DCAE is : ", uLThpt)
        return uLThpt

    def get_dLThpt(self, response, candidate_id):
        responseJson = json.loads(response)
        configDetails = responseJson["sliceConfigDetails"]
        for i in range(len(configDetails)):
            if configDetails[i]["sliceIdentifiers"] == candidate_id:
                aggregatedConfig = configDetails[i]['aggregatedConfig']
                dLThpt = aggregatedConfig.get("dlthptPerSlice")
                LOG.debug(" dLthpt from DCAE is : ", dLThpt)
        return dLThpt

    def get_difference(self, attribute1, attribute2):
        LOG.debug("Computing the difference between two attributes")
        difference = attribute1 - attribute2
        return difference

    def _request(self, method='get', path='/', data=None, context=None, value=None):

        """Performs HTTP request"""

        headers = {
            'X-FromAppId': 'CONDUCTOR',
            'X-TransactionId': str(uuid.uuid4()),
        }

        kwargs = {
            "method": method,
            "path": path,
            "headers": headers,
            "data": data,
            "content_type": "application/json"
        }
        start_time = time.time()
        response = self.rest.request(**kwargs)
        elapsed = time.time() - start_time
        LOG.debug("Total time for DCAE request ({0:}: {1:}): {2:.3f} sec".format(context, value, elapsed))
        if response is None:
            LOG.error(_LE("No response from DCAE ({}: {})").format(context, value))
        elif response.status_code != 200:
            LOG.error(_LE("DCAE request ({}: {}) returned HTTP status {} {},"
                          "link: {}{}").format(context, value, response.status_code, response.reason, self.base, path))
        return response

    def get_dcae_response(self, candidate_id):
        path = self.conf.dcae.get_slice_config_url
        data = {"sliceIdentifiers": [candidate_id], "configParams": ["dLThptPerSlice",
                "uLThptPerSlice", "maxNumberOfConns"]}
        dcae_response = self._request('get', path, data=data)
        LOG.debug(self._request('get', path, data=data))
        LOG.debug(" DCAE response : ", dcae_response)
        LOG.debug("DCAE json response is : ", json.dumps(dcae_response.json()))
        dcae_response2 = json.dumps(dcae_response.json())
        LOG.debug(" processed DCAE response is ", dcae_response2)
        if dcae_response2 is None or dcae_response.status_code != 200:
            return None
        if dcae_response2:
            responseJson = json.loads(dcae_response2)
            LOG.debug("response json from DCAE is :", responseJson)
            if 'sliceConfigDetails' not in responseJson or len(responseJson['sliceConfigDetails']) == 0:
                LOG.debug(" Returning None to capacity_filter()")
                return None
            else:
                LOG.debug("returning DCAE response to capacity_filter() from get_dcae_response()")
                return dcae_response2
