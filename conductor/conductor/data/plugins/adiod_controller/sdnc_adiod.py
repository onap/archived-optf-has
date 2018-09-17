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
from conductor.data.plugins.adiod_controller import base
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
               default=30,
               help='Timeout for SDNC Rest Call'),
    cfg.StrOpt('sdnc_retries',
               default=3,
               help='Retry Numbers for SDNC Rest Call'),
]

CONF.register_opts(SDNC_OPTS, group='sdnc')


class SDNC_ADIOD(base.AdoidControllerBase):
    """SDN ADIOD Service Controller"""

    def __init__(self):
        """Initializer"""
        self.conf = CONF

        self.base = self.conf.sdnc.server_url.rstrip('/')
        self.password = self.conf.sdnc.password
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
        return "SDN-C_ADIOD"

    def _request(self, method='get', path='/', data=None,
                 context=None, value=None):
        """Performs HTTP request."""
        kwargs = {
            "method": method,
            "path": path,
            "data": data,
        }

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

    def capacity_check_operation(self, candidate_list,
                                 request):

        filtered_candidate = list()
        service_model = request.get("service_model")
        service_speed = request.get("service_speed")
        service_speed_unit = request.get("service_speed_unit")
        entity_type = request.get("entity_type")
        entity_id = request.get("entity_id")
        vnf_type = request.get("vnf_type")

        for candidate in candidate_list:
            is_filitered = True
            vnf_host_name = candidate.get("host_id") if "host_id" in candidate else candidate.get("candidate_id")

            data = {
                "input": {
                    "capacity-reservation-information": {
                        "service-model": service_model,
                        "reservation-entity-list": [{
                            "reservation-entity-type": entity_type,
                            "reservation-entity-id": entity_id,
                            "reservation-entity-data": [
                              {
                                "name": "service-speed",
                                "value": service_speed
                              }, {
                                "name": "service-speed-unit",
                                "value": service_speed_unit
                              }
                          ]
                        }],
                        "reservation-target-list": [{
                            "reservation-target-type": "VNF",
                            "reservation-target-id": vnf_host_name,
                            "reservation-target-data": [{
                                "name": "vnf-type",
                                "value": vnf_type
                            }, {
                                "name": "vpe-name",
                                "value": vnf_host_name
                            }]
                        }]
                    }
                }
            }

            path = '/operations/CAPACITY-API:service-capacity-check-operation'
            response = self._request('post', path=path, data=data)

            if response is None or response.status_code != 200:
                is_filitered = False
            body = response.json()

            # check if the candidate is reserved successfully
            output = body.get("output")

            if output:
                capacity_info = output.get("capacity-information")
                response_code = output.get("response-code")
                if capacity_info and response_code == "200":
                    status = capacity_info.get("status").lower()
                    entity_list = capacity_info.get("reservation-entity-list")
                    if status.lower() != 'success':
                        is_filitered = False

                    for entity in entity_list:
                        entity_status = entity.get("status").lower()
                        if entity_status.lower() != 'success':
                            is_filitered = False
                else:
                    is_filitered = False

            if is_filitered:
                filtered_candidate.append(candidate)

        return filtered_candidate if filtered_candidate else None


    def call_reservation_operation(self, method,
                                   candidate_list,
                                   request):

        reserved_candidate = list()
        service_model = request.get("service_model")
        service_speed = request.get("service_speed")
        service_speed_unit = request.get("service_speed_unit")
        entity_type = request.get("entity_type")
        entity_id = request.get("entity_id")
        vnf_type = request.get("vnf_type")

        for candidate in candidate_list:
            result = True
            vnf_host_name = candidate.get("host_id")
            if vnf_host_name is None:
                vnf_host_name = candidate.get("candidate_id")

            if method == "release":
                data = {
                    "input": {
                        "reservation-entity-list": [
                            {
                                "reservation-entity-type": entity_type,
                                "reservation-entity-id": entity_id
                            }
                        ]
                    }
                }

            elif method == "reserve":

                reservation_target_list = [
                                {
                                    "reservation-target-type": "VNF",
                                    "reservation-target-id": vnf_host_name,
                                    "reservation-target-data": [{
                                        "name": "vnf-type",
                                        "value": vnf_type
                                    }, {
                                    "name": "vpe-name",
                                    "value": vnf_host_name
                                    }]
                                }
                              ]

                if service_model == 'ADIG':
                    port_key = request.get("port_key")

                    dict = {
                        "reservation-target-type": "PORT",
                        "reservation-target-id": port_key,
                        "reservation-target-data": [{
                                "name": "service-speed",
                                "value": service_speed
                            },
                            {
                                "name": "service-speed-unit",
                                "value": service_speed_unit
                            }
                        ]
                    }
                    reservation_target_list.append(dict)

                data = {
                    "input": {
                        "capacity-reservation-information": {
                            "service-model": service_model,
                            "reservation-entity-list": [{
                                "reservation-entity-type": entity_type,
                                "reservation-entity-id": entity_id,
                                "reservation-entity-data": [{
                                    "name": "service-speed",
                                    "value": service_speed
                                }, {
                                    "name": "service-speed-unit",
                                    "value": service_speed_unit
                                }]
                            }],
                            "reservation-target-list": reservation_target_list
                        }
                    }
                }

            path = '/operations/CAPACITY-API:service-capacity-' \
                   + method + '-operation'
            response = self._request('post', path=path, data=data)

            if response is None or response.status_code != 200:
                result = False
            body = response.json()

            # check if the candidate is reserved successfully
            output = body.get("output")

            if output:
                capacity_info = output.get("capacity-information")
                response_code = output.get("response-code")
                if method == "release" and response_code == "200":
                    reserved_candidate.append(candidate)
                    break
                if capacity_info and response_code == "200":
                    status = capacity_info.get("status").lower()
                    entity_list = capacity_info.get("reservation-entity-list")
                    if status != 'success':
                        result = False

                    for entity in entity_list:
                        entity_status = entity.get("status").lower()
                        if entity_status != 'success':
                            result = False
                else:
                    result = False

            if result:
                reserved_candidate.append(candidate)

        return reserved_candidate if reserved_candidate else None