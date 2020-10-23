#!/usr/bin/env python
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


"""Constraint/Engine Interface

Utility library that defines the interface between
the constraints and the conductor data engine.

"""

from oslo_log import log

LOG = log.getLogger(__name__)


class ConstraintEngineInterface(object):
    def __init__(self, client):
        self.client = client

    def get_candidate_location(self, candidate):
        # Try calling a method (remember, "calls" are synchronous)
        # FIXME(jdandrea): Doing this because Music calls are expensive.
        lat = candidate.get('latitude')
        lon = candidate.get('longitude')
        if lat and lon:
            response = (float(lat), float(lon))
        else:
            ctxt = {}
            args = {"candidate": candidate}
            response = self.client.call(ctxt=ctxt,
                                        method="get_candidate_location",
                                        args=args)
            LOG.debug("get_candidate_location response: {}".format(response))
        return response

    def get_candidate_zone(self, candidate, _category=None):
        # FIXME(jdandrea): Doing this because Music calls are expensive.
        if _category == 'region':
            response = candidate['location_id']
        elif _category == 'complex':
            response = candidate['complex_name']
        elif _category == 'country':
            response = candidate['country']
        else:
            ctxt = {}
            args = {"candidate": candidate, "category": _category}
            response = self.client.call(ctxt=ctxt,
                                        method="get_candidate_zone",
                                        args=args)
            LOG.debug("get_candidate_zone response: {}".format(response))
        return response

    def get_candidates_from_service(self, constraint_name,
                                    constraint_type, candidate_list,
                                    controller, inventory_type,
                                    request, cost, demand_name,
                                    request_type):
        ctxt = {}
        args = {"constraint_name": constraint_name,
                "constraint_type": constraint_type,
                "candidate_list": candidate_list,
                "controller": controller,
                "inventory_type": inventory_type,
                "request": request,
                "cost": cost,
                "demand_name": demand_name,
                "request_type": request_type}
        response = self.client.call(ctxt=ctxt,
                                    method="get_candidates_from_service",
                                    args=args)
        LOG.debug("get_candidates_from_service response: {}".format(response))
        # response is a list of (candidate, cost) tuples
        return response

    def get_inventory_group_candidates(self, candidate_list,
                                       demand_name, resolved_candidate):
        # return a list of the "pair" candidates for the given candidate
        ctxt = {}
        args = {"candidate_list": candidate_list,
                "demand_name": demand_name,
                "resolved_candidate": resolved_candidate}
        response = self.client.call(ctxt=ctxt,
                                    method="get_inventory_group_candidates",
                                    args=args)
        LOG.debug("get_inventory_group_candidates \
                   response: {}".format(response))
        return response

    def get_candidates_by_attributes(self, demand_name,
                                     candidate_list, properties):
        ctxt = {}
        args = {"candidate_list": candidate_list,
                "properties": properties,
                "demand_name": demand_name}
        response = self.client.call(ctxt=ctxt,
                                    method="get_candidates_by_attributes",
                                    args=args)
        LOG.debug("get_candidates_by_attribute response: {}".format(response))
        # response is a list of (candidate, cost) tuples
        return response

    def get_candidates_with_hpa(self, id, type, directives, candidate_list,
                                flavorProperties):
        """Get candidates with an addition of flavor_mapping for matching cloud candidates with hpa constraints.

        :param label_name: vm_label_name passed from the SO/Policy
        :param candidate_list: list of candidates to process
        :param flavorProperties: hpa features for this vm_label_name
        :return: candidate_list with hpa features and flavor mapping
        """
        ctxt = {}
        args = {"candidate_list": candidate_list,
                "flavorProperties": flavorProperties,
                "id": id,
                "type": type,
                "directives": directives,
                "method_name": "get_candidates_with_hpa"}
        response = self.client.call(ctxt=ctxt,
                                    method="invoke_method",
                                    args=args)
        LOG.debug("get_candidates_with_hpa response: {}".format(response))
        return response

    def get_candidates_with_vim_capacity(self, candidate_list, vim_request):
        """Returns the candidate_list with required vim capacity.

        :param candidate_list: list of candidates to process
        :param requests: vim requests with required cpu, memory and disk
        :return: candidate_list with required vim capacity.
        """
        ctxt = {}
        args = {"candidate_list": candidate_list,
                "request": vim_request}
        response = self.client.call(ctxt=ctxt,
                                    method="get_candidates_with_vim_capacity",
                                    args=args)
        LOG.debug(
            "get_candidates_with_vim_capacity response: {}".format(response))
        return response
