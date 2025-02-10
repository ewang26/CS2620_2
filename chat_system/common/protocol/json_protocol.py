import json
from typing import Optional, Tuple, Any

from .protocol import *
from ..user import User


# Helper functions to serialize and deserialize messages
def message_to_json(message: Message) -> Any:
    return {"i": message.id, "s": message.sender, "c": message.content}


def json_to_message(data: Any) -> Message:
    return Message(data["i"], data["s"], data["c"])


class JSON_CreateAccountMessage(CreateAccountMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type, "n": self.name, "p": self.password}).encode('utf-8')

    def pack_return(self, data: Optional[str]) -> bytes:
        return json.dumps({"t": self.type, "r": data}).encode('utf-8')

    @classmethod
    def unpack(cls, data: bytes) -> Self:
        d = json.loads(data.decode('utf-8'))
        return cls(d["n"], d["p"])

    @classmethod
    def unpack_return(cls, data: bytes) -> Optional[str]:
        return json.loads(data.decode('utf-8'))["r"]


class JSON_LoginMessage(LoginMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type, "n": self.name, "p": self.password}).encode('utf-8')

    def pack_return(self, data: Optional[str]) -> bytes:
        return json.dumps({"t": self.type, "r": data}).encode('utf-8')

    @classmethod
    def unpack(cls, data: bytes) -> Self:
        d = json.loads(data.decode('utf-8'))
        return cls(d["n"], d["p"])

    @classmethod
    def unpack_return(cls, data: bytes) -> Optional[str]:
        return json.loads(data.decode('utf-8'))["r"]


class JSON_ListUsersMessage(ListUsersMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type, "p": self.pattern, "o": self.offset, "l": self.limit}).encode('utf-8')

    def pack_return(self, data: List[User]) -> bytes:
        user_pairs = []
        for user in data:
            user_pairs.append([user.id, user.name])
        return json.dumps({"t": self.type, "r": user_pairs}).encode('utf-8')

    @classmethod
    def unpack(cls, data: bytes) -> Self:
        d = json.loads(data.decode('utf-8'))
        return cls(d["p"], d["o"], d["l"])

    @classmethod
    def unpack_return(cls, data: bytes) -> List[Tuple[int, str]]:
        user_pairs = json.loads(data.decode('utf-8'))["r"]
        return [(pair[0], pair[1]) for pair in user_pairs]


class JSON_GetUserFromIdMessage(GetUserFromIdMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type, "u": self.user_id}).encode('utf-8')

    def pack_return(self, data: str) -> bytes:
        return json.dumps({"t": self.type, "r": data}).encode('utf-8')

    @classmethod
    def unpack(cls, data: bytes) -> Self:
        return cls(json.loads(data.decode('utf-8'))["u"])

    @classmethod
    def unpack_return(cls, data: bytes) -> str:
        return json.loads(data.decode('utf-8'))["r"]


class JSON_DeleteAccountMessage(DeleteAccountMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type}).encode('utf-8')

    def pack_return(self, data: any) -> bytes:
        pass

    @classmethod
    def unpack(cls, data: bytes) -> Self:
        return cls()

    @classmethod
    def unpack_return(cls, data: bytes) -> any:
        pass


class JSON_SendMessageMessage(SendMessageMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type, "r": self.receiver, "c": self.content}).encode('utf-8')

    def pack_return(self, data: any) -> bytes:
        pass

    @classmethod
    def unpack(cls, data: bytes) -> Self:
        d = json.loads(data.decode('utf-8'))
        return cls(d["r"], d["c"])

    @classmethod
    def unpack_return(cls, data: bytes) -> any:
        pass


class JSON_ReceivedMessageMessage(ReceivedMessageMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type, "n": message_to_json(self.new_message)}).encode('utf-8')

    def pack_return(self, data: any) -> bytes:
        pass

    @classmethod
    def unpack(cls, data: bytes) -> Self:
        d = json.loads(data.decode('utf-8'))
        return cls(json_to_message(d["n"]))

    @classmethod
    def unpack_return(cls, data: bytes) -> any:
        pass


class JSON_GetNumberOfUnreadMessagesMessage(GetNumberOfUnreadMessagesMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type}).encode('utf-8')

    def pack_return(self, data: int) -> bytes:
        return json.dumps({"t": self.type, "r": data}).encode('utf-8')

    @classmethod
    def unpack(cls, data: bytes) -> Self:
        return cls()

    @classmethod
    def unpack_return(cls, data: bytes) -> int:
        return json.loads(data.decode('utf-8'))["r"]


class JSON_PopUnreadMessagesMessage(PopUnreadMessagesMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type, "n": self.num_messages}).encode('utf-8')

    def pack_return(self, data: List[Message]) -> bytes:
        messages_json = [message_to_json(m) for m in data]
        return json.dumps({"t": self.type, "r": messages_json}).encode('utf-8')

    @classmethod
    def unpack(cls, data: bytes) -> Self:
        return cls(json.loads(data.decode('utf-8'))["n"])

    @classmethod
    def unpack_return(cls, data: bytes) -> List[Message]:
        d = json.loads(data.decode('utf-8'))["r"]
        return [json_to_message(m) for m in d]


class JSON_GetReadMessagesMessage(GetReadMessagesMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type, "o": self.offset, "n": self.num_messages}).encode('utf-8')

    def pack_return(self, data: List[Message]) -> bytes:
        messages_json = [message_to_json(m) for m in data]
        return json.dumps({"t": self.type, "r": messages_json}).encode('utf-8')

    @classmethod
    def unpack(cls, data: bytes) -> Self:
        d = json.loads(data.decode('utf-8'))
        return cls(d["o"], d["n"])

    @classmethod
    def unpack_return(cls, data: bytes) -> List[Message]:
        d = json.loads(data.decode('utf-8'))["r"]
        return [json_to_message(m) for m in d]


class JSON_DeleteMessagesMessage(DeleteMessagesMessage):
    def pack(self) -> bytes:
        return json.dumps({"t": self.type, "m": self.message_ids}).encode('utf-8')

    def pack_return(self, data: any) -> bytes:
        pass

    @classmethod
    def unpack(cls, data: bytes) -> Self:
        return cls(json.loads(data.decode('utf-8'))["m"])

    @classmethod
    def unpack_return(cls, data: bytes) -> any:
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

    def get_message_type(self, data: bytes) -> MessageType:
        d = json.loads(data.decode('utf-8'))
        return d["t"]
