#
# -------------------------------------------------------------------------
#   Copyright (c) 2018 OAM Technology Consulting LLC Intellectual Property
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
from datetime import datetime, timedelta
import json

from conductor.common import rest
from conductor.i18n import _LE, _LI

from oslo_log import log
LOG = log.getLogger(__name__)

from oslo_config import cfg
CONF = cfg.CONF

# TBD - read values from conductor.conf
AAF_OPTS = [
    cfg.BoolOpt('is_aaf_enabled',
                default=True,
                help='is_aaf_enabled.'),
    cfg.IntOpt('aaf_cache_expiry_hrs',
               default='3',
               help='aaf_cache_expiry_hrs.'),
    cfg.StrOpt('aaf_url',
               default='http://aaf-service:8100/authz/perms/user/',
               help='aaf_url.'),
    cfg.IntOpt('aaf_retries',
               default='3',
               help='aaf_retries.'),
    cfg.IntOpt('aaf_timeout',
               default='100',
               help='aaf_timeout.'),
    cfg.ListOpt('aaf_user_roles',
               default=['{"type": "org.onap.oof","instance": "plans","action": "GET"}',
                      '{"type": "org.onap.oof","instance": "plans","action": "POST"}'],
               help='aaf_user_roles.')
]

CONF.register_opts(AAF_OPTS, group='aaf_authentication')

AUTHZ_PERMS_USER = '{}/authz/perms/user/{}'

EXPIRE_TIME = 'expire_time'

perm_cache = {}

def clear_cache():
    perm_cache.clear()


def authenticate(uid, passwd):
    try:
        perms = get_aaf_permissions(uid, passwd)
        return has_valid_role(perms)
    except Exception as exp:
        LOG.error("Error Authenticating the user {} : {}: ".format(uid, exp))
        pass
    return False

"""
Check whether the user has valid permissions
return True if the user has valid permissions
else return false
"""

def has_valid_role(perms):
    aaf_user_roles = CONF.aaf_authentication.aaf_user_roles

    permObj = json.loads(perms)
    permList = permObj["perm"]
    for user_role in aaf_user_roles:
        role = json.loads(user_role)
        userType = role["type"]
        userInstance = role["instance"]
        userAction = role["action"]
        for perm in permList:
            permType = perm["type"]
            permInstance = perm["instance"]
            permAction = perm["action"]
            if userType == permType and userInstance == permInstance and \
                (userAction == permAction or userAction == "*"):
                return True
    return False

"""
Make the remote aaf api call if user is not in the cache.

Return the perms
"""
def get_aaf_permissions(uid, passwd):
    key = base64.b64encode("{}_{}".format(uid, passwd), "ascii")
    time_delta = timedelta(hours = CONF.aaf_authentication.aaf_cache_expiry_hrs)

# TBD - test cache logic
    perms = perm_cache.get(key)

    if perms and datetime.now() < perms.get(EXPIRE_TIME):
        LOG.debug("Returning cached value")
        return perms
    LOG.debug("Invoking AAF authentication API")
    response = remote_api(passwd, uid)
    perms = {EXPIRE_TIME: datetime.now() + time_delta, 'roles': response}
    perm_cache[key] = perms
    return response

def remote_api(passwd, uid):
    server_url = CONF.aaf_authentication.aaf_url.rstrip('/')
    kwargs = {
        "server_url": server_url,
        "retries": CONF.aaf_authentication.aaf_retries,
        "username": uid,
        "password": passwd,
        "log_debug": LOG.debug,
        "read_timeout": CONF.aaf_authentication.aaf_timeout,
    }
    restReq = rest.REST(**kwargs)

    headers = {"Accept": "application/json"}
    rkwargs = {
        "method": 'GET',
        "path": '',
        "headers": headers,
    }
    response = restReq.request(**rkwargs)

    if response is None:
        LOG.error(_LE("No response from AAF "))
    elif response.status_code != 200:
        LOG.error(_LE("AAF request  returned HTTP "
                      "status {} {}, link: {}").
                  format(response.status_code, response.reason,
                         server_url))
    return response.content

