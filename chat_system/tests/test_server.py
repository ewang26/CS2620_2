import unittest
from unittest.mock import MagicMock
from ..server.server import ChatServer
from ..common.protocol.json_protocol import *

class MockSocket:
    def __init__(self):
        self.send = MagicMock()

class TestServer(unittest.TestCase):
    def setUp(self):
        self.server = ChatServer(use_custom_protocol=False)
        self.socket = MockSocket()

        self.server.close_connection = MagicMock()

    def send_message(self, message, socket=None):
        self.server.process_message(self.socket if socket is None else socket, message)

    def test_create_account(self):
        """Test account creation."""
        self.send_message(JSON_CreateAccountMessage("test", "password"))
        self.socket.send.assert_called_with('{"r": null}'.encode('utf-8'))

        self.send_message(JSON_CreateAccountMessage("test", "different"))
        self.socket.send.assert_called_with('{"r": "Username already taken"}'.encode('utf-8'))

    def test_login(self):
        """Test login functionality."""
        self.send_message(JSON_LoginMessage("test", "password"))
        self.socket.send.assert_called_with('{"r": "Invalid username or password"}'.encode('utf-8'))

        self.send_message(JSON_CreateAccountMessage("test", "password"))

        self.send_message(JSON_LoginMessage("test", "password"))
        self.socket.send.assert_called_with('{"r": null}'.encode('utf-8'))

    def test_list_users(self):
        """Test user listing."""
        self.send_message(JSON_CreateAccountMessage("test", "password"))
        self.send_message(JSON_CreateAccountMessage("alt", "password"))
        self.send_message(JSON_LoginMessage("test", "password"))

        # Test wildcard
        self.send_message(JSON_ListUsersMessage("*", 0, -1))
        self.socket.send.assert_called_with('{"r": [[0, "test"], [1, "alt"]]}'.encode('utf-8'))

        # Test limit
        self.send_message(JSON_ListUsersMessage("*", 1, 1))
        self.socket.send.assert_called_with('{"r": [[1, "alt"]]}'.encode('utf-8'))

        # Test pattern
        self.send_message(JSON_ListUsersMessage("alt", 0, -1))
        self.socket.send.assert_called_with('{"r": [[1, "alt"]]}'.encode('utf-8'))

        # Test empty list
        self.send_message(JSON_ListUsersMessage("none", 0, -1))
        self.socket.send.assert_called_with('{"r": []}'.encode('utf-8'))

    def test_get_user(self):
        """Test getting user from id."""
        self.send_message(JSON_CreateAccountMessage("test", "password"))
        self.send_message(JSON_CreateAccountMessage("alt", "password"))
        self.send_message(JSON_LoginMessage("test", "password"))

        self.send_message(JSON_GetUserFromIdMessage(0))
        self.socket.send.assert_called_with('{"r": "test"}'.encode('utf-8'))

        self.send_message(JSON_GetUserFromIdMessage(1))
        self.socket.send.assert_called_with('{"r": "alt"}'.encode('utf-8'))

    def test_delete_account(self):
        """Test account deletion."""
        self.send_message(JSON_CreateAccountMessage("test", "password"))
        self.send_message(JSON_LoginMessage("test", "password"))

        self.send_message(JSON_DeleteAccountMessage())
        self.server.close_connection.assert_called_with(self.socket)
        self.assertEqual(len(self.server.account_manager.accounts), 0)

    def test_send_message(self):
        """Test sending a message."""
        self.send_message(JSON_CreateAccountMessage("test", "password"))
        self.send_message(JSON_CreateAccountMessage("alt", "password"))
        self.send_message(JSON_LoginMessage("test", "password"))

        # Check that message is added to recipient's queue
        self.send_message(JSON_SendMessageMessage(1, "content"))
        mq = self.server.account_manager.get_user(1).message_queue
        self.assertEqual(len(mq), 1)
        self.assertEqual(mq[0].sender, 0)
        self.assertEqual(mq[0].content, "content")

        # Test sending to logged-in user
        alt_socket = MockSocket()
        self.send_message(JSON_LoginMessage("alt", "password"), alt_socket)

        self.send_message(JSON_SendMessageMessage(1, "content2"))
        alt_socket.send.assert_called_with('{"t": 7, "n": {"i": 1, "s": 0, "c": "content2"}}'.encode('utf-8'))

    def test_get_number_of_unread_messages(self):
        """Test getting unread messages."""
        self.send_message(JSON_CreateAccountMessage("test", "password"))
        self.send_message(JSON_CreateAccountMessage("alt", "password"))
        self.send_message(JSON_LoginMessage("test", "password"))

        self.send_message(JSON_GetNumberOfUnreadMessagesMessage())
        self.socket.send.assert_called_with('{"r": 0}'.encode('utf-8'))

        self.send_message(JSON_SendMessageMessage(1, "content"))
        self.send_message(JSON_SendMessageMessage(1, "content2"))

        alt_socket = MockSocket()
        self.send_message(JSON_LoginMessage("alt", "password"), alt_socket)
        self.send_message(JSON_GetNumberOfUnreadMessagesMessage(), alt_socket)
        alt_socket.send.assert_called_with('{"r": 2}'.encode('utf-8'))

    def test_pop_unread_messages(self):
        """Test popping unread messages."""
        self.send_message(JSON_CreateAccountMessage("test", "password"))
        self.send_message(JSON_CreateAccountMessage("alt", "password"))
        self.send_message(JSON_LoginMessage("test", "password"))

        # Test popping when there are no messages
        self.send_message(JSON_PopUnreadMessagesMessage(1))
        self.socket.send.assert_called_with('{"r": []}'.encode('utf-8'))

        self.send_message(JSON_SendMessageMessage(1, "content"))
        self.send_message(JSON_SendMessageMessage(1, "content2"))
        self.send_message(JSON_SendMessageMessage(1, "content3"))

        # Test popping 1 or all messages
        alt_socket = MockSocket()
        self.send_message(JSON_LoginMessage("alt", "password"), alt_socket)
        self.send_message(JSON_PopUnreadMessagesMessage(1), alt_socket)
        alt_socket.send.assert_called_with('{"r": [{"i": 0, "s": 0, "c": "content"}]}'.encode('utf-8'))
        self.send_message(JSON_PopUnreadMessagesMessage(-1), alt_socket)
        alt_socket.send.assert_called_with('{"r": [{"i": 1, "s": 0, "c": "content2"}, {"i": 2, "s": 0, "c": "content3"}]}'.encode('utf-8'))

        # Make sure messages are removed from queue
        self.assertEqual(len(self.server.account_manager.get_user(1).message_queue), 0)

    def test_get_read_messages(self):
        """Test getting read messages."""
        self.send_message(JSON_CreateAccountMessage("test", "password"))
        self.send_message(JSON_CreateAccountMessage("alt", "password"))
        self.send_message(JSON_LoginMessage("test", "password"))

        self.send_message(JSON_SendMessageMessage(1, "content"))
        self.send_message(JSON_SendMessageMessage(1, "content2"))
        self.send_message(JSON_SendMessageMessage(1, "content3"))

        alt_socket = MockSocket()
        self.send_message(JSON_LoginMessage("alt", "password"), alt_socket)
        self.send_message(JSON_PopUnreadMessagesMessage(-1), alt_socket)

        self.send_message(JSON_GetReadMessagesMessage(0, 1), alt_socket)
        alt_socket.send.assert_called_with('{"r": [{"i": 2, "s": 0, "c": "content3"}]}'.encode('utf-8'))

        self.send_message(JSON_GetReadMessagesMessage(1, -1), alt_socket)
        alt_socket.send.assert_called_with('{"r": [{"i": 0, "s": 0, "c": "content"}, {"i": 1, "s": 0, "c": "content2"}]}'.encode('utf-8'))

    def test_delete_messages(self):
        """Test deleting messages."""
        self.send_message(JSON_CreateAccountMessage("test", "password"))
        self.send_message(JSON_CreateAccountMessage("alt", "password"))
        self.send_message(JSON_LoginMessage("test", "password"))

        self.send_message(JSON_SendMessageMessage(1, "content"))
        self.send_message(JSON_SendMessageMessage(1, "content2"))
        self.send_message(JSON_SendMessageMessage(1, "content3"))

        alt_socket = MockSocket()
        self.send_message(JSON_LoginMessage("alt", "password"), alt_socket)
        self.send_message(JSON_PopUnreadMessagesMessage(-1), alt_socket)

        self.send_message(JSON_DeleteMessagesMessage([0, 2]), alt_socket)
        self.assertEqual(len(self.server.account_manager.get_user(1).read_mailbox), 1)
        self.assertEqual(self.server.account_manager.get_user(1).read_mailbox[0].id, 1)
