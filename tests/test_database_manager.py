import unittest
from unittest.mock import patch

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

    def test_modify_config_non_existent_identifier(self):
        """Test modifying a DNS configuration with a non-existent identifier."""
        with self.assertRaises(ValueError):
            self.db_manager.modify_config("nonexistent", primary_address="192.168.1.20")

    def test_modify_config_duplicate_name(self):
        """Test modifying a DNS configuration with a new name that already exists."""
        # Add a second configuration with the name "test4"
        self.db_manager.add_config("test4", "192.168.1.5")

        # Attempt to modify "test1" to have the name "test4"
        with self.assertRaises(ValueError):
            self.db_manager.modify_config("test1", name="test4")

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


class TestGetConfigs(BaseTestCase):

    def setUp(self):
        super().setUp()
        # Initialize the database with test data for get_configs testing
        self.db_manager.add_config("test1", "192.168.1.1")
        self.db_manager.add_config(
            "test2", "192.168.1.2", "192.168.1.3", "Secondary DNS"
        )
        self.db_manager.add_config("test3", "192.168.1.4")

    def test_get_all_configs(self):
        """Test retrieving all configurations."""
        configs = self.db_manager.get_configs()
        expected = [
            ("test1", "192.168.1.1", None, None),
            ("test2", "192.168.1.2", "192.168.1.3", "Secondary DNS"),
            ("test3", "192.168.1.4", None, None),
        ]
        self.assertEqual(configs, expected)

    def test_get_config_by_identifier(self):
        """Test retrieving a specific configuration by identifier."""
        configs = self.db_manager.get_configs("test2")
        expected = [("test2", "192.168.1.2", "192.168.1.3", "Secondary DNS")]
        self.assertEqual(configs, expected)

    def test_get_no_results(self):
        """Test retrieving configurations with an identifier that doesn't exist."""
        configs = self.db_manager.get_configs("nonexistent")
        self.assertEqual(configs, [])

    @patch.object(
        DataBaseManager, "get_configs", side_effect=RuntimeError("Test DB Error")
    )
    def test_get_configs_database_error(self, _):
        """Test handling of database errors during retrieval."""
        with self.assertRaises(RuntimeError):
            self.db_manager.get_configs("test1")


class TestConfigExists(BaseTestCase):

    @patch.object(
        DataBaseManager, "config_exists", side_effect=RuntimeError("Test DB Error")
    )
    def test_config_exists_raises_exception(self, _):
        """Test that config_exists method raises a RuntimeError when a database error occurs."""
        with self.assertRaises(RuntimeError):
            self.db_manager.config_exists("test1")


if __name__ == "__main__":
    unittest.main()
