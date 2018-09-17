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

from oslo_config import cfg
from oslo_log import log

LOG = log.getLogger(__name__)
CONF = cfg.CONF

SDNC_OPTS = [
    cfg.IntOpt('cache_refresh_interval',
               default=1440,
               help='Interval with which to refresh the local cache, '
                    'in minutes.'),
    cfg.StrOpt('table_prefix',
               default='sdnc',
               help='Data Store table prefix.'),
    cfg.StrOpt('server_url',
               default='https://controller:8443/restconf/',
               help='Base URL for SDN-C, up to and including the version.'),
    cfg.StrOpt('username',
               help='Basic Authentication Username'),
    cfg.StrOpt('password',
               help='Basic Authentication Password'),
    cfg.StrOpt('sdnc_rest_timeout',
               default=30,
               help='Timeout for SDNC Rest Call'),
    cfg.StrOpt('sdnc_retries',
               default=3,
               help='Retry Numbers for SDNC Rest Call'),
]

CONF.register_opts(SDNC_OPTS, group='')

class SNIRO_Callback():

    def __init__(self):
        """Initializer"""
        self.conf = CONF


    def call_SNIRO(self):
        pass
        #call SNIRO manager and inform about the sstatus update






