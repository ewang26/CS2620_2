import unittest
from unittest.mock import MagicMock

from ..common.config import ConnectionSettings
from ..server.server import ChatServer
from ..common.protocol.json_protocol import *

class MockSocket:
    def __init__(self):
        self.send = MagicMock()

def ret_string(message_type, response):
    return f'{{"t": {message_type}, "r": {response}}}'.encode('utf-8')

class TestServer(unittest.TestCase):
    def setUp(self):
        self.server = ChatServer(ConnectionSettings(use_custom_protocol=False))
        self.socket = MockSocket()

    def send_message(self, message, socket=None):
        self.server.process_message(self.socket if socket is None else socket, message)

    def test_create_account(self):
        """Test account creation."""
        self.send_message(JSON_CreateAccountMessage("test", "password"))
        self.socket.send.assert_called_with(ret_string(MessageType.CREATE_ACCOUNT, 'null'))

        self.send_message(JSON_CreateAccountMessage("test", "different"))
        self.socket.send.assert_called_with(ret_string(MessageType.CREATE_ACCOUNT, '"Username already taken"'))

    def test_login(self):
        """Test login functionality."""
        self.send_message(JSON_LoginMessage("test", "password"))
        self.socket.send.assert_called_with(ret_string(MessageType.LOGIN, '"Invalid username or password"'))

        self.send_message(JSON_CreateAccountMessage("test", "password"))

        self.send_message(JSON_LoginMessage("test", "password"))
        self.socket.send.assert_called_with(ret_string(MessageType.LOGIN, 'null'))

    def test_logout(self):
        """Test account logout."""
        self.send_message(JSON_CreateAccountMessage("test", "password"))
        self.send_message(JSON_LoginMessage("test", "password"))

        self.send_message(JSON_LogoutMessage())
        self.assertEqual(self.server.client_sessions[self.socket], -1)


    def test_list_users(self):
        """Test user listing."""
        self.send_message(JSON_CreateAccountMessage("test", "password"))
        self.send_message(JSON_CreateAccountMessage("alt", "password"))
        self.send_message(JSON_LoginMessage("test", "password"))

        # Test wildcard
        self.send_message(JSON_ListUsersMessage("*", 0, -1))
        self.socket.send.assert_called_with(ret_string(MessageType.LIST_USERS, '[[0, "test"], [1, "alt"]]'))

        # Test limit
        self.send_message(JSON_ListUsersMessage("*", 1, 1))
        self.socket.send.assert_called_with(ret_string(MessageType.LIST_USERS, '[[1, "alt"]]'))

        # Test pattern
        self.send_message(JSON_ListUsersMessage("alt", 0, -1))
        self.socket.send.assert_called_with(ret_string(MessageType.LIST_USERS, '[[1, "alt"]]'))

        # Test empty list
        self.send_message(JSON_ListUsersMessage("none", 0, -1))
        self.socket.send.assert_called_with(ret_string(MessageType.LIST_USERS, '[]'))

    def test_get_user(self):
        """Test getting user from id."""
        self.send_message(JSON_CreateAccountMessage("test", "password"))
        self.send_message(JSON_CreateAccountMessage("alt", "password"))
        self.send_message(JSON_LoginMessage("test", "password"))

        self.send_message(JSON_GetUserFromIdMessage(0))
        self.socket.send.assert_called_with(ret_string(MessageType.GET_USER_FROM_ID, '"test"'))

        self.send_message(JSON_GetUserFromIdMessage(1))
        self.socket.send.assert_called_with(ret_string(MessageType.GET_USER_FROM_ID, '"alt"'))

    def test_delete_account(self):
        """Test account deletion."""
        self.send_message(JSON_CreateAccountMessage("test", "password"))
        self.send_message(JSON_LoginMessage("test", "password"))

        self.send_message(JSON_DeleteAccountMessage())
        self.assertEqual(self.server.client_sessions[self.socket], -1)
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
        alt_socket.send.assert_called_with(f'{{"t": {MessageType.RECEIVED_MESSAGE}, "n": {{"i": 1, "s": 0, "c": "content2"}}}}'.encode('utf-8'))
        # Message should be added to the read mailbox since user is logged in
        self.assertEqual(len(self.server.account_manager.get_user(1).read_mailbox), 1)

    def test_get_number_of_unread_messages(self):
        """Test getting unread messages."""
        self.send_message(JSON_CreateAccountMessage("test", "password"))
        self.send_message(JSON_CreateAccountMessage("alt", "password"))
        self.send_message(JSON_LoginMessage("test", "password"))

        self.send_message(JSON_GetNumberOfUnreadMessagesMessage())
        self.socket.send.assert_called_with(ret_string(MessageType.GET_NUMBER_OF_UNREAD_MESSAGES, '0'))

        self.send_message(JSON_SendMessageMessage(1, "content"))
        self.send_message(JSON_SendMessageMessage(1, "content2"))

        alt_socket = MockSocket()
        self.send_message(JSON_LoginMessage("alt", "password"), alt_socket)
        self.send_message(JSON_GetNumberOfUnreadMessagesMessage(), alt_socket)
        alt_socket.send.assert_called_with(ret_string(MessageType.GET_NUMBER_OF_UNREAD_MESSAGES, '2'))

    def test_pop_unread_messages(self):
        """Test popping unread messages."""
        self.send_message(JSON_CreateAccountMessage("test", "password"))
        self.send_message(JSON_CreateAccountMessage("alt", "password"))
        self.send_message(JSON_LoginMessage("test", "password"))

        # Test popping when there are no messages
        self.send_message(JSON_PopUnreadMessagesMessage(10))
        self.socket.send.assert_called_with(ret_string(MessageType.POP_UNREAD_MESSAGES, '[]'))

        self.send_message(JSON_SendMessageMessage(1, "content"))
        self.send_message(JSON_SendMessageMessage(1, "content2"))
        self.send_message(JSON_SendMessageMessage(1, "content3"))

        # Test popping 1 or all messages
        alt_socket = MockSocket()
        self.send_message(JSON_LoginMessage("alt", "password"), alt_socket)
        self.send_message(JSON_PopUnreadMessagesMessage(1), alt_socket)
        alt_socket.send.assert_called_with(ret_string(MessageType.POP_UNREAD_MESSAGES, '[{"i": 0, "s": 0, "c": "content"}]'))
        self.send_message(JSON_PopUnreadMessagesMessage(-1), alt_socket)
        alt_socket.send.assert_called_with(ret_string(MessageType.POP_UNREAD_MESSAGES, '[{"i": 1, "s": 0, "c": "content2"}, {"i": 2, "s": 0, "c": "content3"}]'))

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
        alt_socket.send.assert_called_with(ret_string(MessageType.GET_READ_MESSAGES, '[{"i": 2, "s": 0, "c": "content3"}]'))

        self.send_message(JSON_GetReadMessagesMessage(1, -1), alt_socket)
        alt_socket.send.assert_called_with(ret_string(MessageType.GET_READ_MESSAGES, '[{"i": 0, "s": 0, "c": "content"}, {"i": 1, "s": 0, "c": "content2"}]'))

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
