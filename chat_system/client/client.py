import socket
import threading
from typing import Optional
from ..common.protocol.custom_protocol import Protocol, MessageType
from .gui import ChatGUI

class ChatClient:
    def __init__(self, host: str = 'localhost', port: int = 8888):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gui = ChatGUI(
            on_login=self.login,
            on_create_account=self.create_account,
            on_send_message=self.send_message,
            on_list_accounts=self.list_accounts
        )
    
    def connect(self):
        #connect to the server
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
    
    def create_account(self, username: str, password: str):
        #send create account request
        message = Protocol.create_account_request(username, password)
        self.socket.send(message)
    
    def login(self, username: str, password: str):
        """Send login request."""
        message = Protocol.login_request(username, password)
        self.socket.send(message)
    
    def list_accounts(self, pattern: Optional[str]):
        """Send list accounts request."""
        message = Protocol.list_accounts_request(pattern)
        self.socket.send(message)
    
    def send_message(self, recipient: str, content: str):
        """Send a chat message."""
        message = Protocol.send_message_request(recipient, content)
        self.socket.send(message)
    
    def _receive_messages(self):
        """Receive and process messages from the server."""
        while True:
            try:
                data = self.socket.recv(4096)
                if not data:
                    self.gui.display_message("Disconnected from server")
                    break
                
                message = Protocol.unpack_message(data)
                
                if message.type == MessageType.SUCCESS:
                    self.gui.display_message(f"Success: {message.payload.decode()}")
                elif message.type == MessageType.ERROR:
                    self.gui.display_message(f"Error: {message.payload.decode()}")
                elif message.type == MessageType.ACCOUNT_LIST:
                    accounts = message.payload.decode().split(',')
                    self.gui.display_message("Accounts:")
                    for account in accounts:
                        self.gui.display_message(f"- {account}")
                elif message.type == MessageType.RECEIVE_MESSAGE:
                    sender, content = message.payload.decode().split(':', 1)
                    self.gui.display_message(f"From {sender}: {content}")
                
            except Exception as e:
                self.gui.display_message(f"Error receiving message: {e}")
                break
    
    def run(self):
        """Start the client."""
        if self.connect():
            self.gui.run()

if __name__ == "__main__":
    client = ChatClient()
    client.run() 