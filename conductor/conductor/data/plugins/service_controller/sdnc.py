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
               default=30,
               help='Timeout for SDNC Rest Call'),
    cfg.StrOpt('sdnc_retries',
               default=3,
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

        path = '/operations/DHVCAPACITY-API:service-capacity-check-operation'
        action_type = "RESERVE"
        change_type = "New-Start"

        e2evpnkey = request.get('e2evpnkey')
        dhv_service_instance = request.get('dhv_service_instance')

        vnf_input_list = []

        for candidate in candidate_list:

            # SDN-GC does not reserve cloud candidates
            if candidate.get("inventory_type") == "cloud":
                continue

            vnf_input = {}
            # VNF input parameters common to all service_type
            request = candidate.get('request')
            vnf_input["device-type"] = request.get('service_type')
            vnf_input['dhv-site-effective-bandwidth'] = request.get('dhv_site_effective_bandwidth')

            if candidate.get('location_id') == "AAIAIC25":
                vnf_input["cloud-region-id"] = ""
            else:
                vnf_input["cloud-region-id"] = candidate.get('location_id')

            if "service_resource_id" in candidate:
                vnf_input["cust-service-instance-id"] = candidate.get('service_resource_id')

            vnf_input["vnf-host-name"] = candidate.get('host_id')
            vnf_input["infra-service-instance-id"] = candidate.get('candidate_id')

            vnf_input_list.append(vnf_input)

        data = {
            "input": {
                "service-capacity-check-operation": {
                    "sdnc-request-header": {
                        "request-id":
                            "59c36776-249b-4966-b911-9a89a63d1676"
                    },
                    "capacity-check-information": {
                        "service-instance-id": dhv_service_instance,
                        "service": "DHV SD-WAN",
                        "action-type": action_type,
                        "change-type": change_type,
                        "e2e-vpn-key": e2evpnkey,
                        "vnf-list": {
                            "vnf": vnf_input_list
                        }
                    }
                }
            }
        }

        try:
            response = self._request('post', path=path, data=data)
            if response is None or response.status_code != 200:
                return
            body = response.json()
            response_code = body.get("output"). \
                get("service-capacity-check-response"). \
                get("response-code")

            if response_code == "200":
                return candidate_list

        except Exception as exc:
            LOG.error("SD-WAN reservation, SDNC unknown error: {}".
                      format(exc))
            return

    def filter_candidates(self, request, candidate_list,
                          constraint_name, constraint_type, request_type):
        """Reduce candidate list based on SDN-C intelligence"""
        selected_candidates = []
        path = '/operations/DHVCAPACITY-API:service-capacity-check-operation'
        action_type = ""
        if constraint_type == "instance_fit":
            action_type = "CAPCHECK-SERVICE"
        elif constraint_type == "region_fit":
            action_type = "CAPCHECK-NEWVNF"
        else:
            LOG.error(_LE("Constraint {} has an unknown type {}").
                      format(constraint_name, constraint_type))

        # VNF input params common to all services
        service_type = request.get('service_type')
        e2evpnkey = request.get('e2evpnkey')

        vnf_input = {}
        # VNF inputs specific to service_types
        if service_type.lower() == "vvig":
            # get input parameters
            bw_down = request.get('bw_down')
            bw_up = request.get('bw_up')
            dhv_site_effective_bandwidth = request.get('dhv_site_effective_bandwidth')
            dhv_service_instance = request.get('dhv_service_instance')
            if not dhv_site_effective_bandwidth or not bw_down or not bw_up:
                LOG.error(_LE("Constraint {} vVIG capacity check is "
                "missing up/down/effective bandwidth").
                format(constraint_name))
                return
            # add instance_fit specific input parameters
            if constraint_type == "instance_fit":
                if not dhv_service_instance:
                    LOG.error(_LE("Constraint {} vVIG capacity check is "
                                  "missing DHV service instance").
                              format(constraint_name))
                    return
                vnf_input["infra-service-instance-id"] = dhv_service_instance
            # input params common to both instance_fit & region_fit
            vnf_input["upstream-bandwidth"] = bw_up
            vnf_input["downstream-bandwidth"] = bw_down
            vnf_input["dhv-site-effective-bandwidth"] = dhv_site_effective_bandwidth

        elif service_type.lower() == "vhngw":
            # get input parameters
            dhv_site_effective_bandwidth = \
                request.get('dhv_site_effective_bandwidth')
            if not dhv_site_effective_bandwidth:
                LOG.error(_LE("Constraint {} vHNGW capacity check is "
                              "missing DHV site effective bandwidth").
                          format(constraint_name))
                return
            vnf_input["dhv-site-effective-bandwidth"] = \
                dhv_site_effective_bandwidth
        elif service_type.lower() == "vhnportal":
            dhv_service_instance = request.get('dhv_service_instance')
            # add instance_fit specific input parameters
            if constraint_type == "instance_fit":
                if not dhv_service_instance:
                    LOG.error(_LE("Constraint {} vHNPortal capacity check is "
                                  "missing DHV service instance").
                              format(constraint_name))
                    return
                vnf_input["infra-service-instance-id"] = dhv_service_instance

        for candidate in candidate_list:

            # generate the value of change_type based on the request type (inital or speed changed)
            # and existing placement
            # For New Start (or initial): New-Start
            # For Change Speed No Rehome :  Change-Speed
            # For Change Speed Rehome: Rehome
            change_type = ""
            if request_type == "initial" or request_type == "":
                change_type = "New-Start"
            elif request_type == "speed changed":
                existing_placement = str(candidate.get('existing_placement'))
                if existing_placement == 'false':
                    change_type = "Rehome"
                elif existing_placement == 'true':
                    change_type = "Change-Speed"
            else:
                LOG.error(_LE("Constraint {} has an unknown request type {}").
                          format(constraint_name, request_type))

            # VNF input parameters common to all service_type
            vnf_input["device-type"] = service_type
            # If the candidate region id is AAIAIC25 and region_fit constraint
            # then ignore that candidate since SDNC may fall over if it
            # receives a capacity check for these candidates.
            # If candidate region id is AAIAIC25 and instance constraint
            # then set the region id to empty string in the input to SDNC.
            # If neither of these conditions, then send the candidate's
            # location id as the region id input to SDNC
            if constraint_type == "region_fit" \
                    and candidate.get("inventory_type") == "cloud" \
                    and candidate.get('location_id') == "AAIAIC25":
                continue
            elif constraint_type == "instance_fit" \
                    and candidate.get("inventory_type") == "service" \
                    and candidate.get('location_id') == "AAIAIC25":
                vnf_input["cloud-region-id"] = ""
            else:
                vnf_input["cloud-region-id"] = candidate.get('location_id')

            if constraint_type == "instance_fit":
                vnf_input["vnf-host-name"] = candidate.get('host_id')
                '''
                ONLY for service candidates:
                For candidates with AIC version 2.5, SDN-GC uses 'infra-service-instance-id' to identify vvig.
                'infra-service-instance-id' is 'candidate_id' in Conductor candidate structure
                '''
                vnf_input["infra-service-instance-id"] = candidate.get('candidate_id')

            if "service_resource_id" in candidate:
                vnf_input["cust-service-instance-id"] = candidate.get('service_resource_id')

            data = {
                "input": {
                    "service-capacity-check-operation": {
                        "sdnc-request-header": {
                            "request-id":
                                "59c36776-249b-4966-b911-9a89a63d1676"
                        },
                        "capacity-check-information": {
                            "service-instance-id": "ssb-0001",
                            "service": "DHV SD-WAN",
                            "action-type": action_type,
                            "change-type": change_type,
                            "e2e-vpn-key": e2evpnkey,
                            "vnf-list": {
                                "vnf": [vnf_input]
                            }
                        }
                    }
                }
            }

            try:
                device = None
                cloud_region_id = None
                available_capacity = None
                context = "constraint, type, service type"
                value = "{}, {}, {}".format(
                    constraint_name, constraint_type, service_type)
                LOG.debug("Json sent to SDNC: {}".format(data))
                response = self._request('post', path=path, data=data,
                                         context=context, value=value)
                if response is None or response.status_code != 200:
                    return
                body = response.json()
                vnf_list = body.get("output").\
                    get("service-capacity-check-response").\
                    get("vnf-list").get("vnf")
                if not vnf_list or len(vnf_list) < 1:
                    LOG.error(_LE("VNF is missing in SDNC response "
                                  "for constraint {}, type: {}, "
                                  "service type: {}").
                              format(constraint_name, constraint_type,
                                     service_type))
                elif len(vnf_list) > 1:
                    LOG.error(_LE("More than one VNF received in response"
                                  "for constraint {}, type: {}, "
                                  "service type: {}").
                              format(constraint_name, constraint_type,
                                     service_type))
                    LOG.debug("VNF List: {}".format(vnf_list))
                else:
                    for vnf in vnf_list:
                        device = vnf.get("device-type")
                        cloud_region_id = vnf.get("cloud-region-id")
                        available_capacity = vnf.get("available-capacity")
                        break  # only one response expected for one candidate
                if available_capacity == "N":
                    LOG.error(_LE("insufficient capacity for {} in region {} "
                                  "for constraint {}, type: {}, "
                                  "service type: {}").
                              format(device, cloud_region_id, constraint_name,
                                     constraint_type, service_type))
                    LOG.debug("VNF List: {}".format(vnf_list))
                elif available_capacity == "Y":
                    selected_candidates.append(candidate)
                    LOG.debug("Candidate found for {} in region {} "
                              "for constraint {}, type: {}, "
                              "service type: {}"
                              .format(device, cloud_region_id, constraint_name,
                                      constraint_type, service_type))
            except Exception as exc:
                # TODO(shankar): Make more specific once we know SDNC errors
                LOG.error("Constraint {}, type: {}, SDNC unknown error: {}".
                          format(constraint_name, constraint_type, exc))
                return

        return selected_candidates
