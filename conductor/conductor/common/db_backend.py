#
# -------------------------------------------------------------------------
#   Copyright (C) 2021 Wipro Limited.
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

from conductor.common.etcd.api import EtcdAPI
from conductor.common.music.api import MockAPI
from conductor.common.music.api import MusicAPI

CONF = cfg.CONF

DB_BACKEND_OPTS = [
    cfg.StrOpt('db_backend',
               default='music',
               help='DB backend to use for conductor.'),
    cfg.BoolOpt('music_mock',
                default=False,
                help='use mock api.'),
]

CONF.register_opts(DB_BACKEND_OPTS, group='db_options')

global DB_API


def get_client():
    """Wrapper for Music and Music Mock API"""

    global DB_API

    if CONF.db_options.db_backend == "etcd":
        DB_API = EtcdAPI()
    elif CONF.db_options.db_backend == "music":
        if CONF.db_options.music_mock:
            DB_API = MockAPI()
        DB_API = MusicAPI()
    return DB_API
