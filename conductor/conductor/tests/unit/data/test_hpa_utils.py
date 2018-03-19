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

from conductor.data import hpa_utils


class TestHPAUtils(unittest.TestCase):

    def test_match_all_operator(self):
        self.assertEqual(False, hpa_utils.match_all_operator(None, None))
        self.assertEqual(False, hpa_utils.match_all_operator([], None))
        self.assertEqual(False, hpa_utils.match_all_operator(None, []))
        self.assertEqual(False, hpa_utils.match_all_operator([], []))

        big_list = ['aes', 'sse', 'avx', 'smt']
        small_list = ['avx', 'aes']
        self.assertEqual(True,
                         hpa_utils.match_all_operator(big_list, small_list))

        big_list = ['aes', 'sse', 'avx', 'smt']
        small_list = ['avx', 'pcmulqdq']
        self.assertEqual(False,
                         hpa_utils.match_all_operator(big_list, small_list))

        big_list = ['aes', 'sse', 'avx', 'smt']
        small_list = ['aes', 'sse', 'avx', 'smt']
        self.assertEqual(True,
                         hpa_utils.match_all_operator(big_list, small_list))

        big_list = ['aes', 'sse', 'avx', 'smt']
        small_list = ['smt']
        self.assertEqual(True,
                         hpa_utils.match_all_operator(big_list, small_list))

        big_list = ['aes']
        small_list = ['smt']
        self.assertEqual(False,
                         hpa_utils.match_all_operator(big_list, small_list))

        # check the order of elements
        big_list = ['aes', 'sse', 'avx', 'smt']
        small_list = sorted(big_list)
        self.assertEqual(True,
                         hpa_utils.match_all_operator(big_list, small_list))


if __name__ == "__main__":
    unittest.main()
