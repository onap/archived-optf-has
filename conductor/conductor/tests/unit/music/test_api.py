#
# -------------------------------------------------------------------------
#   Copyright (c) 2018 Intel Corporation Intellectual Property
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
import unittest

import mock
from conductor.common import rest
from conductor.common.music.api import MusicAPI
from oslo_config import cfg


class TestMusicApi(unittest.TestCase):

    def setUp(self):
        cfg.CONF.set_override('debug', True, 'music_api')
        self.mock_lock_id = mock.patch.object(MusicAPI, '_lock_id_create',
                                              return_value='12345678')
        self.mock_lock_name = mock.patch.object(MusicAPI,
                                                '_lock_name_generate',
                                                return_value='tempname')
        self.mock_lock_acquire = mock.patch.object(MusicAPI,
                                                   '_lock_id_acquire',
                                                   return_value=True)
        self.mock_lock_release = mock.patch.object(MusicAPI,
                                                   '_lock_id_release',
                                                   return_value=True)
        self.mock_lock_id.start()
        self.mock_lock_name.start()
        self.mock_lock_acquire.start()
        self.mock_lock_release.start()
        self.music_api = MusicAPI()

    def tearDown(self):
        mock.patch.stopall()

    @mock.patch('conductor.common.rest.REST.request')
    def test_row_create(self, rest_mock):
        keyspace = 'test-keyspace'
        kwargs = {'keyspace': keyspace, 'table': 'votecount',
                  'pk_name': 'name'}
        kwargs['pk_value'] = 'test-name'
        kwargs['values'] = {'name': 'test-name', 'count': 0}
        response = mock.MagicMock()
        response.status_code = 200
        response.ok = True
        rest_mock.return_value = response
        self.assertEquals(True, self.music_api.row_create(**kwargs))

    @mock.patch('conductor.common.rest.REST.request')
    def test_row_update(self, rest_mock):
        keyspace = 'test-keyspace'
        kwargs = {'keyspace': keyspace, 'table': 'votecount',
                  'pk_name': 'name'}
        count = 2
        kwargs['pk_value'] = 'test-name2'
        kwargs['values'] = {'count': count}
        kwargs['atomic'] = True
        response = mock.MagicMock()
        response.status_code = 200
        response.ok = True
        rest_mock.return_value = response
        print(self.mock_lock_id)
        self.assertEquals(True, self.music_api.row_update(**kwargs))

    def test_table_path_generate(self):
        keyspace = 'test-keyspace'
        kwargs = {
            'keyspace': keyspace,
            'table': 'votecount'
        }
        expected = '/keyspaces/test-keyspace/tables/votecount/'
        self.assertEqual(expected,
                         self.music_api._table_path_generate(**kwargs))

    @mock.patch('conductor.common.rest.REST.request')
    def test_table_create(self, rest_mock):
        # Create the table
        keyspace = 'test-keyspace'
        kwargs = {
            'keyspace': keyspace,
            'table': 'votecount',
            'schema': {
                'name': 'text',
                'count': 'varint',
                'PRIMARY KEY': '(name)'
            }
        }

        response = mock.MagicMock()
        response.status_code = 200
        response.ok = True
        rest_mock.return_value = response
        self.assertEquals(True, self.music_api.table_create(**kwargs))

    @mock.patch('conductor.common.rest.REST.request')
    def test_table_delete(self, rest_mock):
        # Delete the table
        keyspace = 'test-keyspace'
        kwargs = {
            'keyspace': keyspace,
            'table': 'votecount'
        }

        response = mock.MagicMock()
        response.status_code = 200
        response.ok = True
        rest_mock.return_value = response
        self.assertEquals(True, self.music_api.table_delete(**kwargs))

    def test_version(self):
        with mock.patch.object(rest.REST, 'request',
                               autospec=True) as rest_mock:
            response = mock.MagicMock()
            response.status = 200
            response.text = 'MUSIC:2.2.14'
            rest_mock.return_value = response
            self.assertEquals('MUSIC:2.2.14', self.music_api.version())


if __name__ == "__main__":
    unittest.main()
