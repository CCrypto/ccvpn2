import unittest
from pyramid import testing
from ccvpn import filters


class TestFilters(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test(self):
        self.assertIsInstance(filters.check('True'), str)
        self.assertIsInstance(filters.check('False'), str)

