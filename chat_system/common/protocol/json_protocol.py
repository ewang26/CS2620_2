import json
from typing import Optional, List, Tuple, Any
from ..user import User, Message
from .protocol import *

# Helper functions to serialize and deserialize messages
def message_to_json(message: Message) -> Any:
    return {"i": message.id, "s": message.sender, "c": message.content}

def json_to_message(data: Any) -> Message:
    return Message(data["i"], data["s"], data["c"])

class JSON_CreateAccountMessage(CreateAccountMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type, "n": self.name, "p": self.password}).encode('utf-8')
    def unpack(self, data: bytes):
        d = json.loads(data.decode('utf-8'))
        self.name = d["n"]
        self.password = d["p"]
    def pack_return(self, data: Optional[str]) -> bytes:
        return json.dumps({"r": data}).encode('utf-8')
    def unpack_return(self, data: bytes) -> Optional[str]:
        return json.loads(data.decode('utf-8'))["r"]

class JSON_LoginMessage(LoginMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type, "n": self.name, "p": self.password}).encode('utf-8')
    def unpack(self, data: bytes):
        d = json.loads(data.decode('utf-8'))
        self.name = d["n"]
        self.password = d["p"]
    def pack_return(self, data: Optional[str]) -> bytes:
        return json.dumps({"r": data}).encode('utf-8')
    def unpack_return(self, data: bytes) -> Optional[str]:
        return json.loads(data.decode('utf-8'))["r"]

class JSON_ListUsersMessage(ListUsersMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type, "p": self.pattern, "o": self.offset, "l": self.limit}).encode('utf-8')
    def unpack(self, data: bytes):
        d = json.loads(data.decode('utf-8'))
        self.pattern = d["p"]
        self.offset = d["o"]
        self.limit = d["l"]
    def pack_return(self, data: List[User]) -> bytes:
        user_pairs = []
        for user in data:
            user_pairs.append([user.id, user.name])
        return json.dumps({"r": user_pairs}).encode('utf-8')
    def unpack_return(self, data: bytes) -> List[Tuple[int, str]]:
        user_pairs = json.loads(data.decode('utf-8'))["r"]
        return [(pair[0], pair[1]) for pair in user_pairs]

class JSON_GetUserFromIdMessage(GetUserFromIdMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type, "u": self.user_id}).encode('utf-8')
    def unpack(self, data: bytes):
        self.user_id = json.loads(data.decode('utf-8'))["u"]
    def pack_return(self, data: str) -> bytes:
        return json.dumps({"r": data}).encode('utf-8')
    def unpack_return(self, data: bytes) -> str:
        return json.loads(data.decode('utf-8'))["r"]

class JSON_DeleteAccountMessage(DeleteAccountMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type}).encode('utf-8')
    def unpack(self, data: bytes):
        pass
    def pack_return(self, data: any) -> bytes:
        pass
    def unpack_return(self, data: bytes) -> any:
        pass

class JSON_SendMessageMessage(SendMessageMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type, "r": self.receiver, "c": self.content}).encode('utf-8')
    def unpack(self, data: bytes):
        d = json.loads(data.decode('utf-8'))
        self.receiver = d["r"]
        self.content = d["c"]
    def pack_return(self, data: any) -> bytes:
        pass
    def unpack_return(self, data: bytes) -> any:
        pass

class JSON_ReceivedMessageMessage(ReceivedMessageMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type, "n": message_to_json(self.new_message)}).encode('utf-8')
    def unpack(self, data: bytes):
        d = json.loads(data.decode('utf-8'))
        self.new_message = json_to_message(d["n"])
    def pack_return(self, data: any) -> bytes:
        pass
    def unpack_return(self, data: bytes) -> any:
        pass

class JSON_GetNumberOfUnreadMessagesMessage(GetNumberOfUnreadMessagesMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type}).encode('utf-8')
    def unpack(self, data: bytes):
        pass
    def pack_return(self, data: int) -> bytes:
        return json.dumps({"r": data}).encode('utf-8')
    def unpack_return(self, data: bytes) -> int:
        return json.loads(data.decode('utf-8'))["r"]

class JSON_PopUnreadMessagesMessage(PopUnreadMessagesMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type, "n": self.num_messages}).encode('utf-8')
    def unpack(self, data: bytes):
        self.num_messages = json.loads(data.decode('utf-8'))["n"]
    def pack_return(self, data: List[Message]) -> bytes:
        messages_json = [message_to_json(m) for m in data]
        return json.dumps({"r": messages_json}).encode('utf-8')
    def unpack_return(self, data: bytes) -> List[Message]:
        d = json.loads(data.decode('utf-8'))["r"]
        return [json_to_message(m) for m in d]

class JSON_GetReadMessagesMessage(GetReadMessagesMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type, "o": self.offset, "n": self.num_messages}).encode('utf-8')
    def unpack(self, data: bytes):
        d = json.loads(data.decode('utf-8'))
        self.offset = d["o"]
        self.num_messages = d["n"]
    def pack_return(self, data: List[Message]) -> bytes:
        messages_json = [message_to_json(m) for m in data]
        return json.dumps({"r": messages_json}).encode('utf-8')
    def unpack_return(self, data: bytes) -> List[Message]:
        d = json.loads(data.decode('utf-8'))["r"]
        return [json_to_message(m) for m in d]

class JSON_DeleteMessagesMessage(DeleteMessagesMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type, "m": self.message_ids}).encode('utf-8')
    def unpack(self, data: bytes):
        self.message_ids = json.loads(data.decode('utf-8'))["m"]
    def pack_return(self, data: any) -> bytes:
        pass
    def unpack_return(self, data: bytes) -> any:
        pass

class JSONProtocol(Protocol):
    message_classes: Dict[MessageType, Type[ProtocolMessage]] = {
        MessageType.CREATE_ACCOUNT: JSON_CreateAccountMessage,
        MessageType.LOGIN: JSON_LoginMessage,
        MessageType.LIST_USERS: JSON_ListUsersMessage,
        MessageType.GET_USER_FROM_ID: JSON_GetUserFromIdMessage,
        MessageType.DELETE_ACCOUNT: JSON_DeleteAccountMessage,
        MessageType.SEND_MESSAGE: JSON_SendMessageMessage,
        MessageType.RECEIVED_MESSAGE: JSON_ReceivedMessageMessage,
        MessageType.GET_NUMBER_OF_UNREAD_MESSAGES: JSON_GetNumberOfUnreadMessagesMessage,
        MessageType.POP_UNREAD_MESSAGES: JSON_PopUnreadMessagesMessage,
        MessageType.GET_READ_MESSAGES: JSON_GetReadMessagesMessage,
        MessageType.DELETE_MESSAGES: JSON_DeleteMessagesMessage
    }

    def parse_message(self, data: bytes) -> ProtocolMessage:
        d = json.loads(data.decode('utf-8'))
        message = (self.message_class(d["t"]))()
        message.unpack(data)
        return message
