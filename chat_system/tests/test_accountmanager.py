import unittest
from ..server.account_manager import AccountManager

class TestAccountManager(unittest.TestCase):
    def setUp(self):
        self.account_manager = AccountManager()

    def test_create_account(self):
        """Test account creation."""
        # Test successful creation
        self.assertIsNone(self.account_manager.create_account("test", "password"))

        # Test duplicate username
        self.assertIsNotNone(self.account_manager.create_account("test", "different"))

    def test_unique_ids(self):
        """Test that user ids are unique."""
        ids = set()
        for i in range(10):
            self.account_manager.create_account(str(i), "password")
            user_id = self.account_manager.login(str(i), "password").id
            self.assertNotIn(user_id, ids)
            ids.add(user_id)

    def test_login(self):
        """Test login functionality."""
        username = "test"
        password = "password"

        # Create account first
        self.account_manager.create_account(username, password)

        # Test successful login
        self.assertIsNotNone(self.account_manager.login(username, password))

        # Test wrong password
        self.assertIsNone(self.account_manager.login(username, "wrong"))

        # Test non-existent user
        self.assertIsNone(self.account_manager.login("nonexistent", password))

    def test_list_accounts(self):
        """Test account listing with patterns."""
        # Create test accounts
        accounts = ["test1", "test2", "other1", "other2"]
        for acc in accounts:
            self.account_manager.create_account(acc, "password")

        # Test listing all accounts
        users = self.account_manager.list_accounts("*")
        self.assertEqual(set([user.name for user in users]), set(accounts))

        # Test pattern matching
        test_accounts = self.account_manager.list_accounts("test*")
        self.assertEqual(set([acc.name for acc in test_accounts]), {"test1", "test2"})

