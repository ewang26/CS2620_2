import json
from typing import Optional, Tuple, Any, Union, List

from .protocol import *
from ..user import User


# Helper functions to serialize and deserialize messages
def message_to_json(message: Message) -> Any:
    return {"i": message.id, "s": message.sender, "c": message.content}


def json_to_message(data: Any) -> Message:
    return Message(data["i"], data["s"], data["c"])


class JSON_CreateAccountMessage(CreateAccountMessage):
    def pack_server(self) -> bytes:
        return json.dumps({"t": self.type, "n": self.name, "p": self.password}).encode('utf-8')

    def pack_client(self, data: Optional[str]) -> bytes:
        return json.dumps({"t": self.type, "r": data}).encode('utf-8')

    @classmethod
    def unpack_server(cls, data: bytes) -> Self:
        d = json.loads(data.decode('utf-8'))
        return cls(d["n"], d["p"])

    @classmethod
    def unpack_client(cls, data: bytes) -> Optional[str]:
        return json.loads(data.decode('utf-8'))["r"]


class JSON_LoginMessage(LoginMessage):
    def pack_server(self) -> bytes:
        return json.dumps({"t": self.type, "n": self.name, "p": self.password}).encode('utf-8')

    def pack_client(self, data: Optional[str]) -> bytes:
        return json.dumps({"t": self.type, "r": data}).encode('utf-8')

    @classmethod
    def unpack_server(cls, data: bytes) -> Self:
        d = json.loads(data.decode('utf-8'))
        return cls(d["n"], d["p"])

    @classmethod
    def unpack_client(cls, data: bytes) -> Optional[str]:
        return json.loads(data.decode('utf-8'))["r"]


class JSON_LogoutMessage(LogoutMessage):
    def pack_server(self) -> bytes:
        return json.dumps({"t": self.type}).encode('utf-8')

    def pack_client(self, data: any) -> bytes:
        pass

    @classmethod
    def unpack_server(cls, data: bytes) -> Self:
        return cls()

    @classmethod
    def unpack_client(cls, data: bytes) -> any:
        pass


class JSON_ListUsersMessage(ListUsersMessage):
    def pack_server(self) -> bytes:
        return json.dumps({"t": self.type, "p": self.pattern, "o": self.offset, "l": self.limit}).encode('utf-8')

    def pack_client(self, data: List[User]) -> bytes:
        users = [user.name for user in data]
        return json.dumps({"t": self.type, "r": users}).encode('utf-8')

    @classmethod
    def unpack_server(cls, data: bytes) -> Self:
        d = json.loads(data.decode('utf-8'))
        return cls(d["p"], d["o"], d["l"])

    @classmethod
    def unpack_client(cls, data: bytes) -> List[str]:
        return json.loads(data.decode('utf-8'))["r"]


class JSON_DeleteAccountMessage(DeleteAccountMessage):
    def pack_server(self) -> bytes:
        return json.dumps({"t": self.type}).encode('utf-8')

    def pack_client(self, data: any) -> bytes:
        pass

    @classmethod
    def unpack_server(cls, data: bytes) -> Self:
        return cls()

    @classmethod
    def unpack_client(cls, data: bytes) -> any:
        pass


class JSON_SendMessageMessage(SendMessageMessage):
    def pack_server(self) -> bytes:
        return json.dumps({"t": self.type, "r": self.receiver, "c": self.content}).encode('utf-8')

    def pack_client(self, data: any) -> bytes:
        pass

    @classmethod
    def unpack_server(cls, data: bytes) -> Self:
        d = json.loads(data.decode('utf-8'))
        return cls(d["r"], d["c"])

    @classmethod
    def unpack_client(cls, data: bytes) -> any:
        pass


class JSON_ReceivedMessageMessage(ReceivedMessageMessage):
    def pack_server(self) -> bytes:
        pass

    def pack_client(self, data: any) -> bytes:
        return json.dumps({"t": self.type, "n": message_to_json(self.new_message)}).encode('utf-8')

    @classmethod
    def unpack_server(cls, data: bytes) -> any:
        pass

    @classmethod
    def unpack_client(cls, data: bytes) -> Self:
        d = json.loads(data.decode('utf-8'))
        return cls(json_to_message(d["n"]))


class JSON_GetNumberOfUnreadMessagesMessage(GetNumberOfUnreadMessagesMessage):
    def pack_server(self) -> bytes:
        return json.dumps({"t": self.type}).encode('utf-8')

    def pack_client(self, data: int) -> bytes:
        return json.dumps({"t": self.type, "r": data}).encode('utf-8')

    @classmethod
    def unpack_server(cls, data: bytes) -> Self:
        return cls()

    @classmethod
    def unpack_client(cls, data: bytes) -> int:
        return json.loads(data.decode('utf-8'))["r"]


class JSON_GetNumberOfReadMessagesMessage(GetNumberOfReadMessagesMessage):
    def pack_server(self) -> bytes:
        return json.dumps({"t": self.type}).encode('utf-8')

    def pack_client(self, data: int) -> bytes:
        return json.dumps({"t": self.type, "r": data}).encode('utf-8')

    @classmethod
    def unpack_server(cls, data: bytes) -> Self:
        return cls()

    @classmethod
    def unpack_client(cls, data: bytes) -> int:
        return json.loads(data.decode('utf-8'))["r"]


class JSON_PopUnreadMessagesMessage(PopUnreadMessagesMessage):
    def pack_server(self) -> bytes:
        return json.dumps({"t": self.type, "n": self.num_messages}).encode('utf-8')

    def pack_client(self, data: List[Message]) -> bytes:
        messages_json = [message_to_json(m) for m in data]
        return json.dumps({"t": self.type, "r": messages_json}).encode('utf-8')

    @classmethod
    def unpack_server(cls, data: bytes) -> Self:
        return cls(json.loads(data.decode('utf-8'))["n"])

    @classmethod
    def unpack_client(cls, data: bytes) -> List[Message]:
        d = json.loads(data.decode('utf-8'))["r"]
        return [json_to_message(m) for m in d]


class JSON_GetReadMessagesMessage(GetReadMessagesMessage):
    def pack_server(self) -> bytes:
        return json.dumps({"t": self.type, "o": self.offset, "n": self.num_messages}).encode('utf-8')

    def pack_client(self, data: List[Message]) -> bytes:
        messages_json = [message_to_json(m) for m in data]
        return json.dumps({"t": self.type, "r": messages_json}).encode('utf-8')

    @classmethod
    def unpack_server(cls, data: bytes) -> Self:
        d = json.loads(data.decode('utf-8'))
        return cls(d["o"], d["n"])

    @classmethod
    def unpack_client(cls, data: bytes) -> List[Message]:
        d = json.loads(data.decode('utf-8'))["r"]
        return [json_to_message(m) for m in d]


class JSON_DeleteMessagesMessage(DeleteMessagesMessage):
    def pack_server(self) -> bytes:
        return json.dumps({"t": self.type, "m": self.message_ids}).encode('utf-8')

    def pack_client(self, data: any) -> bytes:
        pass

    @classmethod
    def unpack_server(cls, data: bytes) -> Self:
        return cls(json.loads(data.decode('utf-8'))["m"])

    @classmethod
    def unpack_client(cls, data: bytes) -> any:
        pass


class JSONProtocol(Protocol):
    message_classes: Dict[MessageType, Type[ProtocolMessage]] = {
        MessageType.CREATE_ACCOUNT: JSON_CreateAccountMessage,
        MessageType.LOGIN: JSON_LoginMessage,
        MessageType.LOGOUT: JSON_LogoutMessage,
        MessageType.LIST_USERS: JSON_ListUsersMessage,
        MessageType.DELETE_ACCOUNT: JSON_DeleteAccountMessage,
        MessageType.SEND_MESSAGE: JSON_SendMessageMessage,
        MessageType.RECEIVED_MESSAGE: JSON_ReceivedMessageMessage,
        MessageType.GET_NUMBER_OF_UNREAD_MESSAGES: JSON_GetNumberOfUnreadMessagesMessage,
        MessageType.GET_NUMBER_OF_READ_MESSAGES: JSON_GetNumberOfReadMessagesMessage,
        MessageType.POP_UNREAD_MESSAGES: JSON_PopUnreadMessagesMessage,
        MessageType.GET_READ_MESSAGES: JSON_GetReadMessagesMessage,
        MessageType.DELETE_MESSAGES: JSON_DeleteMessagesMessage
    }

    def get_message_type(self, data: bytes) -> MessageType:
        d = json.loads(data.decode('utf-8'))
        return d["t"]
