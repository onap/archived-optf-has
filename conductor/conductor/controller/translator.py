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

import copy
import datetime
import json
import os
import uuid

import six
import yaml
from conductor import __file__ as conductor_root
from conductor import messaging
from conductor import service

from conductor.common import threshold
from conductor.common.music import messaging as music_messaging
from conductor.data.plugins.triage_translator.triage_translator_data import TraigeTranslatorData
from conductor.data.plugins.triage_translator.triage_translator import TraigeTranslator
from oslo_config import cfg
from oslo_log import log

LOG = log.getLogger(__name__)

CONF = cfg.CONF

VERSIONS = ["2016-11-01", "2017-10-10", "2018-02-01"]
LOCATION_KEYS = ['latitude', 'longitude', 'host_name', 'clli_code']
INVENTORY_PROVIDERS = ['aai']
INVENTORY_TYPES = ['cloud', 'service', 'transport', 'vfmodule']
DEFAULT_INVENTORY_PROVIDER = INVENTORY_PROVIDERS[0]
CANDIDATE_KEYS = ['candidate_id', 'cost', 'inventory_type', 'location_id',
                  'location_type']
DEMAND_KEYS = ['filtering_attributes', 'passthrough_attributes', 'candidates', 'complex', 'conflict_identifier',
               'customer_id', 'default_cost', 'excluded_candidates',
               'existing_placement', 'flavor', 'inventory_provider',
               'inventory_type', 'port_key', 'region', 'required_candidates',
               'service_id', 'service_resource_id', 'service_subscription',
               'service_type', 'subdivision', 'unique', 'vlan_key']
CONSTRAINT_KEYS = ['type', 'demands', 'properties']
CONSTRAINTS = {
    # constraint_type: {
    #   split: split into individual constraints, one per demand
    #   required: list of required property names,
    #   optional: list of optional property names,
    #   thresholds: dict of property/base-unit pairs for threshold parsing
    #   allowed: dict of keys and allowed values (if controlled vocab);
    #            only use this for Conductor-controlled values!
    # }
    'attribute': {
        'split': True,
        'required': ['evaluate'],
    },
    'distance_between_demands': {
        'required': ['distance'],
        'thresholds': {
            'distance': 'distance'
        },
    },
    'distance_to_location': {
        'split': True,
        'required': ['distance', 'location'],
        'thresholds': {
            'distance': 'distance'
        },
    },
    'instance_fit': {
        'split': True,
        'required': ['controller'],
        'optional': ['request'],
    },
    'inventory_group': {},
    'region_fit': {
        'split': True,
        'required': ['controller'],
        'optional': ['request'],
    },
    'zone': {
        'required': ['qualifier', 'category'],
        'optional': ['location'],
        'allowed': {'qualifier': ['same', 'different'],
                    'category': ['disaster', 'region', 'complex', 'country',
                                 'time', 'maintenance']},
    },
    'vim_fit': {
        'split': True,
        'required': ['controller'],
        'optional': ['request'],
    },
    'hpa': {
        'split': True,
        'required': ['evaluate'],
    },
}
HPA_FEATURES = ['architecture', 'hpa-feature', 'hpa-feature-attributes',
                'hpa-version', 'mandatory', 'directives']
HPA_OPTIONAL = ['score']
HPA_ATTRIBUTES = ['hpa-attribute-key', 'hpa-attribute-value', 'operator']
HPA_ATTRIBUTES_OPTIONAL = ['unit']


class TranslatorException(Exception):
    pass


class Translator(object):
    """Template translator.

    Takes an input template and translates it into
    something the solver can use. Calls the data service
    as needed, giving it the inventory provider as context.
    Presently the only inventory provider is A&AI. Others
    may be added in the future.
    """

    def __init__(self, conf, plan_name, plan_id, template):
        self.conf = conf
        self._template = copy.deepcopy(template)
        self._plan_name = plan_name
        self._plan_id = plan_id
        self._translation = None
        self._valid = False
        self._ok = False
        self.triageTranslatorData= TraigeTranslatorData()
        self.triageTranslator = TraigeTranslator()
        # Set up the RPC service(s) we want to talk to.
        self.data_service = self.setup_rpc(self.conf, "data")

    def setup_rpc(self, conf, topic):
        """Set up the RPC Client"""
        # TODO(jdandrea): Put this pattern inside music_messaging?
        transport = messaging.get_transport(conf=conf)
        target = music_messaging.Target(topic=topic)
        client = music_messaging.RPCClient(conf=conf,
                                           transport=transport,
                                           target=target)
        return client

    def create_components(self):
        # TODO(jdandrea): Make deep copies so the template is untouched
        self._version = self._template.get("homing_template_version")
        self._parameters = self._template.get("parameters", {})
        self._locations = self._template.get("locations", {})
        self._demands = self._template.get("demands", {})
        self._constraints = self._template.get("constraints", {})
        self._optmization = self._template.get("optimization", {})
        self._reservations = self._template.get("reservation", {})

        if isinstance(self._version, datetime.date):
            self._version = str(self._version)

    def validate_components(self):
        """Cursory validation of template components.

        More detailed validation happens while parsing each component.
        """
        self._valid = False

        # Check version
        if self._version not in VERSIONS:
            raise TranslatorException(
                "conductor_template_version must be one "
                "of: {}".format(', '.join(VERSIONS)))

        # Check top level structure
        components = {
            "parameters": {
                "name": "Parameter",
                "content": self._parameters,
            },
            "locations": {
                "name": "Location",
                "keys": LOCATION_KEYS,
                "content": self._locations,
            },
            "demands": {
                "name": "Demand",
                "content": self._demands,
            },
            "constraints": {
                "name": "Constraint",
                "keys": CONSTRAINT_KEYS,
                "content": self._constraints,
            },
            "optimization": {
                "name": "Optimization",
                "content": self._optmization,
            },
            "reservations": {
                "name": "Reservation",
                "content": self._reservations,
            }
        }
        for name, component in components.items():
            name = component.get('name')
            keys = component.get('keys', None)
            content = component.get('content')

            if type(content) is not dict:
                raise TranslatorException(
                    "{} section must be a dictionary".format(name))
            for content_name, content_def in content.items():
                if not keys:
                    continue

                for key in content_def:
                    if key not in keys:
                        raise TranslatorException(
                            "{} {} has an invalid key {}".format(
                                name, content_name, key))

        demand_keys = self._demands.keys()
        location_keys = self._locations.keys()
        for constraint_name, constraint in self._constraints.items():

            # Require a single demand (string), or a list of one or more.
            demands = constraint.get('demands')
            if isinstance(demands, six.string_types):
                demands = [demands]
            if not isinstance(demands, list) or len(demands) < 1:
                raise TranslatorException(
                    "Demand list for Constraint {} must be "
                    "a list of names or a string with one name".format(
                        constraint_name))
            if not set(demands).issubset(demand_keys + location_keys):
                raise TranslatorException(
                    "Undefined Demand(s) {} in Constraint '{}'".format(
                        list(set(demands).difference(demand_keys)),
                        constraint_name))

            properties = constraint.get('properties', None)
            if properties:
                location = properties.get('location', None)
                if location:
                    if location not in location_keys:
                        raise TranslatorException(
                            "Location {} in Constraint {} is undefined".format(
                                location, constraint_name))

        self._valid = True

    def _parse_parameters(self, obj, path=[]):
        """Recursively parse all {get_param: X} occurrences

        This modifies obj in-place. If you want to keep the original,
        pass in a deep copy.
        """
        # Ok to start with a string ...
        if isinstance(path, six.string_types):
            # ... but the breadcrumb trail goes in an array.
            path = [path]

        # Traverse a list
        if type(obj) is list:
            for idx, val in enumerate(obj, start=0):
                # Add path to the breadcrumb trail
                new_path = list(path)
                new_path[-1] += "[{}]".format(idx)

                # Look at each element.
                obj[idx] = self._parse_parameters(val, new_path)

        # Traverse a dict
        elif type(obj) is dict:
            # Did we find a "{get_param: ...}" intrinsic?
            if obj.keys() == ['get_param']:
                param_name = obj['get_param']

                # The parameter name must be a string.
                if not isinstance(param_name, six.string_types):
                    path_str = ' > '.join(path)
                    raise TranslatorException(
                        "Parameter name '{}' not a string in path {}".format(
                            param_name, path_str))

                # Parameter name must be defined.
                if param_name not in self._parameters:
                    path_str = ' > '.join(path)
                    raise TranslatorException(
                        "Parameter '{}' undefined in path {}".format(
                            param_name, path_str))

                # Return the value in place of the call.
                return self._parameters.get(param_name)

            # Not an intrinsic. Traverse as usual.
            for key in obj.keys():
                # Add path to the breadcrumb trail.
                new_path = list(path)
                new_path.append(key)

                # Look at each key/value pair.
                obj[key] = self._parse_parameters(obj[key], new_path)

        # Return whatever we have after unwinding.
        return obj

    def parse_parameters(self):
        """Resolve all parameters references."""
        locations = copy.deepcopy(self._locations)
        self._locations = self._parse_parameters(locations, 'locations')

        demands = copy.deepcopy(self._demands)
        self._demands = self._parse_parameters(demands, 'demands')

        constraints = copy.deepcopy(self._constraints)
        self._constraints = self._parse_parameters(constraints, 'constraints')

        reservations = copy.deepcopy(self._reservations)
        self._reservations = self._parse_parameters(reservations,
                                                    'reservations')

    def parse_locations(self, locations):
        """Prepare the locations for use by the solver."""
        parsed = {}
        for location, args in locations.items():
            ctxt = {
                'plan_id': self._plan_id,
                'keyspace': self.conf.keyspace
            }

            latitude = args.get("latitude")
            longitude = args.get("longitude")

            if latitude and longitude:
                resolved_location = {"latitude": latitude, "longitude": longitude}
            else:
                # ctxt = {}
                response = self.data_service.call(
                    ctxt=ctxt,
                    method="resolve_location",
                    args=args)

                resolved_location = \
                    response and response.get('resolved_location')
            if not resolved_location:
                raise TranslatorException(
                    "Unable to resolve location {}".format(location)
                )
            parsed[location] = resolved_location
        return parsed

    def parse_demands(self, demands):
        """Validate/prepare demands for use by the solver."""
        if type(demands) is not dict:
            raise TranslatorException("Demands must be provided in "
                                      "dictionary form")

        # Look at each demand
        demands_copy = copy.deepcopy(demands)
        parsed = {}
        for name, requirements in demands_copy.items():
            inventory_candidates = []
            for requirement in requirements:
                for key in requirement:
                    if key not in DEMAND_KEYS:
                        raise TranslatorException(
                            "Demand {} has an invalid key {}".format(
                                requirement, key))

                if 'candidates' in requirement:
                    # Candidates *must* specify an inventory provider
                    provider = requirement.get("inventory_provider")
                    if provider and provider not in INVENTORY_PROVIDERS:
                        raise TranslatorException(
                            "Unsupported inventory provider {} "
                            "in demand {}".format(provider, name))
                    else:
                        provider = DEFAULT_INVENTORY_PROVIDER

                    # Check each candidate
                    for candidate in requirement.get('candidates'):
                        # Must be a dictionary
                        if type(candidate) is not dict:
                            raise TranslatorException(
                                "Candidate found in demand {} that is "
                                "not a dictionary".format(name))

                        # Must have only supported keys
                        for key in candidate.keys():
                            if key not in CANDIDATE_KEYS:
                                raise TranslatorException(
                                    "Candidate with invalid key {} found "
                                    "in demand {}".format(key, name)
                                )

                        # TODO(jdandrea): Check required/optional keys

                        # Set the inventory provider if not already
                        candidate['inventory_provider'] = \
                            candidate.get('inventory_provider', provider)

                        # Set cost if not already (default cost is 0?)
                        candidate['cost'] = candidate.get('cost', 0)

                        # Add to our list of parsed candidates
                        inventory_candidates.append(candidate)

                # candidates are specified through inventory providers
                # Do the basic sanity checks for inputs
                else:
                    # inventory provider MUST be specified
                    provider = requirement.get("inventory_provider")
                    if not provider:
                        raise TranslatorException(
                            "Inventory provider not specified "
                            "in demand {}".format(name)
                        )
                    elif provider and provider not in INVENTORY_PROVIDERS:
                        raise TranslatorException(
                            "Unsupported inventory provider {} "
                            "in demand {}".format(provider, name)
                        )
                    else:
                        provider = DEFAULT_INVENTORY_PROVIDER
                        requirement['provider'] = provider

                    # inventory type MUST be specified
                    inventory_type = requirement.get('inventory_type')
                    if not inventory_type or inventory_type == '':
                        raise TranslatorException(
                            "Inventory type not specified for "
                            "demand {}".format(name)
                        )
                    if inventory_type and \
                            inventory_type not in INVENTORY_TYPES:
                        raise TranslatorException(
                            "Unknown inventory type {} specified for "
                            "demand {}".format(inventory_type, name)
                        )

                    # For service and vfmodule inventories, customer_id and
                    # service_type MUST be specified
                    if inventory_type == 'service' or inventory_type == 'vfmodule':
                        filtering_attributes = requirement.get('filtering_attributes')

                        if filtering_attributes:
                            customer_id = filtering_attributes.get('customer-id')
                            global_customer_id = filtering_attributes.get('global-customer-id')
                            if global_customer_id:
                                customer_id = global_customer_id
                        else:
                            # for backward compatibility
                            customer_id = requirement.get('customer_id')
                            service_type = requirement.get('service_type')

                        if not customer_id:
                            raise TranslatorException(
                                "Customer ID not specified for "
                                "demand {}".format(name)
                            )
                        if not filtering_attributes and not service_type:
                            raise TranslatorException(
                                "Service Type not specified for "
                                "demand {}".format(name)
                            )

                # TODO(jdandrea): Check required/optional keys for requirement
                # elif 'inventory_type' in requirement:
                #     # For now this is just a stand-in candidate
                #     candidate = {
                #         'inventory_provider':
                #             requirement.get('inventory_provider',
                #                             DEFAULT_INVENTORY_PROVIDER),
                #         'inventory_type':
                #             requirement.get('inventory_type', ''),
                #         'candidate_id': '',
                #         'location_id': '',
                #         'location_type': '',
                #         'cost': 0,
                #     }
                #
                #     # Add to our list of parsed candidates
                #     inventory_candidates.append(candidate)

            # Ask conductor-data for one or more candidates.
            ctxt = {
                "plan_id": self._plan_id,
                "plan_name": self._plan_name,
                "keyspace": self.conf.keyspace,
            }
            args = {
                "demands": {
                    name: requirements,
                },
                "plan_info":{
                    "plan_id": self._plan_id,
                    "plan_name": self._plan_name
                },
                "triage_translator_data": self.triageTranslatorData.__dict__

            }

            # Check if required_candidate and excluded candidate
            # are mutually exclusive.
            for requirement in requirements:
                required_candidates = requirement.get("required_candidates")
                excluded_candidates = requirement.get("excluded_candidates")
                if (required_candidates and
                    excluded_candidates and
                    set(map(lambda entry: entry['candidate_id'],
                            required_candidates))
                    & set(map(lambda entry: entry['candidate_id'],
                              excluded_candidates))):
                    raise TranslatorException(
                        "Required candidate list and excluded candidate"
                        " list are not mutually exclusive for demand"
                        " {}".format(name)
                    )
            response = self.data_service.call(
                ctxt=ctxt,
                method="resolve_demands",
                args=args)

            resolved_demands = \
                response and response.get('resolved_demands')
            triage_data_trans = \
                response and response.get('trans')

            required_candidates = resolved_demands \
                .get('required_candidates')
            if not resolved_demands:
                self.triageTranslator.thefinalCallTrans(triage_data_trans)
                raise TranslatorException(
                    "Unable to resolve inventory "
                    "candidates for demand {}"
                    .format(name)
                )
            resolved_candidates = resolved_demands.get(name)
            for candidate in resolved_candidates:
                inventory_candidates.append(candidate)
            if len(inventory_candidates) < 1:
                if not required_candidates:
                    self.triageTranslator.thefinalCallTrans(triage_data_trans)
                    raise TranslatorException(
                        "Unable to find any candidate for "
                        "demand {}".format(name)
                    )
                else:
                    self.triageTranslator.thefinalCallTrans(triage_data_trans)
                    raise TranslatorException(
                        "Unable to find any required "
                        "candidate for demand {}"
                        .format(name)
                    )
            parsed[name] = {
                "candidates": inventory_candidates,
            }
        self.triageTranslator.thefinalCallTrans(triage_data_trans)
        return parsed

    def validate_hpa_constraints(self, req_prop, value):
        for para in value.get(req_prop):
            # Make sure there is at least one
            # set of id, type, directives and flavorProperties
            if not para.get('id') \
                    or not para.get('type') \
                    or not para.get('directives') \
                    or not para.get('flavorProperties') \
                    or para.get('id') == '' \
                    or para.get('type') == '' \
                    or not isinstance(para.get('directives'), list) \
                    or para.get('flavorProperties') == '':
                raise TranslatorException(
                    "HPA requirements need at least "
                    "one set of id, type, directives and flavorProperties"
                )
            for feature in para.get('flavorProperties'):
                if type(feature) is not dict:
                    raise TranslatorException("HPA feature must be a dict")
                # process mandatory parameter
                hpa_mandatory = set(HPA_FEATURES).difference(feature.keys())
                if bool(hpa_mandatory):
                    raise TranslatorException(
                        "Lack of compulsory elements inside HPA feature")
                # process optional parameter
                hpa_optional = set(feature.keys()).difference(HPA_FEATURES)
                if hpa_optional and not hpa_optional.issubset(HPA_OPTIONAL):
                    raise TranslatorException(
                        "Got unrecognized elements inside HPA feature")
                if feature.get('mandatory') == 'False' and not feature.get(
                        'score'):
                    raise TranslatorException(
                        "Score needs to be present if mandatory is False")

                for attr in feature.get('hpa-feature-attributes'):
                    if type(attr) is not dict:
                        raise TranslatorException(
                            "HPA feature attributes must be a dict")

                    # process mandatory hpa attribute parameter
                    hpa_attr_mandatory = set(HPA_ATTRIBUTES).difference(
                        attr.keys())
                    if bool(hpa_attr_mandatory):
                        raise TranslatorException(
                            "Lack of compulsory elements inside HPA "
                            "feature attributes")
                    # process optional hpa attribute parameter
                    hpa_attr_optional = set(attr.keys()).difference(
                        HPA_ATTRIBUTES)
                    if hpa_attr_optional and not hpa_attr_optional.issubset(
                            HPA_ATTRIBUTES_OPTIONAL):
                        raise TranslatorException(
                            "Invalid attributes '{}' found inside HPA "
                            "feature attributes".format(hpa_attr_optional))

    def parse_constraints(self, constraints):
        """Validate/prepare constraints for use by the solver."""
        if not isinstance(constraints, dict):
            raise TranslatorException("Constraints must be provided in "
                                      "dictionary form")

        # Look at each constraint. Properties must exist, even if empty.
        constraints_copy = copy.deepcopy(constraints)

        parsed = {}
        for name, constraint in constraints_copy.items():

            if not constraint.get('properties'):
                constraint['properties'] = {}

            constraint_type = constraint.get('type')
            constraint_def = CONSTRAINTS.get(constraint_type)

            # Is it a supported type?
            if constraint_type not in CONSTRAINTS:
                raise TranslatorException(
                    "Unsupported type '{}' found in constraint "
                    "named '{}'".format(constraint_type, name))

            # Now walk through the constraint's content
            for key, value in constraint.items():
                # Must be a supported key
                if key not in CONSTRAINT_KEYS:
                    raise TranslatorException(
                        "Invalid key '{}' found in constraint "
                        "named '{}'".format(key, name))

                # For properties ...
                if key == 'properties':
                    # Make sure all required properties are present
                    required = constraint_def.get('required', [])
                    for req_prop in required:
                        if req_prop not in value.keys():
                            raise TranslatorException(
                                "Required property '{}' not found in "
                                "constraint named '{}'".format(
                                    req_prop, name))
                        if not value.get(req_prop) \
                                or value.get(req_prop) == '':
                            raise TranslatorException(
                                "No value specified for property '{}' in "
                                "constraint named '{}'".format(
                                    req_prop, name))
                            # For HPA constraints
                        if constraint_type == 'hpa':
                            self.validate_hpa_constraints(req_prop, value)

                    # Make sure there are no unknown properties
                    optional = constraint_def.get('optional', [])
                    for prop_name in value.keys():
                        if prop_name not in required + optional:
                            raise TranslatorException(
                                "Unknown property '{}' in "
                                "constraint named '{}'".format(
                                    prop_name, name))

                    # If a property has a controlled vocabulary, make
                    # sure its value is one of the allowed ones.
                    allowed = constraint_def.get('allowed', {})
                    for prop_name, allowed_values in allowed.items():
                        if prop_name in value.keys():
                            prop_value = value.get(prop_name, '')
                            if prop_value not in allowed_values:
                                raise TranslatorException(
                                    "Property '{}' value '{}' unsupported in "
                                    "constraint named '{}' (must be one of "
                                    "{})".format(prop_name, prop_value,
                                                 name, allowed_values))

                    # Break all threshold-formatted values into parts
                    thresholds = constraint_def.get('thresholds', {})
                    for thr_prop, base_units in thresholds.items():
                        if thr_prop in value.keys():
                            expression = value.get(thr_prop)
                            thr = threshold.Threshold(expression, base_units)
                            value[thr_prop] = thr.parts

            # We already know we have one or more demands due to
            # validate_components(). We still need to coerce the demands
            # into a list in case only one demand was provided.
            constraint_demands = constraint.get('demands')
            if isinstance(constraint_demands, six.string_types):
                constraint['demands'] = [constraint_demands]

            # Either split the constraint into parts, one per demand,
            # or use it as-is
            if constraint_def.get('split'):
                for demand in constraint.get('demands', []):
                    constraint_demand = name + '_' + demand
                    parsed[constraint_demand] = copy.deepcopy(constraint)
                    parsed[constraint_demand]['name'] = name
                    parsed[constraint_demand]['demands'] = demand
            else:
                parsed[name] = copy.deepcopy(constraint)
                parsed[name]['name'] = name

        return parsed

    def parse_optimization(self, optimization):
        """Validate/prepare optimization for use by the solver."""

        # WARNING: The template format for optimization is generalized,
        # however the solver is very particular about the expected
        # goal, functions, and operands. Therefore, for the time being,
        # we are choosing to be highly conservative in what we accept
        # at the template level. Once the solver can handle the more
        # general form, we can make the translation pass in this
        # essentially pre-parsed formula unchanged, or we may allow
        # optimizations to be written in algebraic form and pre-parsed
        # with antlr4-python2-runtime. (jdandrea 1 Dec 2016)

        if not optimization:
            LOG.debug("No objective function or "
                      "optimzation provided in the template")
            return

        optimization_copy = copy.deepcopy(optimization)
        parsed = {
            "goal": "min",
            "operation": "sum",
            "operands": [],
        }

        if type(optimization_copy) is not dict:
            raise TranslatorException("Optimization must be a dictionary.")

        goals = optimization_copy.keys()
        if goals != ['minimize']:
            raise TranslatorException(
                "Optimization must contain a single goal of 'minimize'.")

        funcs = optimization_copy['minimize'].keys()
        if funcs != ['sum']:
            raise TranslatorException(
                "Optimization goal 'minimize' must "
                "contain a single function of 'sum'.")

        operands = optimization_copy['minimize']['sum']
        if type(operands) is not list:
            # or len(operands) != 2:
            raise TranslatorException(
                "Optimization goal 'minimize', function 'sum' "
                "must be a list of exactly two operands.")

        def get_latency_between_args(operand):
            args = operand.get('latency_between')
            if type(args) is not list and len(args) != 2:
                raise TranslatorException(
                    "Optimization 'latency_between' arguments must "
                    "be a list of length two.")

            got_demand = False
            got_location = False
            for arg in args:
                if not got_demand and arg in self._demands.keys():
                    got_demand = True
                if not got_location and arg in self._locations.keys():
                    got_location = True
            if not got_demand or not got_location:
                raise TranslatorException(
                    "Optimization 'latency_between' arguments {} must "
                    "include one valid demand name and one valid "
                    "location name.".format(args))

            return args

        def get_distance_between_args(operand):
            args = operand.get('distance_between')
            if type(args) is not list and len(args) != 2:
                raise TranslatorException(
                    "Optimization 'distance_between' arguments must "
                    "be a list of length two.")

            got_demand = False
            got_location = False
            for arg in args:
                if not got_demand and arg in self._demands.keys():
                    got_demand = True
                if not got_location and arg in self._locations.keys():
                    got_location = True
            if not got_demand or not got_location:
                raise TranslatorException(
                    "Optimization 'distance_between' arguments {} must "
                    "include one valid demand name and one valid "
                    "location name.".format(args))

            return args

        for operand in operands:
            weight = 1.0
            args = None
            nested = False

            if operand.keys() == ['distance_between']:
                # Value must be a list of length 2 with one
                # location and one demand
                function = 'distance_between'
                args = get_distance_between_args(operand)

            elif operand.keys() == ['product']:
                for product_op in operand['product']:
                    if threshold.is_number(product_op):
                        weight = product_op
                    elif isinstance(product_op, dict):
                        if product_op.keys() == ['latency_between']:
                            function = 'latency_between'
                            args = get_latency_between_args(product_op)
                        elif product_op.keys() == ['distance_between']:
                            function = 'distance_between'
                            args = get_distance_between_args(product_op)
                        elif product_op.keys() == ['aic_version']:
                            function = 'aic_version'
                            args = product_op.get('aic_version')
                        elif product_op.keys() == ['hpa_score']:
                            function = 'hpa_score'
                            args = product_op.get('hpa_score')
                            if not self.is_hpa_policy_exists(args):
                                raise TranslatorException(
                                    "HPA Score Optimization must include a "
                                    "HPA Policy constraint ")
                        elif product_op.keys() == ['sum']:
                            nested = True
                            nested_operands = product_op.get('sum')
                            for nested_operand in nested_operands:
                                if nested_operand.keys() == ['product']:
                                    nested_weight = weight
                                    for nested_product_op in nested_operand['product']:
                                        if threshold.is_number(nested_product_op):
                                            nested_weight = nested_weight * int(nested_product_op)
                                        elif isinstance(nested_product_op, dict):
                                            if nested_product_op.keys() == ['latency_between']:
                                                function = 'latency_between'
                                                args = get_latency_between_args(nested_product_op)
                                            elif nested_product_op.keys() == ['distance_between']:
                                                function = 'distance_between'
                                                args = get_distance_between_args(nested_product_op)
                                    parsed['operands'].append(
                                        {
                                            "operation": "product",
                                            "weight": nested_weight,
                                            "function": function,
                                            "function_param": args,
                                        }
                                    )

                if not args:
                    raise TranslatorException(
                        "Optimization products must include at least "
                        "one 'distance_between' function call and "
                        "one optional number to be used as a weight.")

            # We now have our weight/function_param.
            if not nested:
                parsed['operands'].append(
                    {
                        "operation": "product",
                        "weight": weight,
                        "function": function,
                        "function_param": args,
                    }
                )
        return parsed

    def is_hpa_policy_exists(self, demand_list):
        # Check if a HPA constraint exist for the demands in the demand list.
        constraints_copy = copy.deepcopy(self._constraints)
        for demand in demand_list:
            for name, constraint in constraints_copy.items():
                constraint_type = constraint.get('type')
                if constraint_type == 'hpa':
                    hpa_demands = constraint.get('demands')
                    if demand in hpa_demands:
                        return True
        return False

    def parse_reservations(self, reservations):
        demands = self._demands
        if not isinstance(reservations, dict):
            raise TranslatorException("Reservations must be provided in "
                                      "dictionary form")
        parsed = {}
        if reservations:
            parsed['counter'] = 0
            parsed['demands'] = {}

        for key, value in reservations.items():

            if key == "service_model":
                parsed['service_model'] = value

            elif key == "service_candidates":
                for name, reservation_details in value.items():
                    if not reservation_details.get('properties'):
                        reservation_details['properties'] = {}
                    for demand in reservation_details.get('demands', []):
                        if demand in demands.keys():
                            reservation_demand = name + '_' + demand
                            parsed['demands'][reservation_demand] = copy.deepcopy(reservation_details)
                            parsed['demands'][reservation_demand]['name'] = name
                            parsed['demands'][reservation_demand]['demands'] = demand
                        else:
                            raise TranslatorException("Demand {} must be provided in demands section".format(demand))

        return parsed

    def do_translation(self):
        """Perform the translation."""
        if not self.valid:
            raise TranslatorException("Can't translate an invalid template.")

        request_type = self._parameters.get("request_type") \
                       or self._parameters.get("REQUEST_TYPE") \
                       or ""

        self._translation = {
            "conductor_solver": {
                "version": self._version,
                "plan_id": self._plan_id,
                "request_type": request_type,
                "locations": self.parse_locations(self._locations),
                "demands": self.parse_demands(self._demands),
                "objective": self.parse_optimization(self._optmization),
                "constraints": self.parse_constraints(self._constraints),
                "objective": self.parse_optimization(self._optmization),
                "reservations": self.parse_reservations(self._reservations),
            }
        }

    def translate(self):
        """Translate the template for the solver."""
        self._ok = False
        try:
            self.create_components()
            self.validate_components()
            self.parse_parameters()
            self.do_translation()
            self._ok = True
        except Exception as exc:
            self._error_message = exc.message

    @property
    def valid(self):
        """Returns True if the template has been validated."""
        return self._valid

    @property
    def ok(self):
        """Returns True if the translation was successful."""
        return self._ok

    @property
    def translation(self):
        """Returns the translation if it was successful."""
        return self._translation

    @property
    def error_message(self):
        """Returns the last known error message."""
        return self._error_message


def main():
    template_name = 'some_template'

    path = os.path.abspath(conductor_root)
    dir_path = os.path.dirname(path)

    # Prepare service-wide components (e.g., config)
    conf = service.prepare_service(
        [], config_files=[dir_path + '/../etc/conductor/conductor.conf'])
    # conf.set_override('mock', True, 'music_api')

    t1 = threshold.Threshold("< 500 ms", "time")
    t2 = threshold.Threshold("= 120 mi", "distance")
    t3 = threshold.Threshold("160", "currency")
    t4 = threshold.Threshold("60-80 Gbps", "throughput")
    print('t1: {}\nt2: {}\nt3: {}\nt4: {}\n'.format(t1, t2, t3, t4))

    template_file = dir_path + '/tests/data/' + template_name + '.yaml'
    fd = open(template_file, "r")
    template = yaml.load(fd)

    trns = Translator(conf, template_name, str(uuid.uuid4()), template)
    trns.translate()
    if trns.ok:
        print(json.dumps(trns.translation, indent=2))
    else:
        print("TESTING - Translator Error: {}".format(trns.error_message))


if __name__ == '__main__':
    main()
