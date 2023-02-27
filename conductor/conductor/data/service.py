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

# import json
# import os

import conductor.common.prometheus_metrics as PC
import cotyledon
from conductor import messaging
# from conductor import __file__ as conductor_root
from conductor.common.music import messaging as music_messaging
from conductor.common.utils import conductor_logging_util as log_util
from conductor.data.plugins.inventory_provider.base import InventoryProviderBase as Base
from conductor.data.plugins.inventory_provider import extensions as ip_ext
from conductor.data.plugins.service_controller import extensions as sc_ext
from conductor.data.plugins.vim_controller import extensions as vc_ext
from conductor.i18n import _LE, _LI, _LW
from oslo_config import cfg
from oslo_log import log

# from stevedore import driver
# from conductor.solver.resource import region
# from conductor.solver.resource import service

LOG = log.getLogger(__name__)

CONF = cfg.CONF

DATA_OPTS = [
    cfg.IntOpt('workers',
               default=1,
               min=1,
               help='Number of workers for data service. '
                    'Default value is 1.'),
    cfg.BoolOpt('concurrent',
                default=False,
                help='Set to True when data will run in active-active '
                     'mode. When set to False, data will flush any abandoned '
                     'messages at startup.'),
    cfg.FloatOpt('existing_placement_cost',
                 default=-8000.0,
                 help='Default value is -8000, which is the diameter of the earth.The distance cannot larger than '
                      'this value'),
    cfg.FloatOpt('cloud_candidate_cost',
                 default=2.0),
    cfg.FloatOpt('service_candidate_cost',
                 default=1.0),
    cfg.FloatOpt('nssi_candidate_cost',
                 default=1.0),
    cfg.FloatOpt('nsi_candidate_cost',
                 default=1.0),
    cfg.FloatOpt('nst_candidate_cost',
                 default=1.0),
    cfg.FloatOpt('nsst_candidate_cost',
                 default=1.0),
]

CONF.register_opts(DATA_OPTS, group='data')


class DataServiceLauncher(object):
    """Listener for the data service."""

    def __init__(self, conf):
        """Initializer."""

        self.conf = conf

        # Initialize Prometheus metrics Endpoint
        # Data service uses index 0
        PC._init_metrics(0)
        self.init_extension_managers(conf)

    def init_extension_managers(self, conf):
        """Initialize extension managers."""
        self.ip_ext_manager = (ip_ext.Manager(conf, 'conductor.inventory_provider.plugin'))
        self.ip_ext_manager.initialize()
        self.vc_ext_manager = (vc_ext.Manager(conf, 'conductor.vim_controller.plugin'))
        self.vc_ext_manager.initialize()
        self.sc_ext_manager = (sc_ext.Manager(conf, 'conductor.service_controller.plugin'))
        self.sc_ext_manager.initialize()

    def run(self):
        transport = messaging.get_transport(self.conf)
        if transport:
            topic = "data"
            target = music_messaging.Target(topic=topic)
            endpoints = [DataEndpoint(self.ip_ext_manager,
                                      self.vc_ext_manager,
                                      self.sc_ext_manager), ]
            flush = not self.conf.data.concurrent
            kwargs = {'transport': transport,
                      'target': target,
                      'endpoints': endpoints,
                      'flush': flush, }
            svcmgr = cotyledon.ServiceManager()
            svcmgr.add(music_messaging.RPCService,
                       workers=self.conf.data.workers,
                       args=(self.conf,), kwargs=kwargs)
            svcmgr.run()


class DataEndpoint(object):
    def __init__(self, ip_ext_manager, vc_ext_manager, sc_ext_manager):

        self.ip_ext_manager = ip_ext_manager
        self.vc_ext_manager = vc_ext_manager
        self.sc_ext_manager = sc_ext_manager
        self.plugin_cache = {}
        self.triage_data_trans = {
            'plan_id': None,
            'plan_name': None,
            'translator_triage': []
        }

    def invoke_method(self, ctx, arg):
        error = False
        results = self.ip_ext_manager.map_method('invoke_method', arg)
        if results:
            results = list(filter(None, results))
            results = [item for sublist in results for item in sublist]
        else:
            error = True
        return {'response': results,
                'error': error}

    def get_candidate_location(self, ctx, arg):
        # candidates should have lat long info already
        error = False
        location = None
        candidate = arg["candidate"]
        lat = candidate.get('latitude', None)
        lon = candidate.get('longitude', None)
        if lat and lon:
            location = (float(lat), float(lon))
        else:
            error = True
        return {'response': location, 'error': error}

    def get_candidate_zone(self, ctx, arg):
        candidate = arg["candidate"]
        category = arg["category"]
        zone = None
        error = False

        if category == 'region':
            zone = candidate['location_id']
        elif category == 'complex':
            zone = candidate['complex_name']
        elif category == 'country':
            zone = candidate['country']
        else:
            error = True

        if error:
            LOG.error(_LE("Unresolvable zone category {}").format(category))
        else:
            LOG.info(_LI("Candidate zone is {}").format(zone))
        return {'response': zone, 'error': error}

    def get_candidates_from_service(self, ctx, arg):

        candidate_list = arg["candidate_list"]
        constraint_name = arg["constraint_name"]
        constraint_type = arg["constraint_type"]
        controller = arg["controller"]
        request = arg["request"]
        request_type = arg["request_type"]

        error = False
        filtered_candidates = []
        # call service and fetch candidates
        # TODO(jdandrea): Get rid of the SDN-C reference (outside of plugin!)
        if controller == "SDN-C":
            service_model = request.get("service_model")

            results = self.sc_ext_manager.map_method(
                'filter_candidates',
                request=request,
                candidate_list=candidate_list,
                constraint_name=constraint_name,
                constraint_type=constraint_type,
                request_type=request_type
            )

            if results and len(results) > 0:
                filtered_candidates = results[0]
            else:
                LOG.warn(
                    _LW("No candidates returned by service "
                        "controller: {}; may be a new service "
                        "instantiation.").format(controller))
        else:
            LOG.error(_LE("Unknown service controller: {}").format(controller))
        # if response from service controller is empty
        if filtered_candidates is None:
            if service_model == "ADIOD":
                LOG.error("No capacity found from SDN-GC for candidates: "
                          "{}".format(candidate_list))
            return {'response': [], 'error': error}
        else:
            LOG.debug("Filtered candidates: {}".format(filtered_candidates))
            candidate_list = [c for c in candidate_list
                              if c in filtered_candidates]
            return {'response': candidate_list, 'error': error}

    def get_candidate_discard_set(self, value, candidate_list, value_attrib):
        discard_set = set()
        value_dict = value
        value_condition = ''
        value_list = None
        if value_dict:
            if "all" in value_dict:
                value_list = value_dict.get("all")
                value_condition = "all"
            elif "any" in value_dict:
                value_list = value_dict.get("any")
                value_condition = "any"

            if not value_list:
                return discard_set

            for candidate in candidate_list:
                c_any = False
                c_all = True
                for value in value_list:
                    if candidate.get(value_attrib) == value:
                        c_any = True  # include if any one is met
                    elif candidate.get(value_attrib) != value:
                        c_all = False  # discard even if one is not met
                if value_condition == 'any' and not c_any:
                    discard_set.add(candidate.get("candidate_id"))
                elif value_condition == 'all' and not c_all:
                    discard_set.add(candidate.get("candidate_id"))
        return discard_set

    # (TODO:Larry) merge this function with the "get_candidate_discard_set"
    def get_candidate_discard_set_by_cloud_region(self, value, candidate_list, value_attrib):
        discard_set = set()

        cloud_requests = value.get("cloud-requests")
        service_requests = value.get("service-requests")
        vfmodule_requests = value.get("vfmodule-requests")

        for candidate in candidate_list:
            if candidate.get("inventory_type") == "cloud" and \
                    (candidate.get(value_attrib) not in cloud_requests):
                discard_set.add(candidate.get("candidate_id"))

            elif candidate.get("inventory_type") == "service" and \
                    (candidate.get(value_attrib) not in service_requests):
                discard_set.add(candidate.get("candidate_id"))

            elif candidate.get("inventory_type") == "vfmodule" and \
                    (candidate.get(value_attrib) not in vfmodule_requests):
                discard_set.add(candidate.get("candidate_id"))

        return discard_set

    def get_inventory_group_candidates(self, ctx, arg):
        candidate_list = arg["candidate_list"]
        resolved_candidate = arg["resolved_candidate"]
        candidate_names = []
        error = False
        service_description = 'DHV_VVIG_PAIR'
        results = self.ip_ext_manager.map_method(
            'get_inventory_group_pairs',
            service_description=service_description
        )
        if not results or len(results) < 1:
            LOG.error(
                _LE("Empty inventory group response for service: {}").format(
                    service_description))
            error = True
        else:
            pairs = results[0]
            if not pairs or len(pairs) < 1:
                LOG.error(
                    _LE("No inventory group candidates found for service: {}, "
                        "inventory provider: {}").format(
                        service_description, self.ip_ext_manager.names()[0]))
                error = True
            else:
                LOG.debug(
                    "Inventory group pairs: {}, service: {}, "
                    "inventory provider: {}".format(
                        pairs, service_description,
                        self.ip_ext_manager.names()[0]))
                for pair in pairs:
                    if resolved_candidate.get("candidate_id") == pair[0]:
                        candidate_names.append(pair[1])
                    elif resolved_candidate.get("candidate_id") == pair[1]:
                        candidate_names.append(pair[0])

        candidate_list = [c for c in candidate_list
                          if c["candidate_id"] in candidate_names]
        LOG.info(
            _LI("Inventory group candidates: {}, service: {}, "
                "inventory provider: {}").format(
                candidate_list, service_description,
                self.ip_ext_manager.names()[0]))
        return {'response': candidate_list, 'error': error}

    def get_candidates_by_attributes(self, ctx, arg):
        candidate_list = arg["candidate_list"]
        # demand_name = arg["demand_name"]
        properties = arg["properties"]
        discard_set = set()

        attributes_to_evaluate = properties.get('evaluate')
        for attrib, value in attributes_to_evaluate.items():
            if value == '':
                continue
            if attrib == 'network_roles':
                role_candidates = dict()
                role_list = []
                nrc_dict = value
                role_condition = ''
                if nrc_dict:
                    if "all" in nrc_dict:
                        role_list = nrc_dict.get("all")
                        role_condition = "all"
                    elif "any" in nrc_dict:
                        role_list = nrc_dict.get("any")
                        role_condition = "any"

                    # if the role_list is empty do nothing
                    if not role_list or role_list == '':
                        LOG.error(
                            _LE("No roles available, "
                                "inventory provider: {}").format(
                                self.ip_ext_manager.names()[0]))
                        continue
                    for role in role_list:
                        # query inventory provider to check if
                        # the candidate is in role
                        results = self.ip_ext_manager.map_method(
                            'check_network_roles',
                            network_role_id=role
                        )
                        if not results or len(results) < 1:
                            LOG.error(
                                _LE("Empty response from inventory "
                                    "provider {} for network role {}").format(
                                    self.ip_ext_manager.names()[0], role))
                            continue
                        region_ids = results[0]
                        if not region_ids:
                            LOG.error(
                                _LE("No candidates from inventory provider {} "
                                    "for network role {}").format(
                                    self.ip_ext_manager.names()[0], role))
                            continue
                        LOG.debug(
                            "Network role candidates: {}, role: {},"
                            "inventory provider: {}".format(
                                region_ids, role,
                                self.ip_ext_manager.names()[0]))
                        role_candidates[role] = region_ids

                    # find candidates that meet conditions
                    for candidate in candidate_list:
                        # perform this check only for cloud candidates
                        if candidate["inventory_type"] != "cloud":
                            continue
                        c_any = False
                        c_all = True
                        for role in role_list:
                            if role not in role_candidates:
                                c_all = False
                                continue
                            rc = role_candidates.get(role)
                            if rc and candidate.get("candidate_id") not in rc:
                                c_all = False
                                # discard even if one role is not met
                            elif rc and candidate.get("candidate_id") in rc:
                                c_any = True
                                # include if any one role is met
                        if role_condition == 'any' and not c_any:
                            discard_set.add(candidate.get("candidate_id"))
                        elif role_condition == 'all' and not c_all:
                            discard_set.add(candidate.get("candidate_id"))

            elif attrib == 'replication_role':

                for candidate in candidate_list:

                    host_id = candidate.get("host_id")
                    if host_id:
                        results = self.ip_ext_manager.map_method(
                            'check_candidate_role',
                            host_id = host_id
                        )

                        if not results or len(results) < 1:
                            LOG.error(
                                _LE("Empty response for replication roles {}").format(role))
                            discard_set.add(candidate.get("candidate_id"))
                            continue

                        # compare results from A&AI with the value in attribute constraint
                        if value and results[0] != value.upper():
                            discard_set.add(candidate.get("candidate_id"))

            elif attrib == 'complex':
                v_discard_set = \
                    self.get_candidate_discard_set(
                        value=value,
                        candidate_list=candidate_list,
                        value_attrib="complex_name")
                discard_set.update(v_discard_set)
            elif attrib == "country":
                v_discard_set = \
                    self.get_candidate_discard_set(
                        value=value,
                        candidate_list=candidate_list,
                        value_attrib="country")
                discard_set.update(v_discard_set)
            elif attrib == "state":
                v_discard_set = \
                    self.get_candidate_discard_set(
                        value=value,
                        candidate_list=candidate_list,
                        value_attrib="state")
                discard_set.update(v_discard_set)
            elif attrib == "region":
                v_discard_set = \
                    self.get_candidate_discard_set(
                        value=value,
                        candidate_list=candidate_list,
                        value_attrib="region")
                discard_set.update(v_discard_set)
            elif attrib == "cloud-region":
                v_discard_set = \
                    self.get_candidate_discard_set_by_cloud_region(
                        value=value,
                        candidate_list=candidate_list,
                        value_attrib="location_id")
                discard_set.update(v_discard_set)

        # return candidates not in discard set
        candidate_list[:] = [c for c in candidate_list
                             if c['candidate_id'] not in discard_set]
        LOG.info(
            "Available candidates after attribute checks: {}, "
            "inventory provider: {}".format(
                candidate_list, self.ip_ext_manager.names()[0]))
        return {'response': candidate_list, 'error': False}

    def get_candidates_with_vim_capacity(self, ctx, arg):
        '''
        RPC for getting candidates with vim capacity
        :param ctx: context
        :param arg: contains input passed from client side for RPC call
        :return: response candidate_list with with required vim capacity
        '''
        error = False
        candidate_list = arg["candidate_list"]
        vim_request = arg["request"]
        vim_list = set()
        discard_set = set()
        for candidate in candidate_list:
            if candidate["inventory_type"] == "cloud":
                vim_list.add(candidate['vim-id'])

        vim_request['VIMs'] = list(vim_list)
        vims_result = self.vc_ext_manager.map_method(
            'check_vim_capacity',
            vim_request
        )

        if vims_result and len(vims_result) > 0 and vims_result[0] is not None:
            vims_set = set(vims_result[0])
            for candidate in candidate_list:
                # perform this check only for cloud candidates
                if candidate["inventory_type"] == "cloud":
                    if candidate['vim-id'] not in vims_set:
                        discard_set.add(candidate.get("candidate_id"))

            # return candidates not in discard set
            candidate_list[:] = [c for c in candidate_list
                                 if c['candidate_id'] not in discard_set]
        else:
            error = True
            LOG.warn(_LI(
                "Multicloud did not respond properly to request: {}".format(
                    vim_request)))

        LOG.info(_LI(
            "Candidates with with vim capacity: {}, vim controller: "
            "{}").format(candidate_list, self.vc_ext_manager.names()[0]))

        return {'response': candidate_list, 'error': error}

    def resolve_demands(self, ctx, arg):

        log_util.setLoggerFilter(LOG, ctx.get('keyspace'), ctx.get('plan_id'))

        error = False
        demands = arg.get('demands')
        plan_info = arg.get('plan_info')
        triage_translator_data = arg.get('triage_translator_data')
        resolved_demands = None
        results = self.ip_ext_manager.map_method(
            'resolve_demands',
            demands, plan_info, triage_translator_data
        )
        if results and len(results) > 0:
            if len(results) > 1:
                resolved_demands = self.get_resolved_demands_from_result(results)
            else:
                resolved_demands = results[0]
            if self.triage_data_trans['plan_id']== None :
                self.triage_data_trans['plan_name'] = triage_translator_data['plan_name']
                self.triage_data_trans['plan_id'] = triage_translator_data['plan_id']
                self.triage_data_trans['translator_triage'].append(triage_translator_data['dropped_candidates'])
            elif not self.triage_data_trans['plan_id'] == triage_translator_data['plan_id'] :
                self.triage_data_trans = {'plan_id': triage_translator_data['plan_id'],
                                          'plan_name': triage_translator_data['plan_name'], 'translator_triage': []}
                self.triage_data_trans['translator_triage'].append(triage_translator_data['dropped_candidates'])
            else:
                self.triage_data_trans['translator_triage'].append(triage_translator_data['dropped_candidates'])
        else:
            error = True

        return {'response': {'resolved_demands': resolved_demands,
                             'trans': self.triage_data_trans},
                'error': error}

    def get_resolved_demands_from_result(self, results):
        resolved_demands = {de: [] for de in results[0].keys()}
        for result in results:
            for demand, candidates in result.items():
                resolved_demands[demand].extend(candidates)
        LOG.info('resolved_demands: {}'.format(str(resolved_demands)))
        return resolved_demands

    def resolve_location(self, ctx, arg):

        log_util.setLoggerFilter(LOG, ctx.get('keyspace'), ctx.get('plan_id'))

        error = False
        resolved_location = None

        host_name = arg.get('host_name')
        clli_code = arg.get('clli_code')

        if host_name:
            results = self.ip_ext_manager.map_method(
                'resolve_host_location',
                host_name
            )

        elif clli_code:
            results = self.ip_ext_manager.map_method(
                'resolve_clli_location',
                clli_code
            )
        else:
            results = None
            # unknown location response
            LOG.error(_LE("Unknown location type from the input template."
                          "Expected location types are host_name"
                          " or clli_code."))

        if results and len(results) > 0:
            resolved_location = results[0]
        else:
            error = True
        return {'response': {'resolved_location': resolved_location},
                'error': error}

    def call_reservation_operation(self, ctx, arg):
        result = True
        reserved_candidates = None
        method = arg["method"]
        candidate_list = arg["candidate_list"]
        reservation_name = arg["reservation_name"]
        reservation_type = arg["reservation_type"]
        controller = arg["controller"]
        request = arg["request"]

        if controller == "SDN-C":
            results = self.sc_ext_manager.map_method(
                'call_reservation_operation',
                method=method,
                candidate_list=candidate_list,
                reservation_name=reservation_name,
                reservation_type=reservation_type,
                request=request
            )
            if results and len(results) > 0:
                reserved_candidates = results[0]
        else:
            LOG.error(_LE("Unknown service controller: {}").format(controller))
        if reserved_candidates is None or not reserved_candidates:
            result = False
            LOG.debug(
                _LW("Unable to {} for "
                    "candidate {}.").format(method, reserved_candidates))
            return {'response': result,
                    'error': not result}
        else:
            LOG.debug("{} for the candidate: "
                      "{}".format(method, reserved_candidates))
            return {'response': result,
                    'error': not result}
