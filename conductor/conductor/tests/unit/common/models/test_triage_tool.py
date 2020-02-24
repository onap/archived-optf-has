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

"""Test class for model triage_tool"""

import unittest
from conductor.common.models.triage_tool import TriageTool

class TestTriageTool(unittest.TestCase):

    def setUp(self):
        self.triageTool = TriageTool()
        self.values = {'triage_solver': 'null', 'optimization_type': None, 'triage_translator': 'null', 'id': None, 'name': None}

    def test_TriageTool(self):
        self.assertEqual(True, self.triageTool.atomic())
        self.assertEqual("id", self.triageTool.pk_name())
        self.assertEqual(None, self.triageTool.pk_value())
        self.assertEqual(self.values, list(self.triageTool.values()))
        self.assertEqual(None, self.triageTool.__json__().get('name'))
        self.assertEqual("text", self.triageTool.schema().get('optimization_type'))


if __name__ == '__main__':
        unittest.main()
