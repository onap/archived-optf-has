#
# -------------------------------------------------------------------------
#   Copyright (C) 2019 IBM.
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

"""Test class for optimizer random_pick.py"""

import unittest
from conductor.common.music import api
from conductor.solver.optimizer.random_pick import RandomPick
from oslo_config import cfg
from mock import patch

class TestRandomPick(unittest.TestCase):

    @patch('conductor.solver.optimizer')
    @patch('conductor.common.music.model.base.Base.table_create')
    @patch('conductor.common.music.model.base.Base.insert')
    def setUp(self, conf, _requests=None, _begin_time=None):
        self.music = api.API()
        self.conf = cfg.CONF
        self.randomPick = RandomPick(self.conf)

    def test_search(self):
        _demand_list = list()
        self.assertEqual(None, self.randomPick.search(_demand_list, '_request').current_demand)


if __name__ == '__main__':
    unittest.main()
