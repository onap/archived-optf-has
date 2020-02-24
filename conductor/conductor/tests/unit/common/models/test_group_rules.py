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

"""Test class for model group_rules"""

import unittest
from conductor.common.models.group_rules import GroupRules

class TestGroupRules(unittest.TestCase):

    def setUp(self):
        self.groupRules = GroupRules()
        self.values = {'group': None, 'id': None}

    def test_GroupRules(self):
        self.assertEqual(True, self.groupRules.atomic())
        self.assertEqual("id", self.groupRules.pk_name())
        self.assertEqual(None, self.groupRules.pk_value())
        self.assertEqual(self.values, list(self.groupRules.values()))
        self.assertEqual(None, self.groupRules.__json__().get('rule'))
        self.assertEqual("text", self.groupRules.schema().get('id'))


if __name__ == '__main__':
        unittest.main()
