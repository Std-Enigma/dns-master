import unittest

from db_manager import DataBaseManager


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # Set up an in-memory database for testing
        self.db_manager = DataBaseManager(":memory:")

    def tearDown(self):
        """Clean up any resources after each test."""
        del self.db_manager


class TestConfigManagement(BaseTestCase):

    def setUp(self):
        super().setUp()
        # Initialize the database with some test data
        self.db_manager.add_config("test1", "192.168.1.1")
        self.db_manager.add_config(
            "test2", "192.168.1.2", "192.168.1.3", "Secondary DNS"
        )
        self.db_manager.add_config("test3", "192.168.1.4")

    def test_add_config(self):
        """Test adding a new DNS configuration."""
        self.db_manager.add_config("test4", "192.168.1.5")
        configs = self.db_manager.get_configs("test4")
        expected = [("test4", "192.168.1.5", None, None)]
        self.assertEqual(configs, expected)

    def test_add_duplicate_config(self):
        """Test adding a duplicate DNS configuration should raise ValueError."""
        with self.assertRaises(ValueError):
            self.db_manager.add_config("test1", "192.168.1.1")

    def test_modify_config(self):
        """Test modifying an existing DNS configuration."""
        self.db_manager.modify_config(
            "test1", primary_address="192.168.1.10", description="Updated"
        )
        configs = self.db_manager.get_configs("test1")
        expected = [("test1", "192.168.1.10", None, "Updated")]
        self.assertEqual(configs, expected)

    def test_remove_config(self):
        """Test removing an existing DNS configuration."""
        self.db_manager.remove_config("test3")
        configs = self.db_manager.get_configs("test3")
        self.assertEqual(configs, [])

    def test_clear_configs(self):
        """Test clearing all DNS configurations."""
        self.db_manager.clear_configs()
        configs = self.db_manager.get_configs()
        self.assertEqual(configs, [])
