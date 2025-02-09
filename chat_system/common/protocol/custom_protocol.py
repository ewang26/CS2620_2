from dataclasses import dataclass
import struct
from typing import Optional, List
from .protocol import MessageType, Protocol

class CustomProtocol(Protocol):
    """
    Custom binary protocol implementation.
    Message format:
    - 1 byte: Message type
    - 4 bytes: Payload length (uint32)
    - N bytes: Payload
    """

    # @staticmethod
    # def pack_message(msg_type: MessageType, payload: bytes) -> bytes:
    #     """Pack a message into bytes according to protocol."""
    #     payload_len = len(payload)
    #     header = struct.pack('!BL', msg_type, payload_len)
    #     return header + payload
    #
    # @staticmethod
    # def unpack_message(data: bytes) -> Message:
    #     """Unpack bytes into a Message object."""
    #     msg_type, payload_len = struct.unpack('!BL', data[:5])
    #     payload = data[5:5+payload_len]
    #     return Message(MessageType(msg_type), payload_len, payload)
    #
    # @staticmethod
    # def create_account_request(username: str, password: str) -> bytes:
    #     """Create an account creation request."""
    #     payload = f"{username}:{password}".encode()
    #     return Protocol.pack_message(MessageType.CREATE_ACCOUNT, payload)
    #
    # @staticmethod
    # def login_request(username: str, password: str) -> bytes:
    #     """Create a login request."""
    #     payload = f"{username}:{password}".encode()
    #     return Protocol.pack_message(MessageType.LOGIN, payload)
    #
    # @staticmethod
    # def list_accounts_request(pattern: Optional[str] = None) -> bytes:
    #     """Create a list accounts request."""
    #     payload = pattern.encode() if pattern else b''
    #     return Protocol.pack_message(MessageType.LIST_ACCOUNTS, payload)
    #
    # @staticmethod
    # def send_message_request(recipient: str, content: str) -> bytes:
    #     """Create a message send request."""
    #     payload = f"{recipient}:{content}".encode()
    #     return Protocol.pack_message(MessageType.SEND_MESSAGE, payload)
