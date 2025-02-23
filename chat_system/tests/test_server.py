import unittest
import grpc
from concurrent import futures
import time
from threading import Thread

from ..common.config import ConnectionSettings
from ..server.server import ChatServer, ChatServicer
from ..proto import chat_pb2, chat_pb2_grpc

class MockContext:
    def __init__(self):
        self.peer_value = "test_peer"
    
    def peer(self):
        return self.peer_value

class TestServer(unittest.TestCase):
    def setUp(self):
        """Create a new server instance for each test."""
        self.server = ChatServer(ConnectionSettings())
        self.servicer = ChatServicer(self.server)
        self.context = MockContext()

    def test_create_account(self):
        """Test account creation."""
        request = chat_pb2.CreateAccountRequest(
            username="test",
            password="password"
        )
        response = self.servicer.CreateAccount(request, self.context)
        self.assertFalse(response.HasField('error'))

        # Test duplicate account
        response = self.servicer.CreateAccount(request, self.context)
        self.assertTrue(response.HasField('error'))

    def test_login_logout(self):
        """Test login and logout functionality."""
        # Create account first
        create_request = chat_pb2.CreateAccountRequest(
            username="test",
            password="password"
        )
        self.servicer.CreateAccount(create_request, self.context)

        # Test successful login
        login_request = chat_pb2.LoginRequest(
            username="test",
            password="password"
        )
        response = self.servicer.Login(login_request, self.context)
        self.assertFalse(response.HasField('error'))
        self.assertEqual(self.server.client_sessions[self.context.peer()], "test")

        # Test logout
        logout_request = chat_pb2.LogoutRequest()
        self.servicer.Logout(logout_request, self.context)
        self.assertIsNone(self.server.client_sessions[self.context.peer()])

    # Add more tests for other gRPC methods...
