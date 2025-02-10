import socket
import threading
import json
from typing import Optional, Dict, Any, List
from ..common.config import DEFAULT_HOST, DEFAULT_PORT
from ..common.protocol.custom_protocol import Protocol, MessageType
from .gui import ChatGUI

class ChatClient:
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logged_in = False

        self.gui = ChatGUI(
            on_login=self.login,
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
        message = {"t": "create_account", "u": username, "p": password}
        self._send(message)

    def login(self, username: str, password: str):
        """Send login request."""
        message = {"t": "login", "u": username, "p": password}
        self._send(message)

    def list_accounts(self, pattern: str, offset: int, limit: int):
        """Send list accounts request."""
        message = {"t": "list_users", "p": pattern, "o": offset, "l": limit}
        self._send(message)

    def send_message(self, recipient: str, content: str):
        """Send a message to another user."""
        if not self.logged_in:
            self.gui.display_message("Please log in first")
            return
        message = {"t": "send_message", "r": recipient, "c": content}
        self._send(message)

    def pop_unread_messages(self, count: int):
        """Pop unread messages."""
        if not self.logged_in:
            self.gui.display_message("Please log in first")
            return
        message = {"t": "pop_unread", "c": count}
        self._send(message)

    def get_read_messages(self, offset: int, limit: int):
        """Get read messages."""
        if not self.logged_in:
            self.gui.display_message("Please log in first")
            return
        message = {"t": "get_read", "o": offset, "l": limit}
        self._send(message)

    def delete_messages(self, message_ids: List[int]):
        """Delete messages."""
        if not self.logged_in:
            self.gui.display_message("Please log in first")
            return
        message = {"t": "delete_messages", "ids": message_ids}
        self._send(message)

    def delete_account(self):
        """Delete account."""
        if not self.logged_in:
            self.gui.display_message("Please log in first")
            return
        message = {"t": "delete_account"}
        self._send(message)
        self.logged_in = False

    def _send(self, message: Dict):
        """Send a message to the server."""
        try:
            self.socket.send(json.dumps(message).encode('utf-8'))
        except Exception as e:
            self.gui.display_message(f"Failed to send message: {e}")

    def _receive_messages(self):
        """Receive messages from the server."""
        while True:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break

                response = json.loads(data.decode('utf-8'))
                self._handle_response(response)

            except Exception as e:
                self.gui.display_message(f"Connection error: {e}")
                break

        self.socket.close()

    def _handle_response(self, response: Dict):
        """Handle server responses."""
        if "error" in response:
            self.gui.display_message(response["error"])
            return

        msg_type = response.get("t")
        if msg_type == "login":
            self.logged_in = True
            self.gui.update_unread_count(response.get("unread", 0))
        elif msg_type == "list_users":
            self.gui.display_users(response["users"])
        elif msg_type == "messages":
            self.gui.display_messages(response["messages"])
        elif msg_type == "unread_count":
            self.gui.update_unread_count(response["count"])
        elif msg_type == "new_message":
            self.gui.update_unread_count(response["unread"])
            self.gui.display_message(f"New message from {response['sender']}")
