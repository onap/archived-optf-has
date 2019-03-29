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
"""Test classes for adiod_controller"""

import conductor.conf.adiod_controller as adiodc

import unittest
from oslo_config import cfg

class TestAdiodController(unittest.TestCase):
    def setUp(self):
        CONF = cfg.CONF
        CONF.register_opts(adiodc.ADC_CONTROLLER_EXT_MANAGER_OPTS, group='sdnc_adiod')
        self.conf = CONF

    def testKeyValue(self):
        self.key = self.conf._groups.keys().pop(0)
        self.assertEqual("sdnc_adiod", self.key)

if __name__ == '__main__':
    unittest.main()
