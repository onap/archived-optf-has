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
"""Base classes for conductor/api tests."""

import os

import eventlet
import mock
import base64

eventlet.monkey_patch(os=False)

import pecan
import pecan.testing
from oslo_config import cfg
from oslo_config import fixture as config_fixture
from oslo_serialization import jsonutils
from oslotest import base as oslo_test_base


class BaseApiTest(oslo_test_base.BaseTestCase):
    """Pecan controller functional testing class.

    Used for functional tests of Pecan controllers where you need to
    test your literal application and its integration with the
    framework.
    """

    extra_environment = {
        'AUTH_TYPE': 'Basic',
        'HTTP_AUTHORIZATION': 'Basic {}'.format(base64.encodestring('admin:default'.encode()).decode().strip())}

    def setUp(self):
        print("setup called ... ")
        super(BaseApiTest, self).setUp()
        # self._set_config()
        # TODO(dileep.ranganathan): Move common mock and configs to BaseTest
        cfg.CONF.set_override('mock', True, 'music_api')
        cfg.CONF.set_override('username', "admin", 'conductor_api')
        cfg.CONF.set_override('password', "default", 'conductor_api')

        self.app = self._make_app()

        def reset_pecan():
            pecan.set_config({}, overwrite=True)

        self.addCleanup(reset_pecan)


    def _make_app(self):
        # Determine where we are so we can set up paths in the config

        self.app_config = {
            'app': {
                'root': 'conductor.api.controllers.root.RootController',
                'modules': ['conductor.api'],
            },
        }

        return pecan.testing.load_test_app(self.app_config, conf=cfg.CONF)

    def path_get(self, project_file=None):
        """Get the absolute path to a file. Used for testing the API.

        :param project_file: File whose path to return. Default: None.
        :returns: path to the specified file, or path to project root.
        """
        root = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            '..',
                                            '..',
                                            )
                               )
        if project_file:
            return os.path.join(root, project_file)
        else:
            return root

    def _set_config(self):
        self.cfg_fixture = self.useFixture(config_fixture.Config(cfg.CONF))
        self.cfg_fixture.config(keyspace='conductor_rpc',
                                group='messaging_server')

    def assertJsonEqual(self, expected, observed):
        """Asserts that 2 complex data structures are json equivalent."""
        self.assertEqual(jsonutils.dumps(expected, sort_keys=True),
                         jsonutils.dumps(observed, sort_keys=True))
