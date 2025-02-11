import unittest
from ..common.protocol.custom_protocol import (
    CustomProtocol, MessageType, 
    Custom_CreateAccountMessage, Custom_LoginMessage,
    Custom_ListUsersMessage
)

class TestCustomProtocol(unittest.TestCase):
    def setUp(self):
        self.protocol = CustomProtocol()

    def test_create_account(self):
        """Test creating account message."""
        username = "testuser"
        password = "testpass"
        
        # Create and pack message
        message = Custom_CreateAccountMessage(username, password)
        packed = message.pack_server()
        
        # Unpack and verify
        unpacked = Custom_CreateAccountMessage.unpack_server(packed)
        self.assertEqual(unpacked.name, username)
        self.assertEqual(unpacked.password, password)
        
        # Test error response
        error_msg = "Username taken"
        packed_response = message.pack_client(error_msg)
        unpacked_response = Custom_CreateAccountMessage.unpack_client(packed_response)
        self.assertEqual(unpacked_response, error_msg)

    def test_login(self):
        """Test login message."""
        username = "testuser"
        password = "testpass"
        
        # Create and pack message
        message = Custom_LoginMessage(username, password)
        packed = message.pack_server()
        
        # Unpack and verify
        unpacked = Custom_LoginMessage.unpack_server(packed)
        self.assertEqual(unpacked.name, username)
        self.assertEqual(unpacked.password, password)

    def test_list_users(self):
        """Test list users message."""
        pattern = "test*"
        offset = 0
        limit = 10
        
        # Create and pack message
        message = Custom_ListUsersMessage(pattern, offset, limit)
        packed = message.pack_server()
        
        # Unpack and verify
        unpacked = Custom_ListUsersMessage.unpack_server(packed)
        self.assertEqual(unpacked.pattern, pattern)
        self.assertEqual(unpacked.offset, offset)
        self.assertEqual(unpacked.limit, limit)
        
        # Test response with user list
        users = ["user1", "user2", "user3"]
        packed_response = message.pack_client(users)
        unpacked_response = Custom_ListUsersMessage.unpack_client(packed_response)
        self.assertEqual(unpacked_response, users) 