import json
import selectors
import signal
import socket
from typing import Dict, Optional

from chat_system.common.config import ConnectionSettings
from .account_manager import AccountManager
from ..common.protocol.custom_protocol import CustomProtocol
from ..common.protocol.json_protocol import JSONProtocol
from ..common.protocol.protocol import *
from ..common.user import Message


class ChatServer:
    def __init__(self, config: ConnectionSettings = ConnectionSettings()):
        self.host = config.host
        self.port = config.port
        self.protocol: Protocol = CustomProtocol() if config.use_custom_protocol else JSONProtocol()
        self.account_manager = AccountManager()
        self.client_sessions: Dict[socket.socket, Optional[str]] = {}  # socket -> username
        self.next_message_id = 0

        self.running = True
        self.server_path = config.server_data_path
        self.selector = selectors.DefaultSelector()

        # Register signal handlers to save state when shutting down
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def save_state(self):
        """Save the server state to a file."""
        with open(self.server_path, "w") as f:
            state = {
                "account_manager": self.account_manager.get_state(),
                "next_message_id": self.next_message_id
            }
            f.write(json.dumps(state))

    def load_state(self):
        """Load the server state from a file."""
        try:
            with open(self.server_path) as f:
                state = json.load(f)
                self.account_manager.load_state(state["account_manager"])
                self.next_message_id = state["next_message_id"]
        except FileNotFoundError:
            print("No server state found, starting fresh")

    def start(self):
        """Start the chat server."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen()
        server.setblocking(False)

        self.selector.register(server, selectors.EVENT_READ, self.accept_connection)

        print(f"Server started on {self.host}:{self.port}")

        while self.running:
            events = self.selector.select(timeout=1)
            for key, mask in events:
                callback = key.data
                callback(key.fileobj)

        print(f"Saving server state to {self.server_path}")
        self.save_state()

    def handle_shutdown(self, signum, frame):
        print("Server shutting down...")
        self.running = False

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

            # We may receive multiple messages at once
            offset = 0
            while offset < len(data):
                dm = data[offset:]
                message_type = self.protocol.get_message_type(dm)
                message, message_len = self.protocol.message_class(message_type).unpack_server(dm)
                print(f"Received message of type {message_type}, {dm} -> {message}")
                self.process_message(sock, message)
                offset += message_len

        except Exception as e:
            print(f"Error handling client: {e}")
            self.close_connection(sock)

    def process_message(self, sock: socket.socket, message: ProtocolMessage):
        """Process a received message."""
        if message.type == MessageType.CREATE_ACCOUNT:
            username, password = message.name, message.password
            success = self.account_manager.create_account(username, password)
            response = message.pack_client(success)
            sock.send(response)

        elif message.type == MessageType.LOGIN:
            username, password = message.name, message.password
            user = self.account_manager.login(username, password)
            if user:
                self.client_sessions[sock] = user.name
                response = message.pack_client(None)
            else:
                response = message.pack_client("Invalid username or password")
            sock.send(response)

        elif self.client_sessions[sock] == -1:
            print("Message received before login:", message.type)

        elif message.type == MessageType.LOGOUT:
            self.client_sessions[sock] = None

        elif message.type == MessageType.LIST_USERS:
            pattern = message.pattern
            accounts = self.account_manager.list_accounts(pattern)
            # Cap to valid range
            offset = max(0, message.offset)
            if message.limit == -1:
                accounts = accounts[offset:]
            else:
                limit = min(len(accounts), offset + message.limit)
                accounts = accounts[offset:limit]
            response = message.pack_client(accounts)
            sock.send(response)

        elif message.type == MessageType.DELETE_ACCOUNT:
            self.account_manager.delete_account(self.client_sessions[sock])
            self.client_sessions[sock] = None

        elif message.type == MessageType.SEND_MESSAGE:
            recipient, content = message.receiver, message.content
            # Make sure the recipient exists
            if self.account_manager.get_user(recipient) is None:
                return

            sender_id = self.client_sessions[sock]
            message = Message(self.next_message_id, sender_id, content)
            self.next_message_id += 1

            # See if any clients are connected as the recipient
            read = False
            for client_sock, user_id in self.client_sessions.items():
                if user_id == recipient:
                    response = (self.protocol.message_class(MessageType.RECEIVED_MESSAGE))(message)
                    client_sock.send(response.pack_client(None))
                    read = True
            if read:
                self.account_manager.get_user(recipient).add_read_message(message)
            else:
                self.account_manager.get_user(recipient).add_message(message)

        elif message.type == MessageType.GET_NUMBER_OF_UNREAD_MESSAGES:
            user = self.account_manager.get_user(self.client_sessions[sock])
            response = message.pack_client(user.get_number_of_unread_messages())
            sock.send(response)

        elif message.type == MessageType.GET_NUMBER_OF_READ_MESSAGES:
            user = self.account_manager.get_user(self.client_sessions[sock])
            response = message.pack_client(user.get_number_of_read_messages())
            sock.send(response)

        elif message.type == MessageType.POP_UNREAD_MESSAGES:
            user = self.account_manager.get_user(self.client_sessions[sock])
            messages = user.pop_unread_messages(message.num_messages)
            response = message.pack_client(messages)
            sock.send(response)

        elif message.type == MessageType.GET_READ_MESSAGES:
            user = self.account_manager.get_user(self.client_sessions[sock])
            messages = user.get_read_messages(message.offset, message.num_messages)
            response = message.pack_client(messages)
            sock.send(response)

        elif message.type == MessageType.DELETE_MESSAGES:
            user = self.account_manager.get_user(self.client_sessions[sock])
            user.delete_messages(message.message_ids)

        else:
            print(f"Unknown message type: {message.type}")

    def close_connection(self, sock: socket.socket):
        """Close a client connection."""
        if sock in self.client_sessions:
            self.client_sessions.pop(sock)
        self.selector.unregister(sock)
        sock.close()
