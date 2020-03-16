from __future__ import absolute_import

import json
import unittest

from conductor.solver.optimizer.constraints.access_distance import AccessDistance
from conductor.solver.request.parser import Parser


class TestConstaintAccessDistance(unittest.TestCase, AccessDistance):

    def setUp(self):

        self.parser = Parser()
        self.parserExpected = {
                               "demands": {},
                               "locations": {},
                               "obj_func_param": {},
                               "cei": "null",
                               "region_gen": "null",
                               "region_group": {},
                               "request_id": "null",
                               "request_type": "null",
                               "objective": "null",
                               "constraints": {}
                              }
        self.test_parser_template = self.parser.parse_template()

    def test_correct_parser_attributes(self):
      a = []
      b = []

      for k in sorted(self.parserExpected):
        a.append(k)

      for key, values in sorted(vars(self.parser).items()):
        b.append(key)
      a.sort()
      b.sort()

      self.assertEqual(a, b)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()