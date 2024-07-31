import unittest

from db_manager import DataBaseManager


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # Set up an in-memory database for testing
        self.db_manager = DataBaseManager(":memory:")

    def tearDown(self):
        """Clean up any resources after each test."""
        del self.db_manager
