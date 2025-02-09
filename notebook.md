# Engineering Notebook

### 2/8/25

- Realized that we want clients who are logged in to immediately receive incoming messages. That means we need the server to also communicate with the client; added this to the design doc.

- Thinking about reporting errors, what if we have an optional return type? For example, can return `0` byte for no error, or string if there is an error. This way, we can have a more flexible error reporting system.

- Crafted an initial design of the protocol, done with efficiency of the number of bits in mind. However, I'm not sure if the current protocol leads to unnecessary interface calls. Planning to revisit the design with this in mind.

- After getting a basic code structure down, returned back to the requirements and started crafting a design doc to help guide the implementation.

- Tried to start by just writing some code and getting the first four requires (creating accounts, logging in, listing accounts, and sending messages) working. The intent was to get a good feel of the problem at hand and try and find any potential issues early on.

- The basic project structure I created was:
   
   chat_system/
   ├── client/
   │   └── __init__.py
   ├── tests/
   │   ├── __init__.py
   │   ├── test_protocol.py
   │   └── test_server.py
   └── setup.py

- Some technical decisions we made were to use Python's unittest framework for testing. This provides comprehensive testing capabilities and is integrated with Python ecosystem
