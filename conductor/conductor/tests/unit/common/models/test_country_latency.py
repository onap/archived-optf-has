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

"""Test class for model country_latency"""

import unittest
from conductor.common.models.country_latency import CountryLatency


class TestCountryLatency(unittest.TestCase):

    def setUp(self):
        self.countryLatency = CountryLatency()

    def test_CountryLatency(self):
        self.assertEqual(True, self.countryLatency.atomic())
        self.assertEqual("id", self.countryLatency.pk_name())
        self.assertEqual(None, self.countryLatency.pk_value())
        self.value = {'country_name': None, 'groups': None}
        self.assertEqual(self.value, list(self.countryLatency.values()))
        self.assertEqual("text", self.countryLatency.schema().get("country_name"))
        self.assertEqual(None, self.countryLatency.__json__().get("groups"))


if __name__ == '__main__':
    unittest.main()
