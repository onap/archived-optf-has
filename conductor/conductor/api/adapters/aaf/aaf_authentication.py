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
import os

from conductor.common import rest
from conductor.i18n import _LE, _LI
from conductor.common.utils import cipherUtils

from oslo_log import log
LOG = log.getLogger(__name__)

from oslo_config import cfg
CONF = cfg.CONF

AAF_OPTS = [
    cfg.BoolOpt('is_aaf_enabled',
                default=False,
                help='is_aaf_enabled.'),
    cfg.IntOpt('aaf_cache_expiry_hrs',
               default='24',
               help='aaf_cache_expiry_hrs.'),
    cfg.StrOpt('aaf_url',
               default='https://aaf-service:8100/authz/perms/user/',
               help='aaf_url.'),
    cfg.StrOpt('username',
               default=None,
               help='username.'),
    cfg.StrOpt('password',
               default=None,
               help='pasword.'),
    cfg.StrOpt('aaf_cert_file',
               default=None,
               help='aaf_cert_file.'),
    cfg.StrOpt('aaf_cert_key_file',
               default=None,
               help='aaf_cert_key_file.'),
    cfg.StrOpt('aaf_ca_bundle_file',
               default="",
               help='aaf_ca_bundle_file.'),
    cfg.IntOpt('aaf_retries',
               default='3',
               help='aaf_retries.'),
    cfg.IntOpt('aaf_timeout',
               default='100',
               help='aaf_timeout.'),
    cfg.StrOpt('aaf_conductor_user',
               default=None,
               help='aaf_conductor_user.'),
    cfg.ListOpt('aaf_permissions',
               default=['{"type": "org.onap.oof.access","instance": "*","action": "*"}'],
               help='aaf_user_roles.')
]

CONF.register_opts(AAF_OPTS, group='aaf_api')

EXPIRE_TIME = 'expire_time'

perm_cache = {}

def clear_cache():
    perm_cache.clear()

def authenticate(uid, passwd):
    aafUser = None
    username = CONF.conductor_api.username
    password = cipherUtils.AESCipher.get_instance().decrypt(CONF.conductor_api.password)
    if username == uid and password == passwd:
        aafUser = CONF.aaf_api.aaf_conductor_user
    else:
        LOG.debug("Error Authenticating the user {} ".format(uid))
        return False

    try:
        perms = get_aaf_permissions(aafUser)
        return has_valid_permissions(perms)
    except Exception as exp:
        LOG.error("Error Authenticating the user {} : {}: ".format(uid, exp))
    return False

"""
Check whether the user has valid permissions
return True if the user has valid permissions
else return false
"""

def has_valid_permissions(userPerms):
    permissions = CONF.aaf_api.aaf_permissions

    LOG.info("Validate permisions: acquired permissions {} ".format(userPerms))
    LOG.info("Validate permisions: allowed permissions {} ".format(permissions))

    userPermObj = json.loads(userPerms)
    userPermList = userPermObj["perm"]
    for perm in permissions:
        permObj = json.loads(perm)
        permType = permObj["type"]
        permInstance = permObj["instance"]
        permAction = permObj["action"]
        for userPerm in userPermList:
            userType = userPerm["type"]
            userInstance = userPerm["instance"]
            userAction = userPerm["action"]
            if userType == permType and userInstance == permInstance and \
                (userAction == permAction or userAction == "*"):
                # FS - trace
                LOG.info("User has valid permissions ")
                return True
    return False

"""
Make the remote aaf api call if user is not in the cache.

Return the perms
"""
def get_aaf_permissions(aafUser):
    key = base64.b64encode("{}".format(aafUser), "ascii")
    time_delta = timedelta(hours = CONF.aaf_api.aaf_cache_expiry_hrs)

    perms = perm_cache.get(key)

    if perms and datetime.now() < perms.get(EXPIRE_TIME):
        LOG.debug("Returning cached value")
        return perms['roles']
    LOG.debug("Invoking AAF authentication API")
    response = remote_api(aafUser)
    perms = {EXPIRE_TIME: datetime.now() + time_delta, 'roles': response}
    perm_cache[key] = perms
    return response


"""
The remote api is the AAF service

"""
def remote_api(aafUser):
    server_url = CONF.aaf_api.aaf_url+aafUser

    kwargs = {
        "server_url": server_url,
        "retries": CONF.aaf_api.aaf_retries,
        "username": CONF.aaf_api.username,
        "password": cipherUtils.AESCipher.get_instance().decrypt(CONF.aaf_api.password),
        "log_debug": LOG.debug,
        "read_timeout": CONF.aaf_api.aaf_timeout,
        "cert_file": CONF.aaf_api.aaf_cert_file,
        "cert_key_file": CONF.aaf_api.aaf_cert_key_file,
        "ca_bundle_file": CONF.aaf_api.aaf_ca_bundle_file,
    }
    restReq = rest.REST(**kwargs)

    headers = {"Accept": "application/Perms+json;q=1.0;charset=utf-8;version=2.1,application/json;q=1.0;version=2.1,*/*;q=1.0"}
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

