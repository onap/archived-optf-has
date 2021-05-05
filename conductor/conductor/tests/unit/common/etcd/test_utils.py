#
# -------------------------------------------------------------------------
#   Copyright (C) 2021 Wipro Limited.
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
import unittest
from conductor.common.etcd.utils import validate_schema
from conductor.common.models.plan import Plan


class TestUtils(unittest.TestCase):

    def test_validate_schema(self):
        schema = Plan.schema()
        plan = {
            "id": "12345",
            "status": "template",
            "created": time.time(),
            "updated": time.time(),
            "name": "sample",
            "timeout": 60
        }
        self.assertTrue(validate_schema(plan, schema))
        plan["abc"] = "xyz"
        self.assertFalse(validate_schema(plan, schema))
        plan.pop("abc")
        plan.pop("id")
        self.assertFalse(validate_schema(plan, schema))
