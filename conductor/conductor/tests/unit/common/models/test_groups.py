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

"""Test class for model group"""

import unittest
from conductor.common.models.groups import Groups


class TestGroups(unittest.TestCase):
    def setUp(self):
        self.groups = Groups()

    def test_groups(self):
        self.assertEqual(True, self.groups.atomic())
        self.assertEqual("id", self.groups.pk_name())
        self.assertEqual(None, self.groups.pk_value())

        self.values = {'group': None, 'id': None}
        self.assertEqual(self.values, list(self.groups.values()))
        self.assertEqual(None, self.groups.__json__().get("group"))
        self.assertEqual('<Groups None>', self.groups.__repr__())
        self.assertEqual('text', self.groups.schema().get("id"))


if __name__ == '__main__':
    unittest.main()
