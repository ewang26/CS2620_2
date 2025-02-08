import unittest
from unittest.mock import Mock, patch
from ..server.account_manager import AccountManager
from ..server.message_store import MessageStore, ChatMessage
from datetime import datetime

class TestAccountManager(unittest.TestCase):
    def setUp(self):
        self.account_manager = AccountManager()
    
    def test_create_account(self):
        """Test account creation."""
        # Test successful creation
        self.assertTrue(self.account_manager.create_account("test", "password"))
        
        # Test duplicate username
        self.assertFalse(self.account_manager.create_account("test", "different"))
    
    def test_login(self):
        """Test login functionality."""
        username = "test"
        password = "password"
        
        # Create account first
        self.account_manager.create_account(username, password)
        
        # Test successful login
        self.assertTrue(self.account_manager.login(username, password))
        self.assertTrue(self.account_manager.is_online(username))
        
        # Test wrong password
        self.assertFalse(self.account_manager.login(username, "wrong"))
        
        # Test non-existent user
        self.assertFalse(self.account_manager.login("nonexistent", password))
    
    def test_list_accounts(self):
        """Test account listing with patterns."""
        # Create test accounts
        accounts = ["test1", "test2", "other1", "other2"]
        for acc in accounts:
            self.account_manager.create_account(acc, "password")
        
        # Test listing all accounts
        self.assertEqual(set(self.account_manager.list_accounts()), set(accounts))
        
        # Test pattern matching
        test_accounts = self.account_manager.list_accounts("test*")
        self.assertEqual(set(test_accounts), {"test1", "test2"})

class TestMessageStore(unittest.TestCase):
    def setUp(self):
        self.message_store = MessageStore()
    
    def test_message_storage_and_retrieval(self):
        """Test message storage and retrieval."""
        recipient = "test_user"
        message = ChatMessage(
            sender="sender",
            content="Hello!",
            timestamp=datetime.now()
        )
        
        # Store message
        self.message_store.store_message(recipient, message)
        
        # Test retrieval
        messages = self.message_store.get_pending_messages(recipient)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], message)
        
        # Test message count
        self.assertEqual(self.message_store.count_unread(recipient), 1)
        
        # Test marking as delivered
        self.message_store.mark_delivered(recipient, message)
        self.assertEqual(self.message_store.count_unread(recipient), 0) 