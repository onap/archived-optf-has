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
                default=False,
                help='is_aaf_enabled.'),
    cfg.IntOpt('aaf_cache_expiry_hrs',
               default='3',
               help='aaf_cache_expiry_hrs.'),
    cfg.StrOpt('aaf_url',
               default='https://aaf-onap-test.osaaf.org:8100/authz/perms/user/',
               help='aaf_url.'),
    cfg.StrOpt('aaf_username',
               default='aaf_admin@people.osaaf.org',
               help='aaf_username.'),
    cfg.StrOpt('aaf_password',
               default='demo123456!',
               help='aaf_pasword.'),
    cfg.StrOpt('aaf_cert_file',
               default='AAF_RootCA.cer',
               help='aaf_cert_file.'),
    cfg.StrOpt('aaf_cert_key_file',
               default='org.onap.oof.keyfile',
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
#    cfg.ListOpt('aaf_users',
#               default=['{"clientId": "conductor","user": "oof@oof.onap.org"}'],
    cfg.StrOpt('aaf_conductor_user',
               default="oof@oof.onap.org",
               help='aaf_users.'),
    cfg.ListOpt('aaf_permissions',
               default=['{"type": "org.onap.oof.access","instance": "*","action": "*"}'],
               help='aaf_user_roles.')
]


CONF.register_opts(AAF_OPTS, group='aaf_authentication')

EXPIRE_TIME = 'expire_time'

perm_cache = {}

def clear_cache():
    perm_cache.clear()

"""
TBD: In authenticate() would prefer to walk a list of clients to map username:password to AAF user identify, but syntax
of config.ListOpt is unclear in configuration file.  Only tested client is conductor so just match
that for now
    # check username, password of OOF client. There may be multiple clients, each mapped to 
    # a user in AAF
    aafUser = None
    username = password = None
    aaf_users = CONF.aaf_authentication.aaf_users
    for users in aaf_users:
        userDict = json.loads(users)
        clientId = userDict["clientId"].encode('UTF-8')
        if clientId == "conductor":
            username = CONF.conductor_api.username
            password = CONF.conductor_api.password
        user = userDict["user"].encode('UTF-8')
        if username == uid and password == passwd:
            aafUser = user
"""

def authenticate(uid, passwd):
    username = CONF.conductor_api.username
    password = CONF.conductor_api.password
    aaf_users = CONF.aaf_authentication.aaf_users
    if username == uid and password == passwd:
        aafUser = CONF.aaf_authentication.aaf_conductor_user
    
    try:
        perms = get_aaf_permissions(aafUser)
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

def has_valid_role(userPerms):
    aaf_permissions = CONF.aaf_authentication.aaf_permissions

    permObj = json.loads(userPerms)
    permList = permObj["perm"]
    for aaf_perm in aaf_permissions:
        role = json.loads(aaf_perm)
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
def get_aaf_permissions(aafUser):
    key = base64.b64encode("{}".format(aafUser), "ascii")
    time_delta = timedelta(hours = CONF.aaf_authentication.aaf_cache_expiry_hrs)

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
#    server_url = CONF.aaf_authentication.aaf_url.rstrip('/')
    server_url = CONF.aaf_authentication.aaf_url+aafUser
    kwargs = {
        "server_url": server_url,
        "retries": CONF.aaf_authentication.aaf_retries,
        "username": CONF.aaf_authentication.aaf_username,
        "password": CONF.aaf_authentication.aaf_password,
        "log_debug": LOG.debug,
        "read_timeout": CONF.aaf_authentication.aaf_timeout,
        # TBD - get certs to work
#        "cert_file": CONF.aaf_authentication.aaf_cert_file,
#        "cert_key_file": CONF.aaf_authentication.aaf_cert_key_file,
        # This will set TLS verify to False, see rest.py
        "ca_bundle_file": CONF.aaf_authentication.aaf_ca_bundle_file,
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

