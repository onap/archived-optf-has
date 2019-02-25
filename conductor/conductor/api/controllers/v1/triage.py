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


from oslo_log import log
import pecan

from conductor.api.controllers import error
from conductor.i18n import _, _LI
from oslo_config import cfg

CONF = cfg.CONF


LOG = log.getLogger(__name__)


class TriageBaseController(object):
    """Triage Base Controller - Common Methods"""

    def triage_get(self, id=None):

        basic_auth_flag = CONF.conductor_api.basic_auth_secure

        if id == 'healthcheck' or \
        not basic_auth_flag or \
        (basic_auth_flag and check_basic_auth()):
            return self.data_getid(id)

    def data_getid(self, id):
        ctx = {}
        method = 'triage_get'
        if id:
            args = {'id': id}
            LOG.debug('triage data  {} requested.'.format(id))
        else:
            args = {}
            LOG.debug('All data in triage requested.')

        triage_data_list = []
        client = pecan.request.controller
        result = client.call(ctx, method, args)
        triage = result

        for tData in triage['triageData']:
            triage_data_list.append(tData)

        if id:
            if len(triage_data_list) == 1:
                return triage_data_list[0]
            else:
                # For a single triage, we return None if not found
                return None
        else:
            # For all tData, it's ok to return an empty list
            return triage_data_list


class TraigeDataItemController(TriageBaseController):
    """Triage Data Item Controller /v1/triage/{id}"""

    def __init__(self, uuid4):
        """Initializer."""
        self.uuid = uuid4
        self.triage = self.triage_get(id=self.uuid)

        if not self.triage:
            error('/errors/not_found',
                  _('DAta {} not found').format(self.uuid))
        pecan.request.context['id'] = self.uuid

    @classmethod
    def allow(cls):
        """Allowed methods"""
        return 'GET'

    @pecan.expose(generic=True, data='json')
    def index(self):
        """Catchall for unallowed methods"""
        message = _('The {} method is not allowed.').format(
            pecan.request.method)
        kwargs = {'allow': self.allow()}
        error('/errors/not_allowed', message, **kwargs)

    @index.when(method='OPTIONS', triage='json')
    def index_options(self):
        """Options"""
        pecan.response.headers['Allow'] = self.allow()
        pecan.response.status = 204

    @index.when(method='GET', triage='json')
    def index_get(self):
        """Get triage data """
        return self.triage

class TriageController(TriageBaseController):
    """tData Controller /v1/triage"""

    @classmethod
    def allow(cls):
        """Allowed methods"""
        return 'GET'

    @pecan.expose(generic=True, triage='json')
    def index(self):
        """Catchall for unallowed methods"""
        message = _('The {} method is not allowed.').format(
            pecan.request.method)
        kwargs = {'allow': self.allow()}
        error('/errors/not_allowed', message, **kwargs)

    @index.when(method='OPTIONS', triage='json')
    def index_options(self):
        """Options"""
        pecan.response.headers['Allow'] = self.allow()
        pecan.response.status = 204

    @index.when(method='GET', triage='json')
    def index_get(self):
        """Get all the tData"""
        tData = self.triage_get()
        return {"tData": tData}

    @pecan.expose()
    def _lookup(self, uuid4, *remainder):
        """Pecan subcontroller routing callback"""
        return TraigeDataItemController(uuid4), remainder


def check_basic_auth():
    '''
    :return: boolean
    '''

    try:
        if pecan.request.headers['Authorization'] and  verify_user(pecan.request.headers['Authorization']):
            LOG.debug("Authorized username and password")
            triage = True
        else:
            triage = False
            auth_str = pecan.request.headers['Authorization']
            user_pw = auth_str.split(' ')[1]
            decode_user_pw = base64.b64decode(user_pw)
            list_id_pw = decode_user_pw.split(':')
            LOG.error("Incorrect username={} / password={}".format(list_id_pw[0],list_id_pw[1]))
    except:
        error('/errors/basic_auth_error', _('Unauthorized: The request does not provide any HTTP authentication (basic authetnication)'))

    if not triage:
        error('/errors/authentication_error', _('Invalid credentials: username or password is incorrect'))
    return triage


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
