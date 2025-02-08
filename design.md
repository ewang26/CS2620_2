# Client-Server Architecture

## Overview

We want to build a client-server chat application, where **multiple clients** connect over sockets to the server. Each client can either create or log into an account, so messages from each client will be tied to **one user** at a time.

A user can do the following tasks:
- Provide a wildcard pattern and get a list of users matching it
  - Potentially do pagination, if there are a lot of users that match
- Send a message to a single user
- Read currently unread messages
  - Again may need to do pagination
- Read all received messages
  - Again may need to do pagination
- Delete a (set of) message(s)
- Delete an account
  - Any delivered messages from this user should not be deleted

## Server state
At a high level, the server should maintain a list of `User`s. Each user then has an `unread_mailbox` and `read_mailbox` of `Message`s. Sending messages to a user will add a message to their `unread_mailbox`, and deleting messages will move them to the `read_mailbox`.

To help id users and messages, each user and message should have a unique UUID. We can keep a global state of `nextUserId` and `nextMessageId` to help generate these. This means we can also store users and messages in a dictionary, with the UUID as the key.

Concretely, we should have
```python
class User:
    name: str
    id: int
    mailbox: Dict[int, Message]

class Message:
    id: int
    sender: int
    receiver: int
    content: str
```

When a client logs in, the server should map the client's socket to its user id. This way, the client doesn't need to send its user id with every request.

Note that because many clients can be connected at once (potentially with one user on multiple clients as well), there may be concurrent accesses to the server state. We can either use a lock to protect the state, or have the server be single-threaded and use a queue to handle requests. **We chose the second option for simplicity, and because we don't expect a high load on the server.**

## Interfaces

`CreateAccount(name: str, password: str) -> bool`:

`Login(name: str, password: str) -> int`:

`ListUsers(pattern: str, page: int) -> List[Tuple[int, str]]`:

`GetUserFromId(user_id: int) -> str`:

`SendMessage(receiver: int, content: str) -> bool`:

`GetNumberOfUnreadMessages() -> int`:

`GetUnreadMessages(page: int) -> List[Message]`:

`MarkMessageAsRead(message_id: int) -> bool`:

`GetReadMessages(page: int) -> List[Message]`:

`DeleteMessages(message_ids: List[int]) -> bool`:

`DeleteAccount() -> bool`:

## Wire Protocol

For our custom protocol, we can use the fact that each interface has a constant type for fields and return values. When a client is calling an interface, it will first send a 1-byte request type, followed by the arguments for the interface. The server will then respond with the return value. The server does not need to identify the return type, since each client is only calling one interface at a time.

The arguments and return values are encoded into bytes as follows:
- `str`: 4-byte length, followed by the string
- `int`: 4-byte integer
- `List[...]`: 4-byte length, followed by the encoded elements
- `Tuple[...]`: sequentially encode the elements
- `bool`: 1-byte integer, 0 for False, 1 for True
- `Message`: sequentially encode `id`, `sender`, and `content`. The `receiver` is not needed, since it is the user calling the interface.

