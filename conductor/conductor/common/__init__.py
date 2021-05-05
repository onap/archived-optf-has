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

"""Music - Common Methods"""

from oslo_log import log as logging

from conductor.common import db_backend
from conductor.common.music import api

LOG = logging.getLogger(__name__)


def music_api(configuration):
    """Create or return a Music API instance"""

    configuration = dict(configuration)
    kwargs = {
        'host': configuration.get('host'),
        'port': configuration.get('port'),
        'version': configuration.get('version'),
        'replication_factor': configuration.get('replication_factor'),
    }
    api_instance = db_backend.get_client(**kwargs)

    # Create the keyspace if necessary
    # TODO(jdandrea): Use oslo.config with a [music] section
    # keyspace = conf.music.get('keyspace')
    # api_instance.create_keyspace(keyspace)
    return api_instance
