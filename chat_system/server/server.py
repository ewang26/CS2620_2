import socket
import selectors
import threading
from typing import Dict, Optional
from ..common.protocol.custom_protocol import Protocol, MessageType, Message
from .account_manager import AccountManager
from .message_store import MessageStore, ChatMessage
from datetime import datetime

class ChatServer:
    def __init__(self, host: str = 'localhost', port: int = 8888):
        self.host = host
        self.port = port
        self.selector = selectors.DefaultSelector()
        self.account_manager = AccountManager()
        self.message_store = MessageStore()
        self.client_sessions: Dict[socket.socket, Optional[str]] = {}  # socket -> username
        
    def start(self):
        """Start the chat server."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen()
        server.setblocking(False)
        
        self.selector.register(server, selectors.EVENT_READ, self.accept_connection)
        
        print(f"Server started on {self.host}:{self.port}")
        
        while True:
            events = self.selector.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj)
    
    def accept_connection(self, sock: socket.socket):
        """Accept a new client connection."""
        client, addr = sock.accept()
        client.setblocking(False)
        self.selector.register(client, selectors.EVENT_READ, self.handle_client)
        self.client_sessions[client] = None
        print(f"New connection from {addr}")
    
    def handle_client(self, sock: socket.socket):
        """Handle client messages."""
        try:
            data = sock.recv(4096)
            if not data:
                self.close_connection(sock)
                return
                
            message = Protocol.unpack_message(data)
            self.process_message(sock, message)
            
        except Exception as e:
            print(f"Error handling client: {e}")
            self.close_connection(sock)
    
    def process_message(self, sock: socket.socket, message: Message):
        """Process a received message."""
        if message.type == MessageType.CREATE_ACCOUNT:
            username, password = message.payload.decode().split(':')
            success = self.account_manager.create_account(username, password)
            response = Protocol.pack_message(
                MessageType.SUCCESS if success else MessageType.ERROR,
                b"Account created" if success else b"Username taken"
            )
            sock.send(response)
            
        elif message.type == MessageType.LOGIN:
            username, password = message.payload.decode().split(':')
            success = self.account_manager.login(username, password)
            if success:
                self.client_sessions[sock] = username
                unread = self.message_store.count_unread(username)
                response = Protocol.pack_message(
                    MessageType.SUCCESS,
                    f"Login successful. You have {unread} unread messages.".encode()
                )
            else:
                response = Protocol.pack_message(
                    MessageType.ERROR,
                    b"Invalid credentials"
                )
            sock.send(response)
            
        elif message.type == MessageType.LIST_ACCOUNTS:
            pattern = message.payload.decode() if message.payload else None
            accounts = self.account_manager.list_accounts(pattern)
            response = Protocol.pack_message(
                MessageType.ACCOUNT_LIST,
                ','.join(accounts).encode())
            sock.send(response)
            
        elif message.type == MessageType.SEND_MESSAGE:
            if not self.client_sessions[sock]:
                response = Protocol.pack_message(
                    MessageType.ERROR,
                    b"Not logged in")
                sock.send(response)
                return
                
            recipient, content = message.payload.decode().split(':', 1)
            chat_message = ChatMessage(
                sender=self.client_sessions[sock],
                content=content,
                timestamp=datetime.now())
            
            # Store or deliver message
            self.message_store.store_message(recipient, chat_message)
            response = Protocol.pack_message(
                MessageType.SUCCESS,
                b"Message sent"
            )
            sock.send(response)
    
    def close_connection(self, sock: socket.socket):
        """Close a client connection."""
        if sock in self.client_sessions:
            username = self.client_sessions[sock]
            if username:
                self.account_manager.logout(username)
            del self.client_sessions[sock]
        self.selector.unregister(sock)
        sock.close() 