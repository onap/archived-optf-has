#
# -------------------------------------------------------------------------
#   Copyright (c) 2015-2017 AT&T Intellectual Property
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

import copy
import json
import re
import time
import uuid

from oslo_config import cfg
from oslo_log import log


from conductor.common import rest
from conductor.data.plugins import constants
from conductor.data.plugins.inventory_provider import base
from conductor.data.plugins.inventory_provider.candidates.candidate import Candidate
from conductor.data.plugins.inventory_provider.candidates.cloud_candidate import Cloud
from conductor.data.plugins.inventory_provider.candidates.nxi_candidate import NxI
from conductor.data.plugins.inventory_provider.candidates.service_candidate import Service
from conductor.data.plugins.inventory_provider.candidates.transport_candidate import Transport
from conductor.data.plugins.inventory_provider.candidates.vfmodule_candidate import VfModule
from conductor.data.plugins.inventory_provider import hpa_utils
from conductor.data.plugins.inventory_provider.utils import aai_utils
from conductor.data.plugins.triage_translator.triage_translator import TraigeTranslator
from conductor.i18n import _LE
from conductor.i18n import _LI

LOG = log.getLogger(__name__)

CONF = cfg.CONF

AAI_OPTS = [
    cfg.IntOpt('cache_refresh_interval',
               default=1440,
               help='Interval with which to refresh the local cache, '
                    'in minutes.'),
    cfg.IntOpt('complex_cache_refresh_interval',
               default=1440,
               help='Interval with which to refresh the local complex cache, '
                    'in minutes.'),
    cfg.StrOpt('table_prefix',
               default='aai',
               help='Data Store table prefix.'),
    cfg.StrOpt('server_url',
               default='https://controller:8443/aai',
               help='Base URL for A&AI, up to and not including '
                    'the version, and without a trailing slash.'),
    cfg.StrOpt('aai_rest_timeout',
               default='30',
               help='Timeout for A&AI Rest Call'),
    cfg.StrOpt('aai_retries',
               default='3',
               help='Number of retry for A&AI Rest Call'),
    cfg.StrOpt('server_url_version',
               default='v10',
               help='The version of A&AI in v# format.'),
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
    # TODO(larry): follow-up with ONAP people on this (AA&I basic auth username and password?)
    cfg.StrOpt('username',
               default='',
               help='Username for AAI.'),
    cfg.StrOpt('password',
               default='',
               help='Password for AAI.'),
]

CONF.register_opts(AAI_OPTS, group='aai')


class AAI(base.InventoryProviderBase):
    """Active and Available Inventory Provider"""

    def __init__(self):
        """Initializer"""

        # FIXME(jdandrea): Pass this in to init.
        self.conf = CONF

        self.base = self.conf.aai.server_url.rstrip('/')
        self.version = self.conf.aai.server_url_version.rstrip('/')
        self.cert = self.conf.aai.certificate_file
        self.key = self.conf.aai.certificate_key_file
        self.verify = self.conf.aai.certificate_authority_bundle_file
        self.cache_refresh_interval = self.conf.aai.cache_refresh_interval
        self.last_refresh_time = None
        self.complex_cache_refresh_interval = \
            self.conf.aai.complex_cache_refresh_interval
        self.complex_last_refresh_time = None
        self.timeout = self.conf.aai.aai_rest_timeout
        self.retries = self.conf.aai.aai_retries
        self.username = self.conf.aai.username
        self.password = self.conf.aai.password
        self.triage_translator = TraigeTranslator()

        # Cache is initially empty
        self._aai_cache = {}
        self._aai_complex_cache = {}

    def initialize(self):

        """Perform any late initialization."""
        # Initialize the Python requests
        self._init_python_request()

        # Refresh the cache once for now
        self._refresh_cache()

        # TODO(jdandrea): Make this periodic, and without a True condition!
        # executor = futurist.ThreadPoolExecutor()
        # while True:
        #     fut = executor.submit(self.refresh_cache)
        #     fut.result()
        #
        #     # Now wait for the next time.
        #     # FIXME(jdandrea): Put inside refresh_cache()?
        #     refresh_interval = self.conf.aai.cache_refresh_interval
        #     time.sleep(refresh_interval)
        # executor.shutdown()

    def name(self):
        """Return human-readable name."""
        return "A&AI"

    @staticmethod
    def _get_version_from_string(string):
        """Extract version number from string"""
        return re.sub("[^0-9.]", "", string)

    def _aai_versioned_path(self, path):
        """Return a URL path with the A&AI version prepended"""
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
        LOG.debug("Total time for A&AI request "
                  "({0:}: {1:}): {2:.3f} sec".format(context, value, elapsed))

        if response is None:
            LOG.error(_LE("No response from A&AI ({}: {})").
                      format(context, value))
        elif response.status_code != 200:
            LOG.error(_LE("A&AI request ({}: {}) returned HTTP "
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
            "cert_file": self.cert,
            "cert_key_file": self.key,
            "ca_bundle_file": self.verify,
            "log_debug": self.conf.debug,
            "read_timeout": self.timeout,
        }
        self.rest = rest.REST(**kwargs)

    def _refresh_cache(self):
        """Refresh the A&AI cache."""
        if not self.last_refresh_time or \
                (time.time() - self.last_refresh_time) > \
                self.cache_refresh_interval * 60:
            # TODO(jdandrea): This is presently brute force.
            # It does not persist to Music. A general purpose ORM caching
            # object likely needs to be made, with a key (hopefully we
            # can use one that is not just a UUID), a value, and a
            # timestamp. The other alternative is to not use the ORM
            # layer and call the API directly, but that is
            # also trading one set of todos for another ...

            # Get all A&AI sites
            LOG.info(_LI("**** Refreshing A&AI cache *****"))
            path = self._aai_versioned_path(
                '/cloud-infrastructure/cloud-regions/?depth=0')
            response = self._request(
                path=path, context="cloud regions", value="all")
            if response is None:
                return
            regions = {}
            if response.status_code == 200:
                body = response.json()
                regions = body.get('cloud-region', {})
            if not regions:
                # Nothing to update the cache with
                LOG.error(_LE("A&AI returned no regions, link: {}{}").
                          format(self.base, path))
                return
            cache = {
                'cloud_region': {},
                'service': {},
            }
            for region in regions:
                cloud_region_id = region.get('cloud-region-id')

                LOG.debug("Working on region '{}' ".format(cloud_region_id))

                cloud_region_version = region.get('cloud-region-version')
                cloud_owner = region.get('cloud-owner')
                cloud_type = region.get('cloud-type')
                cloud_zone = region.get('cloud-zone')

                physical_location_list = self._get_aai_rel_link_data(data=region, related_to='complex',
                                                                     search_key='complex.physical-location-id')
                if len(physical_location_list) > 0:
                    physical_location_id = physical_location_list[0].get('d_value')

                if not (cloud_region_version and cloud_region_id):
                    continue
                rel_link_data_list = \
                    self._get_aai_rel_link_data(
                        data=region,
                        related_to='complex',
                        search_key='complex.physical-location-id')
                if len(rel_link_data_list) > 1:
                    LOG.error(_LE("Region {} has more than one complex").
                              format(cloud_region_id))
                    LOG.debug("Region {}: {}".format(cloud_region_id, region))

                    continue
                rel_link_data = rel_link_data_list[0]
                complex_id = rel_link_data.get("d_value")
                complex_link = rel_link_data.get("link")
                if complex_id and complex_link:
                    complex_info = self._get_complex(
                        complex_link=complex_link,
                        complex_id=complex_id)
                else:  # no complex information
                    LOG.error(_LE("Region {} does not reference a complex").
                              format(cloud_region_id))
                    continue
                if not complex_info:
                    LOG.error(_LE("Region {}, complex {} info not found, "
                                  "link {}").format(cloud_region_id,
                                                    complex_id, complex_link))
                    continue

                latitude = complex_info.get('latitude')
                longitude = complex_info.get('longitude')
                city = complex_info.get('city')
                state = complex_info.get('state')
                region = complex_info.get('region')
                country = complex_info.get('country')
                complex_name = complex_info.get('complex-name')

                if not (latitude and longitude and city and country and complex_name):
                    keys = ('latitude', 'longitude', 'city', 'country',
                            'complex_name')
                    missing_keys = \
                        list(set(keys).difference(
                            list(complex_info.keys())))  # Python 3 Conversion -- dict object to list object
                    LOG.error(_LE("Complex {} is missing {}, link: {}").
                              format(complex_id, missing_keys, complex_link))
                    LOG.debug("Complex {}: {}".
                              format(complex_id, complex_info))

                    continue
                cache['cloud_region'][cloud_region_id] = {
                    'cloud_region_version': cloud_region_version,
                    'cloud_owner': cloud_owner,
                    'cloud_type': cloud_type,
                    'cloud_zone': cloud_zone,
                    'complex_name': complex_name,
                    'physical_location_id': physical_location_id,
                    'complex': {
                        'complex_id': complex_id,
                        'complex_name': complex_name,
                        'latitude': latitude,
                        'longitude': longitude,
                        'city': city,
                        'state': state,
                        'region': region,
                        'country': country,
                    }
                }

                # Added for HPA support
                if self.conf.HPA_enabled:
                    flavors = self._get_flavors(cloud_owner, cloud_region_id)
                    cache['cloud_region'][cloud_region_id]['flavors'] = flavors

                LOG.debug("Candidate with cloud_region_id '{}' selected "
                          "as a potential candidate - ".format(cloud_region_id))
            LOG.debug("Done with region '{}' ".format(cloud_region_id))
            self._aai_cache = cache
            self.last_refresh_time = time.time()
            LOG.info(_LI("**** A&AI cache refresh complete *****"))

    @staticmethod
    def _get_aai_rel_link(data, related_to):
        """Given an A&AI data structure, return the related-to link"""
        rel_dict = data.get('relationship-list')
        if rel_dict:
            for key, rel_list in rel_dict.items():
                for rel in rel_list:
                    if related_to == rel.get('related-to'):
                        return rel.get('related-link')

    @staticmethod
    def _get_aai_rel_link_data(data, related_to, search_key=None,
                               match_dict=None):
        # some strings that we will encounter frequently
        rel_lst = "relationship-list"
        rkey = "relationship-key"
        rval = "relationship-value"
        rdata = "relationship-data"
        response = list()
        if match_dict:
            m_key = match_dict.get('key')
            m_value = match_dict.get('value')
        else:
            m_key = None
            m_value = None
        rel_dict = data.get(rel_lst)
        if rel_dict:  # check if data has relationship lists
            for key, rel_list in rel_dict.items():
                for rel in rel_list:
                    if rel.get("related-to") == related_to:
                        dval = None
                        matched = False
                        link = rel.get("related-link")
                        r_data = rel.get(rdata, [])
                        if search_key:
                            for rd in r_data:
                                if rd.get(rkey) == search_key:
                                    dval = rd.get(rval)
                                    if not match_dict:  # return first match
                                        response.append(
                                            {"link": link, "d_value": dval}
                                        )
                                        break  # go to next relation
                                if rd.get(rkey) == m_key \
                                        and rd.get(rval) == m_value:
                                    matched = True
                            if match_dict and matched:  # if matching required
                                response.append(
                                    {"link": link, "d_value": dval}
                                )
                                # matched, return search value corresponding
                                # to the matched r_data group
                        else:  # no search key; just return the link
                            response.append(
                                {"link": link, "d_value": dval}
                            )
        if len(response) == 0:
            response.append(
                {"link": None, "d_value": None}
            )
        return response

    @staticmethod
    def check_sriov_automation(aic_version, demand_name, candidate_name):
        """Check if specific candidate has SRIOV automation available or no"""
        if aic_version:
            LOG.debug(_LI("Demand {}, candidate {} has an AIC version number {}").format(demand_name, candidate_name,
                                                                                         aic_version))
            if aic_version == "X.Y":
                return True
        return False

    def _get_complex(self, complex_link, complex_id=None):

        if not self.complex_last_refresh_time or \
                (time.time() - self.complex_last_refresh_time) > \
                self.complex_cache_refresh_interval * 60:
            self._aai_complex_cache.clear()
        if complex_id and complex_id in self._aai_complex_cache:
            return self._aai_complex_cache[complex_id]
        else:
            path = self._aai_versioned_path(self._get_aai_path_from_link(complex_link))
            response = self._request(path=path, context="complex", value=complex_id)
            if response is None:
                return
            if response.status_code == 200:
                complex_info = response.json()
                if 'complex' in complex_info:
                    complex_info = complex_info.get('complex')

                latitude = complex_info.get('latitude')
                longitude = complex_info.get('longitude')
                city = complex_info.get('city')
                country = complex_info.get('country')
                # removed the state check for countries in Europe that do not always enter states
                if not (latitude and longitude and city and country):
                    keys = ('latitude', 'longitude', 'city', 'country')
                    missing_keys = \
                        list(set(keys).difference(set(complex_info.keys())))
                    LOG.error(_LE("Complex {} is missing {}, link: {}").
                              format(complex_id, missing_keys, complex_link))
                    LOG.debug("Complex {}: {}".format(complex_id, complex_info))
                    return

                if complex_id:  # cache only if complex_id is given
                    self._aai_complex_cache[complex_id] = response.json()
                    self.complex_last_refresh_time = time.time()

                return complex_info

    def _get_regions(self):
        self._refresh_cache()
        regions = self._aai_cache.get('cloud_region', {})
        return regions

    def _get_flavors(self, cloud_owner, cloud_region_id):
        '''Fetch all flavors of a given cloud regions specified using {cloud-owner}/{cloud-region-id} composite key

        :return flavors_info json object which list of flavor nodes and its children - HPACapabilities:
        '''

        LOG.debug("Fetch all flavors and its child nodes HPACapabilities")
        flavor_path = constants.FLAVORS_URI % (cloud_owner, cloud_region_id)
        path = self._aai_versioned_path(flavor_path)
        LOG.debug("Flavors path '{}' ".format(path))

        response = self._request(path=path, context="flavors", value="all")
        if response is None:
            return
        if response.status_code == 200:
            flavors_info = response.json()
            if not flavors_info or not flavors_info["flavor"] or \
                    len(flavors_info["flavor"]) == 0:
                LOG.error(_LE("Flavor is missing in Cloud-Region {}/{}").
                          format(cloud_owner, cloud_region_id))
                return
            LOG.debug(flavors_info)
            # Remove extraneous flavor information
            return flavors_info
        else:
            LOG.error(_LE("Received Error while fetching flavors from Cloud-region {}/{}").format(cloud_owner,
                                                                                                  cloud_region_id))
            return

    def _get_aai_path_from_link(self, link):
        path = link.split(self.version, 1)
        if not path or len(path) <= 1:
            # TODO(shankar): Treat this as a critical error?
            LOG.error(_LE("A&AI version {} not found in link {}").
                      format(self.version, link))
        else:
            return "{}".format(path[1])

    def check_candidate_role(self, host_id=None):

        vnf_name_uri = '/network/generic-vnfs/?vnf-name=' + host_id + '&depth=0'
        path = self._aai_versioned_path(vnf_name_uri)

        response = self._request('get', path=path, data=None,
                                 context="vnf name")

        if response is None or not response.ok:
            return None
        body = response.json()

        generic_vnf = body.get("generic-vnf", [])

        for vnf in generic_vnf:
            related_to = "service-instance"
            search_key = "customer.global-customer-id"
            rl_data_list = self._get_aai_rel_link_data(
                data=vnf,
                related_to=related_to,
                search_key=search_key,
            )

            if len(rl_data_list) != 1:
                return None

            rl_data = rl_data_list[0]
            candidate_role_link = rl_data.get("link")

            if not candidate_role_link:
                LOG.error(_LE("Unable to get candidate role link for host id {} ").format(host_id))
                return None

            candidate_role_path = self._get_aai_path_from_link(candidate_role_link) + '/allotted-resources?depth=all'
            path = self._aai_versioned_path(candidate_role_path)

            response = self._request('get', path=path, data=None,
                                     context="candidate role")

            if response is None or not response.ok:
                return None
            body = response.json()

            response_items = body.get('allotted-resource')
            if len(response_items) > 0:
                role = response_items[0].get('role')
            return role

    def check_network_roles(self, network_role_id=None):
        # the network role query from A&AI is not using
        # the version number in the query
        network_role_uri = \
            '/network/l3-networks?network-role=' + network_role_id
        path = self._aai_versioned_path(network_role_uri)

        # This UUID is reserved by A&AI for a Conductor-specific named query.
        named_query_uid = "role-UUID"

        data = {
            "query-parameters": {
                "named-query": {
                    "named-query-uuid": named_query_uid
                }
            },
            "instance-filters": {
                "instance-filter": [
                    {
                        "l3-network": {
                            "network-role": network_role_id
                        }
                    }
                ]
            }
        }
        region_ids = set()
        response = self._request('get', path=path, data=data,
                                 context="role", value=network_role_id)
        if response is None:
            return None
        body = response.json()

        response_items = body.get('l3-network', [])

        for item in response_items:
            cloud_region_instances = self._get_aai_rel_link_data(
                data=item,
                related_to='cloud-region',
                search_key='cloud-region.cloud-region-id'
            )

            if len(cloud_region_instances) > 0:
                for r_instance in cloud_region_instances:
                    region_id = r_instance.get('d_value')
                    if region_id is not None:
                        region_ids.add(region_id)

        # return region ids that fit the role
        return region_ids

    def resolve_host_location(self, host_name):
        path = self._aai_versioned_path('/query?format=id')
        data = {"start": ["network/pnfs/pnf/" + host_name,
                          "cloud-infrastructure/pservers/pserver/" + host_name],
                "query": "query/ucpe-instance"
                }
        response = self._request('put', path=path, data=data,
                                 context="host name", value=host_name)
        if response is None or response.status_code != 200:
            return None
        body = response.json()
        results = body.get('results', [])
        complex_link = None
        for result in results:
            if "resource-type" in result and \
                    "resource-link" in result and \
                    result["resource-type"] == "complex":
                complex_link = result["resource-link"]
        if not complex_link:
            LOG.error(_LE("Unable to get a complex link for hostname {} "
                          " in response {}").format(host_name, response))
            return None
        complex_info = self._get_complex(
            complex_link=complex_link,
            complex_id=None
        )
        if complex_info:
            lat = complex_info.get('latitude')
            lon = complex_info.get('longitude')
            country = complex_info.get('country')
            if lat and lon:
                location = {"latitude": lat, "longitude": lon}
                location["country"] = country if country else None
                return location
            else:
                LOG.error(_LE("Unable to get a latitude and longitude "
                              "information for hostname {} from complex "
                              " link {}").format(host_name, complex_link))
                return None
        else:
            LOG.error(_LE("Unable to get a complex information for "
                          " hostname {} from complex "
                          " link {}").format(host_name, complex_link))
            return None

    def resolve_clli_location(self, clli_name):
        clli_uri = '/cloud-infrastructure/complexes/complex/' + clli_name
        path = self._aai_versioned_path(clli_uri)

        response = self._request('get', path=path, data=None,
                                 context="clli name", value=clli_name)
        if response is None or response.status_code != 200:
            return None

        body = response.json()

        if body:
            lat = body.get('latitude')
            lon = body.get('longitude')
            country = body.get('country')
            if lat and lon:
                location = {"latitude": lat, "longitude": lon}
                location["country"] = country if country else None
                return location
            else:
                LOG.error(_LE("Unable to get a latitude and longitude "
                              "information for CLLI code {} from complex").
                          format(clli_name))
                return None
        else:
            LOG.error(_LE("Unable to get a complex information for "
                          " clli {} from complex "
                          " link {}").format(clli_name, clli_uri))
            return None

    def get_inventory_group_pairs(self, service_description):
        pairs = list()
        path = self._aai_versioned_path(
            '/network/instance-groups/?description={}&depth=0'.format(
                service_description))
        response = self._request(path=path, context="inventory group",
                                 value=service_description)
        if response is None or response.status_code != 200:
            return
        body = response.json()
        if "instance-group" not in body:
            LOG.error(_LE("Unable to get instance groups from inventory "
                          " in response {}").format(response))
            return
        for instance_groups in body["instance-group"]:
            s_instances = self._get_aai_rel_link_data(
                data=instance_groups,
                related_to='service-instance',
                search_key='service-instance.service-instance-id'
            )
            if s_instances and len(s_instances) == 2:
                pair = list()
                for s_inst in s_instances:
                    pair.append(s_inst.get('d_value'))
                pairs.append(pair)
            else:
                LOG.error(_LE("Number of instance pairs not found to "
                              "be two: {}").format(instance_groups))
        return pairs

    def _log_multiple_item_error(self, name, service_type,
                                 related_to, search_key='',
                                 context=None, value=None):
        """Helper method to log multiple-item errors

        Used by resolve_demands
        """
        LOG.error(_LE("Demand {}, role {} has more than one {} ({})").
                  format(name, service_type, related_to, search_key))
        if context and value:
            LOG.debug("{} details: {}".format(context, value))

    def match_candidate_attribute(self, candidate, attribute_name,
                                  restricted_value, demand_name,
                                  inventory_type):
        """Check if specific candidate attribute matches the restricted value

        Used by resolve_demands
        """
        if restricted_value and restricted_value != '' and candidate[attribute_name] != restricted_value:
            LOG.info(_LI("Demand: {} "
                         "Discarded {} candidate as "
                         "it doesn't match the "
                         "{} attribute "
                         "{} ").format(demand_name,
                                       inventory_type,
                                       attribute_name,
                                       restricted_value
                                       )
                     )
            return True
        return False

    def match_vserver_attribute(self, vserver_list):

        value = None
        for i in range(0, len(vserver_list)):
            if value and \
                    value != vserver_list[i].get('d_value'):
                return False
            value = vserver_list[i].get('d_value')
        return True

    def match_inventory_attributes(self, template_attributes,
                                   inventory_attributes, candidate_id):

        for attribute_key, attribute_values in template_attributes.items():

            if attribute_key and \
                    (attribute_key == 'service-type' or attribute_key == 'equipment-role'
                     or attribute_key == 'model-invariant-id' or attribute_key == 'model-version-id'):
                continue

            match_type = 'any'
            if type(attribute_values) is dict:
                if 'any' in attribute_values:
                    attribute_values = attribute_values['any']
                elif 'not' in attribute_values:
                    match_type = 'not'
                    attribute_values = attribute_values['not']

            if match_type == 'any':
                if attribute_key not in inventory_attributes or \
                        (len(attribute_values) > 0 and inventory_attributes[attribute_key] not in attribute_values):
                    return False
            elif match_type == 'not':
                # drop the candidate when
                # 1)field exists in AAI and 2)value is not null or empty 3)value is one of those in the 'not' list
                # Remember, this means if the property is not returned at all from AAI, that still can be a candidate.
                if attribute_key in inventory_attributes and \
                        inventory_attributes[attribute_key] and \
                        inventory_attributes[attribute_key] in attribute_values:
                    return False

        return True

    def first_level_service_call(self, path, name, service_type):

        response = self._request(
            path=path, context="demand, GENERIC-VNF role",
            value="{}, {}".format(name, service_type))
        if response is None or response.status_code != 200:
            return list()  # move ahead with next requirement
        body = response.json()
        return body.get("generic-vnf", [])

    def resolve_v_server_for_candidate(self, candidate_id, location_id, vs_link, add_interfaces, demand_name,
                                       triage_translator_data):
        if not vs_link:
            LOG.error(_LE("{} VSERVER link information not "
                          "available from A&AI").format(demand_name))
            self.triage_translator.collectDroppedCandiate(candidate_id,
                                                          location_id, demand_name,
                                                          triage_translator_data,
                                                          reason="VSERVER link information not")
            return None  # move ahead with the next vnf

        if add_interfaces:
            vs_link = vs_link + '?depth=2'
        vs_path = self._get_aai_path_from_link(vs_link)
        if not vs_path:
            LOG.error(_LE("{} VSERVER path information not "
                          "available from A&AI - {}").
                      format(demand_name, vs_path))
            self.triage_translator.collectDroppedCandiate(candidate_id,
                                                          location_id, demand_name,
                                                          triage_translator_data,
                                                          reason="VSERVER path information not available from A&AI")
            return None  # move ahead with the next vnf
        path = self._aai_versioned_path(vs_path)
        response = self._request(
            path=path, context="demand, VSERVER",
            value="{}, {}".format(demand_name, vs_path))
        if response is None or response.status_code != 200:
            self.triage_translator.collectDroppedCandiate(candidate_id,
                                                          location_id, demand_name,
                                                          triage_translator_data,
                                                          reason=response.status_code)
            return None
        return response.json()

    def resolve_vf_modules_for_generic_vnf(self, candidate_id, location_id, vnf, demand_name, triage_translator_data):
        raw_path = '/network/generic-vnfs/generic-vnf/{}?depth=1'.format(vnf.get("vnf-id"))
        path = self._aai_versioned_path(raw_path)

        response = self._request('get', path=path, data=None)
        if response is None or response.status_code != 200:
            self.triage_translator.collectDroppedCandiate(candidate_id, location_id, demand_name,
                                                          triage_translator_data, reason=response)
            return None
        generic_vnf_details = response.json()

        if generic_vnf_details is None or not generic_vnf_details.get('vf-modules') \
                or not generic_vnf_details.get('vf-modules').get('vf-module'):
            self.triage_translator.collectDroppedCandiate(candidate_id, location_id, demand_name,
                                                          triage_translator_data,
                                                          reason="Generic-VNF No detailed data for VF-modules")
            return None
        else:
            return generic_vnf_details.get('vf-modules').get('vf-module')

    def resolve_cloud_regions_by_cloud_region_id(self, cloud_region_id):
        cloud_region_uri = '/cloud-infrastructure/cloud-regions' \
                           '/?cloud-region-id=' \
                           + cloud_region_id
        path = self._aai_versioned_path(cloud_region_uri)

        response = self._request('get',
                                 path=path,
                                 data=None)
        if response is None or response.status_code != 200:
            return None

        body = response.json()
        return body.get('cloud-region', [])

    def assign_candidate_existing_placement(self, candidate, existing_placement):

        """Assign existing_placement and cost parameters to candidate

        Used by resolve_demands
        """
        candidate['existing_placement'] = 'false'
        if existing_placement:
            if existing_placement.get('candidate_id') == candidate['candidate_id']:
                candidate['cost'] = self.conf.data.existing_placement_cost
                candidate['existing_placement'] = 'true'

    def resovle_conflict_id(self, conflict_identifier, candidate):

        # Initialize the conflict_id_list
        conflict_id_list = list()
        # conflict_id is separated by pipe (|)
        separator = '|'

        for conflict_element in conflict_identifier:
            # if the conflict_element is a dictionary with key = 'get_candidate_attribute',
            # then add candidate's coressponding value to conflict_id string
            if isinstance(conflict_element, dict) and 'get_candidate_attribute' in conflict_element:
                attribute_name = conflict_element.get('get_candidate_attribute')
                conflict_id_list.append(candidate[attribute_name] + separator)
            elif isinstance(conflict_element, unicode):
                conflict_id_list.append(conflict_element + separator)

        return ''.join(conflict_id_list)

    def resolve_v_server_links_for_vnf(self, vnf):
        related_to = "vserver"
        search_key = "cloud-region.cloud-owner"
        rl_data_list = self._get_aai_rel_link_data(
            data=vnf, related_to=related_to,
            search_key=search_key)
        vs_link_list = list()
        for i in range(0, len(rl_data_list)):
            vs_link_list.append(rl_data_list[i].get('link'))
        return vs_link_list

    def resolve_complex_info_link_for_v_server(self, candidate_id, v_server, cloud_owner, cloud_region_id,
                                               service_type, demand_name, triage_translator_data):
        related_to = "pserver"
        rl_data_list = self._get_aai_rel_link_data(
            data=v_server,
            related_to=related_to,
            search_key=None
        )
        if len(rl_data_list) > 1:
            self._log_multiple_item_error(
                demand_name, service_type, related_to, "item",
                "VSERVER", v_server)
            self.triage_translator.collectDroppedCandiate(candidate_id, cloud_region_id, demand_name,
                                                          triage_translator_data, reason="item VSERVER")
            return None
        rl_data = rl_data_list[0]
        ps_link = rl_data.get('link')

        # Third level query to get cloud region from pserver
        if not ps_link:
            LOG.error(_LE("{} pserver related link "
                          "not found in A&AI: {}").
                      format(demand_name, rl_data))
            # if HPA_feature is disabled
            if not self.conf.HPA_enabled:
                # Triage Tool Feature Changes
                self.triage_translator.collectDroppedCandiate(candidate_id, cloud_region_id, demand_name,
                                                              triage_translator_data, reason="ps link not found")
                return None
            else:
                if not (cloud_owner and cloud_region_id):
                    LOG.error("{} cloud-owner or cloud-region not "
                              "available from A&AI".
                              format(demand_name))
                    # Triage Tool Feature Changes
                    self.triage_translator.collectDroppedCandiate(candidate_id, cloud_region_id, demand_name,
                                                                  triage_translator_data,
                                                                  reason="Cloud owner and cloud region "
                                                                         "id not found")
                    return None  # move ahead with the next vnf
                cloud_region_uri = \
                    '/cloud-infrastructure/cloud-regions/cloud-region' \
                    '/?cloud-owner=' + cloud_owner \
                    + '&cloud-region-id=' + cloud_region_id
                path = self._aai_versioned_path(cloud_region_uri)
                response = self._request('get',
                                         path=path,
                                         data=None)
                if response is None or response.status_code != 200:
                    # Triage Tool Feature Changes
                    self.triage_translator.collectDroppedCandiate(candidate_id, cloud_region_id, demand_name,
                                                                  triage_translator_data, reason=response)
                    return None
                body = response.json()
        else:
            ps_path = self._get_aai_path_from_link(ps_link)
            if not ps_path:
                LOG.error(_LE("{} pserver path information "
                              "not found in A&AI: {}").
                          format(demand_name, ps_link))
                # Triage Tool Feature Changes
                self.triage_translator.collectDroppedCandiate(candidate_id, cloud_region_id, demand_name,
                                                              triage_translator_data, reason="ps path not found")
                return None  # move ahead with the next vnf
            path = self._aai_versioned_path(ps_path)
            response = self._request(
                path=path, context="PSERVER", value=ps_path)
            if response is None or response.status_code != 200:
                # Triage Tool Feature Changes
                self.triage_translator.collectDroppedCandiate(candidate_id, cloud_region_id, demand_name,
                                                              triage_translator_data, reason=response)
                return None
            body = response.json()

        related_to = "complex"
        search_key = "complex.physical-location-id"
        rl_data_list = self._get_aai_rel_link_data(
            data=body,
            related_to=related_to,
            search_key=search_key
        )
        if len(rl_data_list) > 1:
            if not self.match_vserver_attribute(rl_data_list):
                self._log_multiple_item_error(
                    demand_name, service_type, related_to, search_key, "PSERVER", body)
                self.triage_translator.collectDroppedCandiate(candidate_id, cloud_region_id, demand_name,
                                                              triage_translator_data, reason="PSERVER error")
                return None
        return rl_data_list[0]

    def resolve_cloud_for_vnf(self, candidate_id, location_id, vnf, service_type, demand_name, triage_translator_data):
        related_to = "vserver"
        search_keys = ["cloud-region.cloud-owner", "cloud-region.cloud-region-id"]
        cloud_info = dict()
        for search_key in search_keys:
            rl_data_list = self._get_aai_rel_link_data(
                data=vnf, related_to=related_to,
                search_key=search_key)

            if len(rl_data_list) > 1:
                if not self.match_vserver_attribute(rl_data_list):
                    self._log_multiple_item_error(
                        demand_name, service_type, related_to, search_key,
                        "VNF", vnf)
                    self.triage_translator.collectDroppedCandiate(candidate_id,
                                                                  location_id, demand_name,
                                                                  triage_translator_data,
                                                                  reason="VNF error")
                    return None
            cloud_info[search_key.split(".")[1].replace('-', '_')] = rl_data_list[0].get('d_value') if rl_data_list[
                0] else None
        cloud_info['cloud_region_version'] = self.get_cloud_region_version(cloud_info['cloud_region_id'])
        cloud_info['location_type'] = 'att_aic'
        cloud_info['location_id'] = cloud_info.pop('cloud_region_id')
        return cloud_info

    def get_cloud_region_version(self, cloud_region_id):
        if cloud_region_id:
            regions = self.resolve_cloud_regions_by_cloud_region_id(cloud_region_id)
            if regions is None:
                return None
            for region in regions:
                if "cloud-region-version" in region:
                    return self._get_version_from_string(region["cloud-region-version"])

    def resolve_global_customer_id_for_vnf(self, candidate_id, location_id, vnf, customer_id, service_type,
                                           demand_name, triage_translator_data):
        related_to = "service-instance"
        search_key = "customer.global-customer-id"
        match_key = "customer.global-customer-id"
        rl_data_list = self._get_aai_rel_link_data(
            data=vnf,
            related_to=related_to,
            search_key=search_key,
            match_dict={'key': match_key,
                        'value': customer_id}
        )
        if len(rl_data_list) > 1:
            if not self.match_vserver_attribute(rl_data_list):
                self._log_multiple_item_error(
                    demand_name, service_type, related_to, search_key, "VNF", vnf)
                self.triage_translator.collectDroppedCandiate(candidate_id, location_id,
                                                              demand_name, triage_translator_data,
                                                              reason=" match_vserver_attribute generic-vnf")
                return None
        return rl_data_list[0]

    def resolve_service_instance_id_for_vnf(self, candidate_id, location_id, vnf, customer_id, service_type,
                                            demand_name, triage_translator_data):
        related_to = "service-instance"
        search_key = "service-instance.service-instance-id"
        match_key = "customer.global-customer-id"
        rl_data_list = self._get_aai_rel_link_data(
            data=vnf,
            related_to=related_to,
            search_key=search_key,
            match_dict={'key': match_key,
                        'value': customer_id}
        )
        if len(rl_data_list) > 1:
            if not self.match_vserver_attribute(rl_data_list):
                self._log_multiple_item_error(
                    demand_name, service_type, related_to, search_key, "VNF", vnf)
                self.triage_translator.collectDroppedCandiate(candidate_id, location_id,
                                                              demand_name, triage_translator_data,
                                                              reason="multiple_item_error generic-vnf")
                return None
        return rl_data_list[0]

    def build_complex_info_for_candidate(self, candidate_id, location_id, vnf, complex_list, service_type, demand_name,
                                         triage_translator_data):
        if not complex_list or \
                len(complex_list) < 1:
            LOG.error("Complex information not "
                      "available from A&AI")
            self.triage_translator.collectDroppedCandiate(candidate_id, location_id, demand_name,
                                                          triage_translator_data,
                                                          reason="Complex information not available from A&AI")
            return

        # In the scenario where no pserver information is available
        # assumption here is that cloud-region does not span across
        # multiple complexes
        if len(complex_list) > 1:
            related_to = "complex"
            search_key = "complex.physical-location-id"
            if not self.match_vserver_attribute(complex_list):
                self._log_multiple_item_error(
                    demand_name, service_type, related_to, search_key,
                    "VNF", vnf)
                self.triage_translator.collectDroppedCandiate(candidate_id, location_id, demand_name,
                                                              triage_translator_data,
                                                              reason="Generic-vnf error")
                return

        rl_data = complex_list[0]
        complex_link = rl_data.get('link')
        complex_id = rl_data.get('d_value')

        # Final query for the complex information
        if not (complex_link and complex_id):
            LOG.debug("{} complex information not "
                      "available from A&AI - {}".
                      format(demand_name, complex_link))
            self.triage_translator.collectDroppedCandiate(candidate_id, location_id, demand_name,
                                                          triage_translator_data,
                                                          reason="Complex information not available from A&AI")
            return  # move ahead with the next vnf
        else:
            complex_info = self._get_complex(
                complex_link=complex_link,
                complex_id=complex_id
            )
            if not complex_info:
                LOG.debug("{} complex information not "
                          "available from A&AI - {}".
                          format(demand_name, complex_link))
                self.triage_translator.collectDroppedCandiate(candidate_id, location_id, demand_name,
                                                              triage_translator_data,
                                                              reason="Complex information not available from A&AI")
                return  # move ahead with the next vnf

            complex_info = self.build_complex_dict(complex_info, '')
            return complex_info

    def resolve_demands(self, demands, plan_info, triage_translator_data):
        """Resolve demands into inventory candidate lists"""

        self.triage_translator.getPlanIdNAme(plan_info['plan_name'], plan_info['plan_id'], triage_translator_data)

        resolved_demands = {}
        for name, requirements in demands.items():
            self.triage_translator.addDemandsTriageTranslator(name, triage_translator_data)
            resolved_demands[name] = []
            for requirement in requirements:
                inventory_type = requirement.get('inventory_type').lower()
                service_subscription = requirement.get('service_subscription')
                candidate_uniqueness = requirement.get('unique', 'true')
                filtering_attributes = requirement.get('filtering_attributes')
                passthrough_attributes = requirement.get('passthrough_attributes')
                default_attributes = requirement.get('default_attributes')
                # TODO(XYZ): may need to support multiple service_type and customer_id in the futrue

                # TODO(XYZ): make it consistent for dash and underscore
                if filtering_attributes:
                    # catch equipment-role and service-type from template
                    equipment_role = filtering_attributes.get('equipment-role')
                    service_type = filtering_attributes.get('service-type')
                    if equipment_role:
                        service_type = equipment_role
                    # catch global-customer-id and customer-id from template
                    global_customer_id = filtering_attributes.get('global-customer-id')
                    customer_id = filtering_attributes.get('customer-id')
                    if global_customer_id:
                        customer_id = global_customer_id

                    model_invariant_id = filtering_attributes.get('model-invariant-id')
                    model_version_id = filtering_attributes.get('model-version-id')
                    service_role = filtering_attributes.get('service-role')
                # For earlier
                else:
                    service_type = equipment_role = requirement.get('service_type')
                    customer_id = global_customer_id = requirement.get('customer_id')
                # region_id is OPTIONAL. This will restrict the initial
                # candidate set to come from the given region id
                restricted_region_id = requirement.get('region')
                restricted_complex_id = requirement.get('complex')
                # Used for order locking feature
                # by defaut, conflict id is the combination of candidate id, service type and vnf-e2e-key
                conflict_identifier = requirement.get('conflict_identifier')
                # VLAN fields
                vlan_key = requirement.get('vlan_key')
                port_key = requirement.get('port_key')

                # get required candidates from the demand
                required_candidates = requirement.get("required_candidates")

                # get existing_placement from the demand
                existing_placement = requirement.get("existing_placement")

                if required_candidates:
                    resolved_demands['required_candidates'] = \
                        required_candidates

                # get excluded candidate from the demand
                excluded_candidates = requirement.get("excluded_candidates")

                # service_resource_id is OPTIONAL and is
                # transparent to Conductor
                service_resource_id = requirement.get('service_resource_id') \
                    if requirement.get('service_resource_id') else ''

                if inventory_type == 'cloud':
                    # load region candidates from cache
                    regions = self._get_regions()
                    if not regions or len(regions) < 1:
                        LOG.debug("Region information is not available in cache")
                    for region_id, region in regions.items():
                        # Pick only candidates from the restricted_region
                        info = Candidate.build_candidate_info('aai', inventory_type,
                                                              self.conf.data.cloud_candidate_cost,
                                                              candidate_uniqueness, region_id, service_resource_id)
                        cloud = self.resolve_cloud_for_region(region, region_id)
                        complex_info = self.build_complex_dict(region['complex'], inventory_type)
                        flavors = self.resolve_flavors_for_region(region['flavors'])
                        other = dict()
                        other['vim-id'] = self.get_vim_id(cloud['cloud_owner'], cloud['location_id'])
                        if self.check_sriov_automation(cloud['cloud_region_version'], name, info['candidate_id']):
                            other['sriov_automation'] = 'true'
                        else:
                            other['sriov_automation'] = 'false'
                        cloud_candidate = Cloud(info=info, cloud_region=cloud, complex=complex_info, flavors=flavors,
                                                additional_fields=other)
                        candidate = cloud_candidate.convert_nested_dict_to_dict()

                        cloud_region_attr = dict()
                        cloud_region_attr['cloud-owner'] = region['cloud_owner']
                        cloud_region_attr['cloud-region-version'] = region['cloud_region_version']
                        cloud_region_attr['cloud-type'] = region['cloud_type']
                        cloud_region_attr['cloud-zone'] = region['cloud_zone']
                        cloud_region_attr['complex-name'] = region['complex_name']
                        cloud_region_attr['physical-location-id'] = region['physical_location_id']

                        if filtering_attributes and (not self.match_inventory_attributes(filtering_attributes,
                                                                                         cloud_region_attr,
                                                                                         candidate['candidate_id'])):
                            self.triage_translator.collectDroppedCandiate(candidate['candidate_id'],
                                                                          candidate['location_id'], name,
                                                                          triage_translator_data,
                                                                          reason='attributes and match invetory '
                                                                                 'attributes')
                            continue

                        if conflict_identifier:
                            candidate['conflict_id'] = self.resovle_conflict_id(conflict_identifier, candidate)

                        if not self.match_region(candidate, restricted_region_id, restricted_complex_id, name,
                                                 triage_translator_data):
                            continue

                        self.assign_candidate_existing_placement(candidate, existing_placement)

                        # Pick only candidates not in the excluded list, if excluded candidate list is provided
                        if excluded_candidates and self.match_candidate_by_list(candidate, excluded_candidates, True,
                                                                                name, triage_translator_data):
                            continue

                        # Pick only candidates in the required list, if required candidate list is provided
                        if required_candidates and not self.match_candidate_by_list(candidate, required_candidates,
                                                                                    False, name,
                                                                                    triage_translator_data):
                            continue

                        self.add_passthrough_attributes(candidate, passthrough_attributes, name)
                        # add candidate to demand candidates
                        resolved_demands[name].append(candidate)
                        LOG.debug(">>>>>>> Candidate <<<<<<<")
                        LOG.debug(json.dumps(candidate, indent=4))

                elif (inventory_type == 'service') and customer_id:
                    # First level query to get the list of generic vnfs
                    vnf_by_model_invariant = list()
                    if filtering_attributes and model_invariant_id:

                        raw_path = '/network/generic-vnfs/' \
                                   '?model-invariant-id={}&depth=0'.format(model_invariant_id)
                        if model_version_id:
                            raw_path = '/network/generic-vnfs/' \
                                       '?model-invariant-id={}&model-version-id={}&depth=0'.format(model_invariant_id,
                                                                                                   model_version_id)
                        path = self._aai_versioned_path(raw_path)
                        vnf_by_model_invariant = self.first_level_service_call(path, name, service_type)

                    vnf_by_service_type = list()
                    if service_type or equipment_role:
                        path = self._aai_versioned_path(
                            '/network/generic-vnfs/'
                            '?equipment-role={}&depth=0'.format(service_type))
                        vnf_by_service_type = self.first_level_service_call(path, name, service_type)

                    generic_vnf = vnf_by_model_invariant + vnf_by_service_type
                    vnf_dict = dict()

                    for vnf in generic_vnf:
                        # if this vnf already appears, skip it
                        vnf_id = vnf.get('vnf-id')
                        if vnf_id in vnf_dict:
                            continue
                        # add vnf (with vnf_id as key) to the dictionary
                        vnf_dict[vnf_id] = vnf
                        vnf_info = dict()
                        vnf_info['host_id'] = vnf.get("vnf-name")
                        vlan_info = self.build_vlan_info(vlan_key, port_key)
                        cloud = self.resolve_cloud_for_vnf('', '', vnf, service_type, name, triage_translator_data)
                        if cloud['location_id'] is None or cloud['cloud_owner'] is None or \
                                cloud['cloud_region_version'] is None:
                            continue

                        rl_data = self.resolve_global_customer_id_for_vnf('', cloud['location_id'], vnf, customer_id,
                                                                          service_type, name, triage_translator_data)
                        if rl_data is None:
                            continue
                        else:
                            vs_cust_id = rl_data.get('d_value')
                        rl_data = self.resolve_service_instance_id_for_vnf('', cloud['location_id'], vnf, customer_id,
                                                                           service_type, name, triage_translator_data)
                        if rl_data is None:
                            continue
                        else:
                            vs_service_instance_id = rl_data.get('d_value')

                        # INFO
                        if vs_cust_id and vs_cust_id == customer_id:
                            info = Candidate.build_candidate_info('aai', inventory_type,
                                                                  self.conf.data.service_candidate_cost,
                                                                  candidate_uniqueness, vs_service_instance_id,
                                                                  service_resource_id)
                        else:  # vserver is for a different customer
                            self.triage_translator.collectDroppedCandiate('', cloud['location_id'], name,
                                                                          triage_translator_data,
                                                                          reason="vserver is for a different customer")
                            continue
                        # Added vim-id for short-term workaround
                        other = dict()
                        other['vim-id'] = self.get_vim_id(cloud['cloud_owner'], cloud['location_id'])
                        other['sriov_automation'] = 'true' if self.check_sriov_automation(
                            cloud['cloud_region_version'], name, info['candidate_id']) else 'false'

                        # Second level query to get the pserver from vserver
                        complex_list = list()
                        for complex_link in self.resolve_v_server_and_complex_link_for_vnf(info['candidate_id'], cloud,
                                                                                           vnf, name,
                                                                                           triage_translator_data,
                                                                                           service_type):
                            complex_list.append(complex_link[1])
                        complex_info = self.build_complex_info_for_candidate(info['candidate_id'],
                                                                             cloud['location_id'], vnf,
                                                                             complex_list, service_type, name,
                                                                             triage_translator_data)
                        if "complex_name" not in complex_info:
                            continue

                        service_candidate = Service(info=info, cloud_region=cloud, complex=complex_info,
                                                    generic_vnf=vnf_info, additional_fields=other, vlan=vlan_info)
                        candidate = service_candidate.convert_nested_dict_to_dict()

                        # add specifal parameters for comparsion
                        vnf['global-customer-id'] = customer_id
                        vnf['customer-id'] = customer_id
                        vnf['cloud-region-id'] = cloud.get('cloud_region_id')
                        vnf['physical-location-id'] = complex_info.get('physical_location_id')

                        if filtering_attributes and not self.match_inventory_attributes(filtering_attributes, vnf,
                                                                                        candidate['candidate_id']):
                            self.triage_translator.collectDroppedCandiate(candidate['candidate_id'],
                                                                          candidate['location_id'], name,
                                                                          triage_translator_data,
                                                                          reason="attibute check error")
                            continue
                        self.assign_candidate_existing_placement(candidate, existing_placement)

                        # Pick only candidates not in the excluded list
                        # if excluded candidate list is provided
                        if excluded_candidates and self.match_candidate_by_list(candidate, excluded_candidates, True,
                                                                                name, triage_translator_data):
                            continue

                        # Pick only candidates in the required list
                        # if required candidate list is provided
                        if required_candidates and not self.match_candidate_by_list(candidate, required_candidates,
                                                                                    False, name,
                                                                                    triage_translator_data):
                            continue

                        # add the candidate to the demand
                        # Pick only candidates from the restricted_region
                        # or restricted_complex
                        if not self.match_region(candidate, restricted_region_id, restricted_complex_id, name,
                                                 triage_translator_data):
                            continue
                        else:
                            self.add_passthrough_attributes(candidate, passthrough_attributes, name)
                            resolved_demands[name].append(candidate)
                            LOG.debug(">>>>>>> Candidate <<<<<<<")
                            LOG.debug(json.dumps(candidate, indent=4))

                elif (inventory_type == 'vfmodule') and customer_id:

                    # First level query to get the list of generic vnfs
                    vnf_by_model_invariant = list()
                    if filtering_attributes and model_invariant_id:

                        raw_path = '/network/generic-vnfs/' \
                                   '?model-invariant-id={}&depth=0'.format(model_invariant_id)
                        if model_version_id:
                            raw_path = '/network/generic-vnfs/' \
                                       '?model-invariant-id={}&model-version-id={}&depth=0'.format(model_invariant_id,
                                                                                                   model_version_id)
                        path = self._aai_versioned_path(raw_path)
                        vnf_by_model_invariant = self.first_level_service_call(path, name, service_type)

                    vnf_by_service_type = list()
                    if service_type or equipment_role:
                        path = self._aai_versioned_path('/network/generic-vnfs/'
                                                        '?equipment-role={}&depth=0'.format(service_type))
                        vnf_by_service_type = self.first_level_service_call(path, name, service_type)

                    generic_vnf = vnf_by_model_invariant + vnf_by_service_type
                    vnf_dict = dict()

                    for vnf in generic_vnf:
                        # if this vnf already appears, skip it
                        vnf_id = vnf.get('vnf-id')
                        if vnf_id in vnf_dict:
                            continue
                        # add vnf (with vnf_id as key) to the dictionary
                        vnf_dict[vnf_id] = vnf

                        # INFO
                        info = Candidate.build_candidate_info('aai', inventory_type,
                                                              self.conf.data.service_candidate_cost,
                                                              candidate_uniqueness, "", service_resource_id)
                        # VLAN INFO
                        vlan_info = self.build_vlan_info(vlan_key, port_key)
                        # Generic VNF Info
                        vnf_info = self.get_vnf_info(vnf)

                        rl_data = self.resolve_global_customer_id_for_vnf('', '', vnf, customer_id,
                                                                          service_type, name, triage_translator_data)
                        if rl_data is None:
                            continue
                        else:
                            vs_cust_id = rl_data.get('d_value')

                        rl_data = self.resolve_service_instance_id_for_vnf('', '', vnf, customer_id,
                                                                           service_type, name, triage_translator_data)
                        if rl_data is None:
                            continue
                        else:
                            vs_service_instance_id = rl_data.get('d_value')

                        service_info = dict()
                        if vs_cust_id and vs_cust_id == customer_id:
                            service_info['service_instance_id'] = vs_service_instance_id
                        else:  # vserver is for a different customer
                            self.triage_translator.collectDroppedCandiate('', '', name,
                                                                          triage_translator_data,
                                                                          reason="candidate is for a different"
                                                                                 " customer")
                            continue

                        vf_modules_list = self.resolve_vf_modules_for_generic_vnf('', '', vnf, name,
                                                                                  triage_translator_data)
                        if vf_modules_list is None:
                            continue

                        for vf_module in vf_modules_list:
                            # for vfmodule demands we allow to have vfmodules from different cloud regions
                            info['candidate_id'] = vf_module.get("vf-module-id")
                            vf_module_info = self.get_vf_module(vf_module)
                            cloud = self.resolve_cloud_for_vnf(info['candidate_id'], '', vf_module, service_type, name,
                                                               triage_translator_data)
                            if cloud['location_id'] is None or cloud['cloud_owner'] is None or \
                                    cloud['cloud_region_version'] is None:
                                continue

                            # OTHER - Added vim-id for short-term workaround
                            other = dict()
                            other['vim-id'] = self.get_vim_id(cloud['cloud_owner'], cloud['location_id'])
                            other['sriov_automation'] = 'true' if self.check_sriov_automation(
                                cloud['cloud_region_version'], name, info['candidate_id']) else 'false'

                            # Second level query to get the pserver from vserver
                            vserver_info = dict()
                            vserver_info['vservers'] = list()
                            complex_list = list()
                            for v_server, complex_link in \
                                    self.resolve_v_server_and_complex_link_for_vnf(info['candidate_id'],
                                                                                   cloud, vnf, name,
                                                                                   triage_translator_data,
                                                                                   service_type):
                                complex_list.append(complex_link)
                                candidate_vserver = dict()
                                candidate_vserver['vserver-id'] = v_server.get('vserver-id')
                                candidate_vserver['vserver-name'] = v_server.get('vserver-name')
                                l_interfaces = self.get_l_interfaces_from_vserver(info['candidate_id'],
                                                                                  cloud['location_id'],
                                                                                  v_server, name,
                                                                                  triage_translator_data)
                                if l_interfaces:
                                    candidate_vserver['l-interfaces'] = l_interfaces
                                else:
                                    continue
                                vserver_info['vservers'].append(candidate_vserver)

                            # COMPLEX
                            complex_info = self.build_complex_info_for_candidate(info['candidate_id'],
                                                                                 cloud['location_id'], vnf,
                                                                                 complex_list, service_type, name,
                                                                                 triage_translator_data)
                            if complex_info.get("complex_name") is None:
                                continue

                            vf_module_candidate = VfModule(complex=complex_info, info=info, generic_vnf=vnf_info,
                                                           cloud_region=cloud, service_instance=service_info,
                                                           vf_module=vf_module_info, vserver=vserver_info,
                                                           additional_fields=other, vlan=vlan_info)
                            candidate = vf_module_candidate.convert_nested_dict_to_dict()

                            # add vf-module parameters for filtering
                            vnf_vf_module_inventory = copy.deepcopy(vnf)
                            vnf_vf_module_inventory.update(vf_module)
                            # add specifal parameters for comparsion
                            vnf_vf_module_inventory['global-customer-id'] = customer_id
                            vnf_vf_module_inventory['customer-id'] = customer_id
                            vnf_vf_module_inventory['cloud-region-id'] = cloud.get('location_id')
                            vnf_vf_module_inventory['physical-location-id'] = complex_info.get('physical_location_id')
                            vnf_vf_module_inventory['service_instance_id'] = vs_service_instance_id

                            if filtering_attributes and not self.match_inventory_attributes(filtering_attributes,
                                                                                            vnf_vf_module_inventory,
                                                                                            candidate['candidate_id']):
                                self.triage_translator.collectDroppedCandiate(candidate['candidate_id'],
                                                                              candidate['location_id'], name,
                                                                              triage_translator_data,
                                                                              reason="attibute check error")
                                continue
                            self.assign_candidate_existing_placement(candidate, existing_placement)

                            # Pick only candidates not in the excluded list
                            # if excluded candidate list is provided
                            if excluded_candidates and self.match_candidate_by_list(candidate, excluded_candidates,
                                                                                    True,
                                                                                    name, triage_translator_data):
                                continue

                            # Pick only candidates in the required list
                            # if required candidate list is provided
                            if required_candidates and not self.match_candidate_by_list(candidate, required_candidates,
                                                                                        False, name,
                                                                                        triage_translator_data):
                                continue

                            # add the candidate to the demand
                            # Pick only candidates from the restricted_region
                            # or restricted_complex
                            if not self.match_region(candidate, restricted_region_id, restricted_complex_id, name,
                                                     triage_translator_data):
                                continue
                            else:
                                self.add_passthrough_attributes(candidate, passthrough_attributes, name)
                                resolved_demands[name].append(candidate)
                                LOG.debug(">>>>>>> Candidate <<<<<<<")
                                with open("vf.log", mode='w') as log_file:
                                    log_file.write(">>>>>>>Vf Candidate <<<<<<<")
                                    log_file.write(json.dumps(candidate, indent=4))
                                LOG.debug(json.dumps(candidate, indent=4))

                elif inventory_type == 'transport' \
                        and customer_id and service_type and \
                        service_subscription and service_role:

                    path = self._aai_versioned_path('business/customers/customer/{}/service-subscriptions/'
                                                    'service-subscription/{}/service-instances'
                                                    '?service-type={}&service-role={}'.format(customer_id,
                                                                                              service_subscription,
                                                                                              service_type,
                                                                                              service_role))
                    response = self._request('get', path=path, data=None)
                    if response is None or response.status_code != 200:
                        self.triage_translator.collectDroppedCandiate("", "", name,
                                                                      triage_translator_data,
                                                                      reason=response.status_code)
                        continue
                    body = response.json()
                    transport_vnfs = body.get('service-instance', [])

                    for vnf in transport_vnfs:
                        # create a default candidate
                        other = dict()
                        other['location_id'] = ''
                        other['location_type'] = 'att_aic'
                        # INFO
                        vnf_service_instance_id = vnf.get('service-instance-id')
                        if vnf_service_instance_id:
                            info = Candidate.build_candidate_info('aai', inventory_type,
                                                                  self.conf.data.transport_candidate_cost,
                                                                  candidate_uniqueness, vnf_service_instance_id,
                                                                  service_resource_id)
                        else:
                            self.triage_translator.collectDroppedCandiate('', other['location_id'], name,
                                                                          triage_translator_data,
                                                                          reason="service-instance-id error ")
                            continue

                        # ZONE
                        zone_info = dict()
                        zone = self.resolve_zone_for_vnf(info['candidate_id'], other['location_id'], vnf, name,
                                                         triage_translator_data)
                        if zone:
                            zone_info['zone_id'] = zone.get('zone-id')
                            zone_info['zone_name'] = zone.get('zone-name')
                        else:
                            continue

                        # COMPLEX
                        related_to = "complex"
                        search_key = "complex.physical-location-id"
                        rel_link_data_list = self._get_aai_rel_link_data(
                            data=zone,
                            related_to=related_to,
                            search_key=search_key
                        )

                        if len(rel_link_data_list) > 1:
                            self.triage_translator.collectDroppedCandiate(info['candidate_id'], other['location_id'],
                                                                          name, triage_translator_data,
                                                                          reason="rel_link_data_list error")

                            continue
                        rel_link_data = rel_link_data_list[0]
                        complex_id = rel_link_data.get("d_value")
                        complex_link = rel_link_data.get('link')

                        if not (complex_link and complex_id):
                            LOG.debug("{} complex information not "
                                      "available from A&AI - {}".
                                      format(name, complex_link))
                            self.triage_translator.collectDroppedCandiate(info['candidate_id'], other['location_id'],
                                                                          name, triage_translator_data,
                                                                          reason="complex information not available "
                                                                                 "from A&AI")
                            continue
                        else:
                            complex_info = self._get_complex(
                                complex_link=complex_link,
                                complex_id=complex_id
                            )
                            if not complex_info:
                                LOG.debug("{} complex information not "
                                          "available from A&AI - {}".
                                          format(name, complex_link))
                                self.triage_translator.collectDroppedCandiate(info['candidate_id'],
                                                                              other['location_id'], name,
                                                                              triage_translator_data,
                                                                              reason="complex information not "
                                                                                     "available from A&AI")
                                continue  # move ahead with the next vnf

                            complex_info = self.build_complex_dict(complex_info, inventory_type)
                            transport_candidate = Transport(info=info, zone=zone_info, complex=complex_info,
                                                            additional_fiels=other)
                            candidate = transport_candidate.convert_nested_dict_to_dict()

                            self.add_passthrough_attributes(candidate, passthrough_attributes, name)
                            # add candidate to demand candidates
                            resolved_demands[name].append(candidate)

                elif inventory_type == 'nssi' or inventory_type == 'nsi':
                    if filtering_attributes and model_invariant_id:
                        second_level_match = aai_utils.get_first_level_and_second_level_filter(filtering_attributes,
                                                                                               "service_instance")
                        aai_response = self.get_nxi_candidates(filtering_attributes)
                        resolved_demands[name].extend(self.filter_nxi_candidates(aai_response, second_level_match,
                                                                                 default_attributes,
                                                                                 candidate_uniqueness, inventory_type))

                else:
                    LOG.error("Unknown inventory_type "
                              " {}".format(inventory_type))
        return resolved_demands

    @staticmethod
    def build_complex_dict(aai_complex, inv_type):
        complex_info = dict()
        valid_keys = ['physical-location-id', 'complex-name', 'latitude', 'longitude', 'state', 'country', 'city',
                      'region']
        # for cloud type, complex_id instead of physical-location-id - note
        if inv_type == "cloud":
            for valid_key in valid_keys:
                if '-' in valid_key:
                    complex_info[valid_key.replace('-', '_')] = aai_complex.get('complex_id') \
                        if valid_key == 'physical-location-id' else \
                        aai_complex.get(valid_key.replace('-', '_'))
                else:
                    complex_info[valid_key] = aai_complex.get(valid_key)
        else:
            for valid_key in valid_keys:
                if '-' in valid_key:
                    complex_info[valid_key.replace('-', '_')] = aai_complex.get(valid_key)
                else:
                    complex_info[valid_key] = aai_complex.get(valid_key)
        return complex_info

    @staticmethod
    def build_vlan_info(vlan_key, port_key):
        vlan_info = dict()
        vlan_info['vlan_key'] = vlan_key
        vlan_info['port_key'] = port_key
        return vlan_info

    def resolve_flavors_for_region(self, flavors_obj):
        if self.conf.HPA_enabled:
            flavors = dict()
            flavors['flavors'] = flavors_obj
        return flavors

    def resolve_v_server_and_complex_link_for_vnf(self, candidate_id, cloud, vnf, name, triage_translator_data,
                                                  service_type):
        vs_link_list = self.resolve_v_server_links_for_vnf(vnf)
        for vs_link in vs_link_list:
            body = self.resolve_v_server_for_candidate(candidate_id, cloud['location_id'],
                                                       vs_link, True, name, triage_translator_data)
            if body is None:
                continue
            rl_data = self.resolve_complex_info_link_for_v_server(candidate_id, body,
                                                                  cloud['cloud_owner'], cloud['location_id'],
                                                                  service_type, name, triage_translator_data)
            if rl_data is None:
                continue
            yield body, rl_data

    def get_l_interfaces_from_vserver(self, candidate_id, location_id, v_server, name, triage_translator_data):
        if not v_server.get('l-interfaces') or not v_server.get('l-interfaces').get('l-interface'):
            self.triage_translator.collectDroppedCandiate(candidate_id,
                                                          location_id, name,
                                                          triage_translator_data,
                                                          reason="VF-server interfaces error")
            return None
        else:
            l_interfaces = v_server.get('l-interfaces').get('l-interface')
            l_interfaces_list = list()

            for l_interface in l_interfaces:
                vserver_interface = dict()
                vserver_interface['interface-id'] = l_interface.get('interface-id')
                vserver_interface['interface-name'] = l_interface.get('interface-name')
                vserver_interface['macaddr'] = l_interface.get('macaddr')
                vserver_interface['network-id'] = l_interface.get('network-name')
                vserver_interface['network-name'] = ''
                vserver_interface['ipv4-addresses'] = list()
                vserver_interface['ipv6-addresses'] = list()

                if l_interface.get('l3-interface-ipv4-address-list'):
                    for ip_address_info in l_interface.get('l3-interface-ipv4-address-list'):
                        vserver_interface['ipv4-addresses']. \
                            append(ip_address_info.get('l3-interface-ipv4-address'))

                if l_interface.get('l3-interface-ipv6-address-list'):
                    for ip_address_info in l_interface.get('l3-interface-ipv6-address-list'):
                        vserver_interface['ipv6-addresses']. \
                            append(ip_address_info.get('l3-interface-ipv6-address'))

                l_interfaces_list.append(vserver_interface)
            return l_interfaces_list

    @staticmethod
    def get_vnf_info(vnf):
        # some validation should happen
        vnf_info = dict()
        vnf_info['host_id'] = vnf.get("vnf-name")
        vnf_info['nf-name'] = vnf.get("vnf-name")
        vnf_info['nf-id'] = vnf.get("vnf-id")
        vnf_info['nf-type'] = 'vnf'
        vnf_info['vnf-type'] = vnf.get("vnf-type")
        vnf_info['ipv4-oam-address'] = vnf.get("ipv4-oam-address") if vnf.get("ipv4-oam-address") else ""
        vnf_info['ipv6-oam-address'] = vnf.get("ipv6-oam-address") if vnf.get("ipv6-oam-address") else ""
        return vnf_info

    @staticmethod
    def resolve_cloud_for_region(region, region_id):
        cloud = dict()
        valid_keys = ['cloud_owner', 'cloud_region_version', 'location_id']
        for valid_key in valid_keys:
            cloud[valid_key] = region.get(valid_key) if not valid_key == 'location_id' else region_id
        cloud['location_type'] = 'att_aic'
        return cloud

    @staticmethod
    def get_vf_module(vf_module):
        vf_module_info = dict()
        vf_module_info['vf-module-name'] = vf_module.get("vf-module-name")
        vf_module_info['vf-module-id'] = vf_module.get("vf-module-id")
        return vf_module_info

    def get_vim_id(self, cloud_owner, cloud_region_id):
        if self.conf.HPA_enabled:
            return cloud_owner + '_' + cloud_region_id

    @staticmethod
    def add_passthrough_attributes(candidate, passthrough_attributes, demand_name):
        if passthrough_attributes is None:
            return
        if len(passthrough_attributes.items()) > 0:
            candidate['passthrough_attributes'] = dict()
            for key, value in passthrough_attributes.items():
                candidate['passthrough_attributes'][key] = value

    def resolve_zone_for_vnf(self, candidate_id, location_id, vnf, name, triage_translator_data):
        related_to = "zone"
        zone_link = self._get_aai_rel_link(
            data=vnf, related_to=related_to)
        if not zone_link:
            LOG.error("Zone information not available from A&AI for transport candidates")
            self.triage_translator.collectDroppedCandiate(candidate_id, location_id,
                                                          name, triage_translator_data,
                                                          reason="Zone information not available from A&AI for "
                                                                 "transport candidates")
            return None
        zone_aai_path = self._get_aai_path_from_link(zone_link)
        response = self._request('get', path=zone_aai_path, data=None)
        if response is None or response.status_code != 200:
            self.triage_translator.collectDroppedCandiate(candidate_id, location_id, name,
                                                          triage_translator_data,
                                                          reason=response.status_code)
            return None
        body = response.json()
        return body

    def match_region(self, candidate, restricted_region_id, restricted_complex_id, demand_name,
                     triage_translator_data):
        if self.match_candidate_attribute(
                candidate,
                "location_id",
                restricted_region_id,
                demand_name,
                candidate.get('inventory_type')) or \
                self.match_candidate_attribute(
                    candidate,
                    "physical_location_id",
                    restricted_complex_id,
                    demand_name,
                    candidate.get('inventory_type')):
            self.triage_translator.collectDroppedCandiate(candidate['candidate_id'], candidate['location_id'],
                                                          demand_name, triage_translator_data,
                                                          reason="candidate region does not match")
            return False
        else:
            return True

    def match_candidate_by_list(self, candidate, candidates_list, exclude, demand_name, triage_translator_data):
        has_candidate = False
        if candidates_list:
            for list_candidate in candidates_list:
                if list_candidate \
                        and list_candidate.get('inventory_type') \
                        == candidate.get('inventory_type'):
                    if isinstance(list_candidate.get('candidate_id'), list):
                        for candidate_id in list_candidate.get('candidate_id'):
                            if candidate_id == candidate.get('candidate_id'):
                                has_candidate = True
                                break
                    else:
                        raise Exception("Invalid candidate id list format")
                    if has_candidate:
                        break

        if not exclude:
            if not has_candidate:
                self.triage_translator.collectDroppedCandiate(candidate['candidate_id'], candidate['location_id'],
                                                              demand_name, triage_translator_data,
                                                              reason="has_required_candidate candidate")
        elif has_candidate:
            self.triage_translator.collectDroppedCandiate(candidate['candidate_id'], candidate['location_id'],
                                                          demand_name, triage_translator_data,
                                                          reason="excluded candidate")
        return has_candidate

    def match_hpa(self, candidate, features):
        """Match HPA features requirement with the candidate flavors """
        hpa_provider = hpa_utils.HpaMatchProvider(candidate, features)
        if hpa_provider.init_verify():
            directives = hpa_provider.match_flavor()
        else:
            directives = None
        return directives

    def get_nxi_candidates(self, filtering_attributes):
        raw_path = 'nodes/service-instances' + aai_utils.add_query_params_and_depth(filtering_attributes, "2")
        path = self._aai_versioned_path(raw_path)
        aai_response = self._request('get', path, data=None)

        if aai_response is None or aai_response.status_code != 200:
            return None
        if aai_response.json():
            return aai_response.json()

    def filter_nxi_candidates(self, response_body, filtering_attributes, default_attributes, candidate_uniqueness,
                              type):
        candidates = list()
        if response_body is not None:
            nxi_instances = response_body.get("service-instance", [])

            for nxi_instance in nxi_instances:
                inventory_attributes = aai_utils.get_inv_values_for_second_level_filter(filtering_attributes,
                                                                                        nxi_instance)
                nxi_info = aai_utils.get_instance_info(nxi_instance)
                if not filtering_attributes or \
                        self.match_inventory_attributes(filtering_attributes, inventory_attributes,
                                                        nxi_instance.get('service-instance-id')):
                    if type == 'nssi':
                        profiles = nxi_instance.get('slice-profiles').get('slice-profile')
                        cost = self.conf.data.nssi_candidate_cost
                    elif type == 'nsi':
                        profiles = nxi_instance.get('service-profiles').get('service-profile')
                        cost = self.conf.data.nsi_candidate_cost
                    for profile in profiles:
                        profile_id = profile.get('profile-id')
                        info = Candidate.build_candidate_info('aai', type, cost, candidate_uniqueness, profile_id)
                        profile_info = aai_utils.convert_hyphen_to_under_score(profile)
                        nxi_candidate = NxI(instance_info=nxi_info, profile_info=profile_info, info=info,
                                            default_fields=aai_utils.convert_hyphen_to_under_score(default_attributes))
                        candidate = nxi_candidate.convert_nested_dict_to_dict()
                        candidates.append(candidate)
        return candidates
