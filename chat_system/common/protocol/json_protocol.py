import json
from typing import Optional, Dict, Any
from enum import Enum

class MessageType(str, Enum):
    CREATE_ACCOUNT = "create_account"
    LOGIN = "login"
    LIST_ACCOUNTS = "list_accounts"
    SEND_MESSAGE = "send_message"
    RECEIVE_MESSAGE = "receive_message"
    SUCCESS = "success"
    ERROR = "error"
    ACCOUNT_LIST = "account_list"

class JSONProtocol:
    @staticmethod
    def create_message(msg_type: MessageType, **payload) -> bytes:
        """Create a JSON message."""
        message = {
            "type": msg_type,
            "payload": payload
        }
        return json.dumps(message).encode()
    
    @staticmethod
    def parse_message(data: bytes) -> Dict[str, Any]:
        """Parse a JSON message."""
        return json.loads(data.decode())
    
    @staticmethod
    def create_account_request(username: str, password: str) -> bytes:
        return JSONProtocol.create_message(
            MessageType.CREATE_ACCOUNT,
            username=username,
            password=password
        )
    
    @staticmethod
    def login_request(username: str, password: str) -> bytes:
        return JSONProtocol.create_message(
            MessageType.LOGIN,
            username=username,
            password=password
        )
    
    @staticmethod
    def list_accounts_request(pattern: Optional[str] = None) -> bytes:
        return JSONProtocol.create_message(
            MessageType.LIST_ACCOUNTS,
            pattern=pattern
        )
    
    @staticmethod
    def send_message_request(recipient: str, content: str) -> bytes:
        return JSONProtocol.create_message(
            MessageType.SEND_MESSAGE,
            recipient=recipient,
            content=content
        ) 