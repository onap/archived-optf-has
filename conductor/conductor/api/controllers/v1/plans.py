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
import six
import yaml
import base64
from yaml.constructor import ConstructorError

from notario import decorators
from notario.validators import types
from oslo_log import log
import pecan
from pecan_notario import validate

from conductor.api.controllers import error
from conductor.api.controllers import string_or_dict
from conductor.api.controllers import validator
from conductor.i18n import _, _LI
from oslo_config import cfg

from conductor.api.adapters.aaf import aaf_authentication as aaf_auth

CONF = cfg.CONF

LOG = log.getLogger(__name__)

CONDUCTOR_API_OPTS = [
    cfg.StrOpt('server_url',
               default='',
               help='Base URL for plans.'),
    cfg.StrOpt('username',
               default='',
               help='username for plans.'),
    cfg.StrOpt('password',
               default='',
               help='password for plans.'),
    cfg.BoolOpt('basic_auth_secure',
                default=True,
                help='auth toggling.'),
]

CONF.register_opts(CONDUCTOR_API_OPTS, group='conductor_api')

CREATE_SCHEMA = (
    (decorators.optional('files'), types.dictionary),
    (decorators.optional('id'), types.string),
    (decorators.optional('limit'), types.integer),
    (decorators.optional('name'), types.string),
    (decorators.optional('num_solution'), types.string),
    ('template', string_or_dict),
    (decorators.optional('template_url'), types.string),
    (decorators.optional('timeout'), types.integer),
)


class PlansBaseController(object):
    """Plans Base Controller - Common Methods"""

    def plan_link(self, plan_id):
        return [
            {
                "href": "%(url)s/v1/%(endpoint)s/%(id)s" %
                        {
                            'url': pecan.request.application_url,
                            'endpoint': 'plans',
                            'id': plan_id,
                        },
                "rel": "self"
            }
        ]

    def plans_get(self, plan_id=None):

        auth_flag = CONF.conductor_api.basic_auth_secure or CONF.aaf_api.is_aaf_enabled

        # TBD - is healthcheck properly supported?
        if plan_id == 'healthcheck' or \
                not auth_flag or \
                (auth_flag and check_auth()):
            return self.plan_getid(plan_id)

    def plan_getid(self, plan_id):
        ctx = {}
        method = 'plans_get'
        if plan_id:
            args = {'plan_id': plan_id}
            LOG.debug('Plan {} requested.'.format(plan_id))
        else:
            args = {}
            LOG.debug('All plans requested.')

        plans_list = []

        client = pecan.request.controller
        result = client.call(ctx, method, args)
        plans = result and result.get('plans')

        for the_plan in plans:
            the_plan_id = the_plan.get('id')
            the_plan['links'] = [self.plan_link(the_plan_id)]
            plans_list.append(the_plan)

        if plan_id:
            if len(plans_list) == 1:
                return plans_list[0]
            else:
                # For a single plan, we return None if not found
                return None
        else:
            # For all plans, it's ok to return an empty list
            return plans_list

    def plan_create(self, args):
        ctx = {}
        method = 'plan_create'

        # TODO(jdandrea): Enhance notario errors to use similar syntax
        # valid_keys = ['files', 'id', 'limit', 'name',
        #               'template', 'template_url', 'timeout']
        # if not set(args.keys()).issubset(valid_keys):
        #     invalid = [name for name in args if name not in valid_keys]
        #     invalid_str = ', '.join(invalid)
        #     error('/errors/invalid',
        #           _('Invalid keys found: {}').format(invalid_str))
        # required_keys = ['template']
        # if not set(required_keys).issubset(args):
        #     required = [name for name in required_keys if name not in args]
        #     required_str = ', '.join(required)
        #     error('/errors/invalid',
        #           _('Missing required keys: {}').format(required_str))

        LOG.debug('Plan creation requested (name "{}").'.format(
            args.get('name')))

        client = pecan.request.controller

        transaction_id = pecan.request.headers.get('transaction-id')
        if transaction_id:
            args['template']['transaction-id'] = transaction_id

        result = client.call(ctx, method, args)
        plan = result and result.get('plan')

        if plan:
            plan_name = plan.get('name')
            plan_id = plan.get('id')
            plan['links'] = [self.plan_link(plan_id)]
            LOG.info(_LI('Plan {} (name "{}") created.').format(
                plan_id, plan_name))

        return plan

    def plan_delete(self, plan):
        ctx = {}
        method = 'plans_delete'

        plan_name = plan.get('name')
        plan_id = plan.get('id')
        LOG.debug('Plan {} (name "{}") deletion requested.'.format(
            plan_id, plan_name))

        args = {'plan_id': plan_id}
        client = pecan.request.controller
        client.call(ctx, method, args)
        LOG.info(_LI('Plan {} (name "{}") deleted.').format(
            plan_id, plan_name))


class PlansItemController(PlansBaseController):
    """Plans Item Controller /v1/plans/{plan_id}"""

    def __init__(self, uuid4):
        """Initializer."""
        self.uuid = uuid4
        self.plan = self.plans_get(plan_id=self.uuid)

        if not self.plan:
            error('/errors/not_found',
                  _('Plan {} not found').format(self.uuid))
        pecan.request.context['plan_id'] = self.uuid

    @classmethod
    def allow(cls):
        """Allowed methods"""
        return 'GET,DELETE'

    @pecan.expose(generic=True, template='json')
    def index(self):
        """Catchall for unallowed methods"""
        message = _('The {} method is not allowed.').format(
            pecan.request.method)
        kwargs = {'allow': self.allow()}
        error('/errors/not_allowed', message, **kwargs)

    @index.when(method='OPTIONS', template='json')
    def index_options(self):
        """Options"""
        pecan.response.headers['Allow'] = self.allow()
        pecan.response.status = 204

    @index.when(method='GET', template='json')
    def index_get(self):
        """Get plan"""
        return {"plans": [self.plan]}

    @index.when(method='DELETE', template='json')
    def index_delete(self):
        """Delete a Plan"""
        self.plan_delete(self.plan)
        pecan.response.status = 204


class PlansController(PlansBaseController):
    """Plans Controller /v1/plans"""

    @classmethod
    def allow(cls):
        """Allowed methods"""
        return 'GET,POST'

    @pecan.expose(generic=True, template='json')
    def index(self):
        """Catchall for unallowed methods"""
        message = _('The {} method is not allowed.').format(
            pecan.request.method)
        kwargs = {'allow': self.allow()}
        error('/errors/not_allowed', message, **kwargs)

    @index.when(method='OPTIONS', template='json')
    def index_options(self):
        """Options"""
        pecan.response.headers['Allow'] = self.allow()
        pecan.response.status = 204

    @index.when(method='GET', template='json')
    def index_get(self):
        """Get all the plans"""
        plans = self.plans_get()
        return {"plans": plans}

    @index.when(method='POST', template='json')
    @validate(CREATE_SCHEMA, '/errors/schema')
    def index_post(self):
        """Create a Plan"""

        # Look for duplicate keys in the YAML/JSON, first in the
        # entire request, and then again if the template parameter
        # value is itself an embedded JSON/YAML string.
        where = "API Request"
        try:
            parsed = yaml.load(pecan.request.text, validator.UniqueKeyLoader)
            if 'template' in parsed:
                where = "Template"
                template = parsed['template']
                if isinstance(template, six.string_types):
                    yaml.load(template, validator.UniqueKeyLoader)
        except ConstructorError as exc:
            # Only bail on the duplicate key problem (problem and problem_mark
            # attributes are available in ConstructorError):
            if exc.problem is \
                    validator.UniqueKeyLoader.DUPLICATE_KEY_PROBLEM_MARK:
                # ConstructorError messages have a two line snippet.
                # Grab it, get rid of the second line, and strip any
                # remaining whitespace so we can fashion a one line msg.
                snippet = exc.problem_mark.get_snippet()
                snippet = snippet.split('\n')[0].strip()
                msg = _('{} has a duplicate key on line {}: {}')
                error('/errors/invalid',
                      msg.format(where, exc.problem_mark.line + 1, snippet))
        except Exception as exc:
            # Let all others pass through for now.
            pass

        args = pecan.request.json

        # Print request id from SNIOR at the beginning of API component
        if args and args['name']:
            LOG.info('Plan name: {}'.format(args['name']))

        auth_flag = CONF.conductor_api.basic_auth_secure or CONF.aaf_api.is_aaf_enabled

        # Create the plan only when the basic authentication is disabled or pass the authenticaiton check
        if not auth_flag or \
                (auth_flag and check_auth()):
            plan = self.plan_create(args)

        if not plan:
            error('/errors/server_error', _('Unable to create Plan.'))
        else:
            pecan.response.status = 201
            return plan

    @pecan.expose()
    def _lookup(self, uuid4, *remainder):
        """Pecan subcontroller routing callback"""
        return PlansItemController(uuid4), remainder


def check_auth():
    """
    Returns True/False if the username/password of Basic Auth match/not match
    Will also check role-based access controls if AAF integration configured
    :return boolean value
    """

    try:
        if pecan.request.headers['Authorization'] and verify_user(pecan.request.headers['Authorization']):
            LOG.debug("Authorized username and password")
            plan = True
        else:
            plan = False
            auth_str = pecan.request.headers['Authorization']
            user_pw = auth_str.split(' ')[1]
            decode_user_pw = base64.b64decode(user_pw.encode()).decode()
            list_id_pw = decode_user_pw.split(':')
            LOG.error("Incorrect username={} / password={}".format(list_id_pw[0], list_id_pw[1]))
    except:
        error('/errors/basic_auth_error', _('Unauthorized: The request does not '
                                            'provide any HTTP authentication (basic authentication)'))
        plan = False

    if not plan:
        error('/errors/authentication_error', _('Invalid credentials: username or password is incorrect'))

    return plan


def verify_user(authstr):
    """
    authenticate user as per config file or AAF authentication service
    :param authstr:
    :return boolean value
    """
    user_dict = dict()
    auth_str = authstr
    user_pw = auth_str.split(' ')[1]
    user_pw = user_pw.encode()   # below function needs user_pw in bytes object in python 3 so converting that
    decode_user_pw = base64.b64decode(user_pw)
    list_id_pw = decode_user_pw.decode().split(':')
    user_dict['username'] = str(list_id_pw[0])
    user_dict['password'] = str(list_id_pw[1])
    password = CONF.conductor_api.password
    username = CONF.conductor_api.username

#    print ("plans.verify_user(): Expected username/password: {}/{}".format(username, password))
#    print ("plans.verify_user(): Provided username/password: {}/{}".format(user_dict['username'], user_dict['password']))

    retVal = False

    if CONF.aaf_api.is_aaf_enabled:
        retVal = aaf_auth.authenticate(user_dict['username'], user_dict['password'])
    else:
        if username == user_dict['username'] and password == user_dict['password']:
            retVal = True

    return retVal

