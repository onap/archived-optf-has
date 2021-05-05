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

import time

from oslo_config import cfg

from conductor.common import db_backend
from conductor import service

CONF = cfg.CONF


def current_time_millis():
    """Current time in milliseconds."""
    return int(round(time.time() * 1000))


def main():
    """Sample usage of Music."""
    service.prepare_service()
    CONF.set_override('debug', True, 'music_api')
    CONF.set_override('mock', True, 'music_api')
    CONF.set_override('hostnames', ['music2'], 'music_api')
    music = db_backend.get_client()
    print("Music version %s" % music.version())

    # Randomize the name so that we don't step on each other.
    keyspace = 'NewVotingApp' + str(current_time_millis() / 100)
    music.keyspace_create(keyspace)

    # Create the table
    kwargs = {
        'keyspace': keyspace,
        'table': 'votecount',
        'schema': {
            'name': 'text',
            'count': 'varint',
            'PRIMARY KEY': '(name)'
        }
    }
    music.table_create(**kwargs)

    # Candidate data
    data = {
        'Joe': 5,
        'Shankar': 7,
        'Gueyoung': 8,
        'Matti': 2,
        'Kaustubh': 0
    }

    # Create an entry in the voting table for each candidate
    # and with a vote count of 0.
    kwargs = {'keyspace': keyspace, 'table': 'votecount', 'pk_name': 'name'}
    for name in data:  # We only want the keys
        kwargs['pk_value'] = name
        kwargs['values'] = {'name': name, 'count': 0}
        music.row_create(**kwargs)

    # Update each candidate's count atomically.
    kwargs = {'keyspace': keyspace, 'table': 'votecount', 'pk_name': 'name'}
    for name in data:
        count = data[name]
        kwargs['pk_value'] = name
        kwargs['values'] = {'count': count}
        kwargs['atomic'] = True
        music.row_update(**kwargs)

    # Read all rows
    kwargs = {'keyspace': keyspace, 'table': 'votecount'}
    print(music.row_read(**kwargs))  # Reads all rows

    # Delete Joe, read Matti
    kwargs = {'keyspace': keyspace, 'table': 'votecount', 'pk_name': 'name'}
    kwargs['pk_value'] = 'Joe'
    music.row_delete(**kwargs)
    kwargs['pk_value'] = 'Matti'
    print(music.row_read(**kwargs))

    # Read all rows again
    kwargs = {'keyspace': keyspace, 'table': 'votecount'}
    print(music.row_read(**kwargs))  # Reads all rows

    # Cleanup.
    music.keyspace_delete(keyspace)


if __name__ == "__main__":
    main()
