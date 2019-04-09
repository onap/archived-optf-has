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
import conductor.common.utils.basic_auth_util as BaseAuthUtil
from conductor.i18n import _, _LI, _LE


class TestBaseAuthUtil(unittest.TestCase):
    def setUp(self):
        self.userId = 'Test'
        self.userId = 'Password'

    def test_basic_auth_util(self):
        self.authorization_val = _LE(BaseAuthUtil.encode(self.userId, self.userId))
        self.assertEqual('Basic UGFzc3dvcmQ6UGFzc3dvcmQ=', self.authorization_val)


if __name__ == "__main__":
    unittest.main()
