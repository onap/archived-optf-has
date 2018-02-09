import unittest

def fun(x):
    return x + 1

class SimpleIntegralIncrementTest(unittest.TestCase):
    def test(self):
        self.assertEqual(fun(3), 4)