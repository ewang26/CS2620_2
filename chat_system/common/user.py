from dataclasses import dataclass
from typing import List

@dataclass
class Message:
    id: int
    sender: str
    content: str

@dataclass
class User:
    id: int
    name: str
    message_queue: List[Message]
    read_mailbox: List[Message]

    def add_message(self, message: Message):
        self.message_queue.append(message)

    def pop_unread_messages(self, num_messages: int) -> List[Message]:
        messages = self.message_queue[:num_messages]
        self.message_queue = self.message_queue[num_messages:]
        self.read_mailbox.extend(messages)
        return messages

    def get_number_of_unread_messages(self) -> int:
        return len(self.message_queue)

    def get_read_messages(self, offset: int, num_messages: int) -> List[Message]:
        return self.read_mailbox[-num_messages-offset:-offset]

    def delete_messages(self, message_ids: List[int]):
        for id in message_ids:
            for message in self.read_mailbox:
                if message.id == id:
                    self.read_mailbox.remove(message)
                    break
