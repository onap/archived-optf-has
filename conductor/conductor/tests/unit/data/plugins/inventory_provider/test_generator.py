#
# -------------------------------------------------------------------------
#   Copyright (C) 2020 Wipro Limited.
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
import json
from mock import patch

from conductor.data.plugins.inventory_provider.generator import Generator


class TestGenerator(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        patch.stopall()

    def test_generate_candidate(self):

        candidates_file = './conductor/tests/unit/data/plugins/inventory_provider/generated_candidates.json'
        expected_candidates = json.loads(open(candidates_file).read())

        #uuids = [candidate['candidate_id'] for candidate in expected_candidates]

        #self.patcher = patch('uuid.uuid4', side_effect=uuids)
        #self.patcher.start()

        generator = Generator()

        filtering_attributes = {'latency': {'min': 5, 'max': 20, 'steps': 1},
                                'reliability': {'values': [99.99, 99.999]}}

        generated_candidates = generator.generate_candidates('nssi', filtering_attributes,
                                                             candidate_uniqueness='true')
        #with open('/home/krishna/actual_candidates.json', 'w') as f:
        #    f.write(json.dumps(generated_candidates))

        for candidate in generated_candidates:
            self.assertIsNotNone(candidate['candidate_id'])
            del candidate['candidate_id']

        for candidate in expected_candidates:
            del candidate['candidate_id']

        self.assertCountEqual(expected_candidates, generated_candidates)

        self.assertEqual([], generator.generate_candidates('cloud', filtering_attributes,
                                                           candidate_uniqueness='true'))
