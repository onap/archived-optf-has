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
import conductor.common.music.model.transaction as Transaction



class TestTransaction(unittest.TestCase):

    def setUp(self):
        self.expectedValue = None

    def test_Transaction(self):
        self.assertEqual(self.expectedValue, Transaction.start())
        self.assertEqual(self.expectedValue, Transaction.start_read_only())
        self.assertEqual(self.expectedValue, Transaction.commit())
        self.assertEqual(self.expectedValue, Transaction.rollback())
        self.assertEqual(self.expectedValue, Transaction.clear())
        self.assertEqual(self.expectedValue, Transaction.flush())


if __name__ == "__main__":
    unittest.main()
