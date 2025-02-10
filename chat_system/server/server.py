import sys
import socket
import selectors

from chat_system.common.config import DEFAULT_HOST, DEFAULT_PORT
from ..common.protocol.custom_protocol import CustomProtocol
from ..common.protocol.json_protocol import JSONProtocol
from ..common.protocol.protocol import *
from .account_manager import AccountManager
from ..common.user import Message

class ChatServer:
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, use_custom_protocol = True):
        self.host = host
        self.port = port
        self.protocol: Protocol = CustomProtocol() if use_custom_protocol else JSONProtocol()
        self.selector = selectors.DefaultSelector()
        self.account_manager = AccountManager()
        self.client_sessions: Dict[socket.socket, int] = {}  # socket -> user id
        self.next_message_id = 0

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
            events = self.selector.select(timeout=1)
            for key, mask in events:
                callback = key.data
                callback(key.fileobj)

    def accept_connection(self, sock: socket.socket):
        """Accept a new client connection."""
        client, addr = sock.accept()
        client.setblocking(False)
        self.selector.register(client, selectors.EVENT_READ, self.handle_client)
        self.client_sessions[client] = -1
        print(f"New connection from {addr}")

    def handle_client(self, sock: socket.socket):
        """Handle client messages."""
        try:
            data = sock.recv(4096)
            if not data:
                self.close_connection(sock)
                return

            message_type, message = self.protocol.parse_message(data)
            self.process_message(sock, message)

        except Exception as e:
            print(f"Error handling client: {e}")
            self.close_connection(sock)

    def process_message(self, sock: socket.socket, message: ProtocolMessage):
        """Process a received message."""
        if message.type == MessageType.CREATE_ACCOUNT:
            username, password = message.name, message.password
            success = self.account_manager.create_account(username, password)
            response = message.pack_return(success)
            sock.send(response)

        elif message.type == MessageType.LOGIN:
            username, password = message.name, message.password
            user = self.account_manager.login(username, password)
            if user:
                self.client_sessions[sock] = user.id
                response = message.pack_return(None)
            else:
                response = message.pack_return("Invalid username or password")
            sock.send(response)

        elif self.client_sessions[sock] == -1:
            print("Message received before login:", message.type)

        elif message.type == MessageType.LIST_USERS:
            pattern = message.pattern
            accounts = self.account_manager.list_accounts(pattern)
            if message.limit == -1:
                accounts = accounts[message.offset:]
            else:
                accounts = accounts[message.offset:message.offset+message.limit]
            response = message.pack_return(accounts)
            sock.send(response)

        elif message.type == MessageType.GET_USER_FROM_ID:
            user = self.account_manager.get_user(message.user_id)
            response = message.pack_return(user.name)
            sock.send(response)

        elif message.type == MessageType.DELETE_ACCOUNT:
            self.account_manager.delete_account(self.client_sessions[sock])
            self.close_connection(sock)

        elif message.type == MessageType.SEND_MESSAGE:
            recipient, content = message.receiver, message.content
            sender_id = self.client_sessions[sock]
            message = Message(self.next_message_id, sender_id, content)
            self.next_message_id += 1

            # See if any clients are connected as the recipient
            read = False
            for client_sock, user_id in self.client_sessions.items():
                if user_id == recipient:
                    response = (self.protocol.message_class(MessageType.RECEIVED_MESSAGE))(message)
                    client_sock.send(response.pack())
                    read = True
            if not read:
                self.account_manager.get_user(recipient).add_message(message)

        elif message.type == MessageType.GET_NUMBER_OF_UNREAD_MESSAGES:
            user = self.account_manager.get_user(self.client_sessions[sock])
            response = message.pack_return(user.get_number_of_unread_messages())
            sock.send(response)

        elif message.type == MessageType.POP_UNREAD_MESSAGES:
            user = self.account_manager.get_user(self.client_sessions[sock])
            messages = user.pop_unread_messages(message.num_messages)
            response = message.pack_return(messages)
            sock.send(response)

        elif message.type == MessageType.GET_READ_MESSAGES:
            user = self.account_manager.get_user(self.client_sessions[sock])
            messages = user.get_read_messages(message.offset, message.num_messages)
            response = message.pack_return(messages)
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
