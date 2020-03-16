#
# -------------------------------------------------------------------------
#   Copyright (c) 2015-2018 AT&T Intellectual Property
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

import base64

from notario import decorators
from notario.validators import types
from oslo_log import log
import pecan

from conductor.api.controllers import error
from conductor.api.controllers import string_or_dict
from conductor.i18n import _, _LI
from oslo_config import cfg

CONF = cfg.CONF


LOG = log.getLogger(__name__)

class TestRuleBaseController(object):

    def test_rule(self, args):

        ctx = {}
        method = 'test_rule'
        client = pecan.request.controller
        response = client.call(ctx, method, args)

        return response

class TestRuleController(TestRuleBaseController):

    @classmethod
    def allow(cls):
        """Allowed methods"""
        return 'POST'

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


    @index.when(method='POST', template='json')
    # @validate(CREATE_SCHEMA, '/errors/schema')
    def index_post(self):

        args = pecan.request.json

        if check_basic_auth():
            response = self.test_rule(args)
        if not response:
            error('/errors/server_error', _('Unable to release orders'))
        else:
            pecan.response.status = 201
            return response


def check_basic_auth():
    '''
    :return: boolean
    '''

    try:
        if pecan.request.headers['Authorization'] and  verify_user(pecan.request.headers['Authorization']):
            LOG.debug("Authorized username and password")
            plan = True
        else:
            plan = False
            auth_str = pecan.request.headers['Authorization']
            user_pw = auth_str.split(' ')[1]
            decode_user_pw = base64.b64decode(user_pw)
            list_id_pw = decode_user_pw.split(':')
            LOG.error("Incorrect username={} / password={}".format(list_id_pw[0],list_id_pw[1]))
    except:
        error('/errors/basic_auth_error', _('Unauthorized: The request does not provide any HTTP authentication (basic authetnication)'))

    if not plan:
        error('/errors/authentication_error', _('Invalid credentials: username or password is incorrect'))
    return plan


def verify_user(authstr):
    """
    authenticate user as per config file
    :param headers:
    :return boolean value
    """
    user_dict = dict()
    auth_str = authstr
    user_pw = auth_str.split(' ')[1]
    decode_user_pw = base64.b64decode(user_pw)
    list_id_pw = decode_user_pw.split(':')
    user_dict['username'] = list_id_pw[0]
    user_dict['password'] = list_id_pw[1]
    password = CONF.conductor_api.password
    username = CONF.conductor_api.username
    if username == user_dict['username'] and password == user_dict['password']:
        return True
    else:
        return False

