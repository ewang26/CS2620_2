# Engineering Notebook

### 2/12/25

- Ran into an issue where messages that are sent immediately after each other are received on the same socket poll, but only the first message is processed. To fix this, we need to add some form of message framing to the protocol. 

- Went and got rid of all user ID entirely, now that we're using usernames to send messages.

- Added to our test suite. In particular, we create a password security test that tests empty passwords and long passwords, and makes sure that even if two users use the same passwords, the salts and hashes are different. We also test if the message ordering is preserved through the queue/mailbox system and if passwords can handle edge cases where special characters and Unicode are used.

### 2/11/25

- Decided to send messages using a user's username rather than their ID in the GUI. In the list of users, we show the username and their corresponding ID, but to make this more user-friendly, we map the username to the ID on the server-side, so the user only needs to specify the username of the user they want to send messages to.


### 2/10/25

- While working on the wire protocol, we replaced the old protocol methods in custom_protocol.py with new custom_message classes. Specifically, pack_message and unpack_message are replaced by the pack_server/pack_client/unpack_server/unpack_client methods in each Custom_Message class. And the request methods are replaced as follows:
create_account_request -> Custom_CreateAccountMessage
login_request -> Custom_LoginMessage
list_accounts_request -> Custom_ListUsersMessage
send_message_request -> Custom_SendMessageMessage.

- Ran into a small bug where immediately delivered messages were not being added to the read mailbox. Should add this as part of a test case.

- Instead of thinking in terms of packing message and return value, we should refer to them as packing client/server messages. This helps unify the interfaces of messages sent in either direction. 

- 🎉successful client server login🎉, protocol does actually work :D 

- When thinking about multithreading the client, realized we would want one thread for reading + one thread for writing. This implies that **return messages should be typed as well**, since we need to know what to do with the response. This is a change from the current design, where we currently assume the client knows how to pair requests with responses.

### 2/9/25

- Finished implementation tests; caught a few bugs around the methods that fetch a limited number of elements, but nothing major. Also turns out password hashing is a bit slow, added as a TODO for later.

- Started implementing server tests for each possible message. Not comprehensive, but they give confidence that the main functionality is working.

- Made progress on the client-side, focusing on implementing the GUI interface in the ChatGUI class. In particular, added functionality for deleting messages and accounts, as well as getting read messages/displaying unread message count. But the client can't connect to the server yet.

- Still need to implement the custom protocol.

### 2/8/25

- Went between a few protocol designs that could be extended to allow both our custom and json protocol. Finally landed on a design where we have a class per message type, since that is what is extended between the protocols.

- Realized that we want clients who are logged in to immediately receive incoming messages. That means we need the server to also communicate with the client; added this to the design doc.

- Thinking about reporting errors, what if we have an optional return type? For example, can return `0` byte for no error, or string if there is an error. This way, we can have a more flexible error reporting system.

- Crafted an initial design of the protocol, done with efficiency of the number of bits in mind. However, I'm not sure if the current protocol leads to unnecessary interface calls. Planning to revisit the design with this in mind.

- After getting a basic code structure down, returned back to the requirements and started crafting a design doc to help guide the implementation.

- Tried to start by just writing some code and getting the first four requires (creating accounts, logging in, listing accounts, and sending messages) working. The intent was to get a good feel of the problem at hand and try and find any potential issues early on.

- The basic project structure I created was:
   
```
   chat_system/
   ├── client/
   │   └── __init__.py
   ├── tests/
   │   ├── __init__.py
   │   ├── test_protocol.py
   │   └── test_server.py
   └── setup.py
```

- Some technical decisions we made were to use Python's unittest framework for testing. This provides comprehensive testing capabilities and is integrated with Python ecosystem
