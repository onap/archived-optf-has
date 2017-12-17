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

CONF = cfg.CONF

MUSIC_API_COMMON_OPTS = [
    cfg.BoolOpt('debug',
                default=False,
                help='Log debug messages. '
                     'Default value is False.'),
]

CONF.register_opts(MUSIC_API_COMMON_OPTS, group='music_api')
