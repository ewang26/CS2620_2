import socket
import threading
from typing import Any, List, Dict
from ..common.config import ConnectionSettings
from ..common.protocol.protocol import Protocol, ProtocolMessage, MessageType
from ..common.protocol.custom_protocol import CustomProtocol
from ..common.protocol.json_protocol import JSONProtocol
from .gui import ChatGUI

class ChatClient:
    def __init__(self, config: ConnectionSettings = ConnectionSettings()):
        self.host = config.host
        self.port = config.port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_send_lock = threading.Lock()
        self.protocol: Protocol = CustomProtocol() if config.use_custom_protocol else JSONProtocol()

        self.gui = ChatGUI(
            on_login=self.login,
            on_logout=self.logout,
            on_create_account=self.create_account,
            on_send_message=self.send_message,
            on_list_accounts=self.list_accounts,
            on_delete_messages=self.delete_messages,
            on_delete_account=self.delete_account,
            on_view_history=self.get_read_messages,
            on_pop_messages=self.pop_unread_messages
        )

    def connect(self) -> bool:
        """Connect to the server."""
        try:
            self.socket.connect((self.host, self.port))
            # Start receiving thread
            thread = threading.Thread(target=self._receive_messages)
            thread.daemon = True
            thread.start()
            return True
        except Exception as e:
            self.gui.display_message(f"Connection failed: {e}")
            return False

    def start(self):
        """Start the client."""
        if self.connect():
            self.gui.start()

    def create_account(self, username: str, password: str):
        """Send create account request."""
        message = (self.protocol.message_class(MessageType.CREATE_ACCOUNT))(name=username, password=password)
        self._send(message)

    def login(self, username: str, password: str):
        """Send login request."""
        message = (self.protocol.message_class(MessageType.LOGIN))(name=username, password=password)
        self._send(message)

    def logout(self):
        """Send logout request."""
        self._send((self.protocol.message_class(MessageType.LOGOUT))())

    def list_accounts(self, pattern: str, offset: int, limit: int):
        """Send list accounts request."""
        message = (self.protocol.message_class(MessageType.LIST_USERS))(pattern=pattern, offset=offset, limit=limit)
        self._send(message)

    def send_message(self, recipient_username: str, content: str):
        """Send a message to another user using their username."""
        message = (self.protocol.message_class(MessageType.SEND_MESSAGE))(
            receiver=recipient_username,  # username instead of ID
            content=content
        )
        self._send(message)

    def pop_unread_messages(self, count: int):
        """Pop unread messages."""
        message = (self.protocol.message_class(MessageType.POP_UNREAD_MESSAGES))(num_messages=count)
        self._send(message)

    def get_read_messages(self, offset: int, limit: int):
        """Get read messages."""
        message = (self.protocol.message_class(MessageType.GET_READ_MESSAGES))(offset=offset, num_messages=limit)
        self._send(message)

    def delete_messages(self, message_ids: List[int]):
        """Delete messages."""
        message = (self.protocol.message_class(MessageType.DELETE_MESSAGES))(message_ids=message_ids)
        self._send(message)

    def delete_account(self):
        """Delete account."""
        message = (self.protocol.message_class(MessageType.DELETE_ACCOUNT))()
        self._send(message)

    def _send(self, message: ProtocolMessage):
        """Send a message to the server."""
        try:
            with self.socket_send_lock:
                self.socket.send(message.pack_server())
        except Exception as e:
            self.gui.display_message(f"Failed to send message: {e}")

    def _receive_messages(self):
        """Receive messages from the server."""
        while True:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break

                message_type = self.protocol.get_message_type(data)
                print(f"Received message: {message_type}, {data}")
                ret = self.protocol.message_class(message_type).unpack_client(data)
                self._handle_response(message_type, ret)
            except Exception as e:
                self.gui.display_message(f"Connection error: {e}")
                break

        self.socket.close()

    def _handle_response(self, msg_type: MessageType, response: Any):
        """Handle server responses."""

        if msg_type == MessageType.CREATE_ACCOUNT:
            if response is not None:
                self.gui.display_message(response)
            else:
                self.gui.display_message("Account created successfully, please log in")

        elif msg_type == MessageType.LOGIN:
            if response is not None:
                self.gui.display_message(response)
            else:
                self.gui.show_main_widgets()
                self._send((self.protocol.message_class(MessageType.GET_NUMBER_OF_UNREAD_MESSAGES))())

        elif msg_type == MessageType.LIST_USERS:
            self.gui.display_users(response)

        elif msg_type == MessageType.GET_USER_FROM_ID:
            pass

        elif msg_type == MessageType.GET_NUMBER_OF_UNREAD_MESSAGES:
            self.gui.update_unread_count(response)

        elif msg_type == MessageType.POP_UNREAD_MESSAGES:
            self.gui.display_messages(response)
            self._send((self.protocol.message_class(MessageType.GET_NUMBER_OF_UNREAD_MESSAGES))())

        elif msg_type == MessageType.GET_READ_MESSAGES:
            self.gui.display_messages(response)

        elif msg_type == MessageType.RECEIVED_MESSAGE:
            msg = response.new_message
            self.gui.display_message(f"New message from {msg.sender}")
            self.gui.display_messages([msg])
