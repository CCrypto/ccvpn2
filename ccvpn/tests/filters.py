from ccvpn import filters
from ccvpn.tests import BaseTest


class TestFilters(BaseTest):
    def test(self):
        self.assertIsInstance(filters.check('True'), str)
        self.assertIsInstance(filters.check('False'), str)

