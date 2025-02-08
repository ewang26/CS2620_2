import unittest
from ..common.protocol.custom_protocol import Protocol, MessageType, Message
from ..common.protocol.json_protocol import JSONProtocol

class TestCustomProtocol(unittest.TestCase):
    def test_pack_unpack_message(self):
        """Test message packing and unpacking."""
        original_type = MessageType.CREATE_ACCOUNT
        original_payload = b"test:password123"
        
        packed = Protocol.pack_message(original_type, original_payload)
        unpacked = Protocol.unpack_message(packed)
        
        self.assertEqual(unpacked.type, original_type)
        self.assertEqual(unpacked.payload, original_payload)
    
    def test_create_account_request(self):
        """Test creating account request."""
        username = "testuser"
        password = "testpass"
        
        message = Protocol.create_account_request(username, password)
        unpacked = Protocol.unpack_message(message)
        
        self.assertEqual(unpacked.type, MessageType.CREATE_ACCOUNT)
        self.assertEqual(unpacked.payload.decode(), f"{username}:{password}")
    
    def test_login_request(self):
        """Test login request."""
        username = "testuser"
        password = "testpass"
        
        message = Protocol.login_request(username, password)
        unpacked = Protocol.unpack_message(message)
        
        self.assertEqual(unpacked.type, MessageType.LOGIN)
        self.assertEqual(unpacked.payload.decode(), f"{username}:{password}")
    
    def test_list_accounts_request(self):
        """Test list accounts request."""
        pattern = "test*"
        
        message = Protocol.list_accounts_request(pattern)
        unpacked = Protocol.unpack_message(message)
        
        self.assertEqual(unpacked.type, MessageType.LIST_ACCOUNTS)
        self.assertEqual(unpacked.payload.decode(), pattern)
        
        # Test without pattern
        message = Protocol.list_accounts_request()
        unpacked = Protocol.unpack_message(message)
        self.assertEqual(unpacked.payload, b"")

class TestJSONProtocol(unittest.TestCase):
    def test_create_message(self):
        """Test JSON message creation."""
        message = JSONProtocol.create_message(
            "create_account",
            username="test",
            password="pass"
        )
        parsed = JSONProtocol.parse_message(message)
        
        self.assertEqual(parsed["type"], "create_account")
        self.assertEqual(parsed["payload"]["username"], "test")
        self.assertEqual(parsed["payload"]["password"], "pass") 