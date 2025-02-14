# CS 2620 Client-Server Chat System

This project is a simple client-server chat system. The general architecture is detailed in the [design document](design.md).

### Configuration
The server and client can be configured using the shared `config.json` file. This JSON file contains the following fields:
- `host`: The host to bind the server to. Default is `localhost`.
- `port`: The port to bind the server to. Default is `8888`.
- `use_custom_protocol`: Whether to use the custom protocol or the JSON protocol. Default is `true`.
- `server_data`: The path to the server data file. Default is `server_data.json`.

### Running
Once the configuration file is set up, the server can be started with
```bash
python -m chat_system.server
```
and the client can be started with
```bash
python -m chat_system.client
```

You can optionally give an alternative path to a config file as a command line argument:
```bash
python -m chat_system.server path/to/config.json
```

Our codebase is organized such that it has the following structure:

# Chat System Project Structure

```
chat_system/
│
├─ setup.py                # Package setup configuration
├─ config.json             # Main configuration file
├─ client_config.json      # Client-specific configuration
├─ server_config.json      # Server-specific configuration
├─ notebook.md             # Engineering notebook
├─ design.md               # Design document
│
├─ client/                 # Client-side code
│  ├─ __init__.py
│  ├─ __main__.py         # Client entry point
│  ├─ client.py           # Client implementation
│  └─ gui.py              # GUI implementation
│
├─ server/                 # Server-side code
│  ├─ __init__.py
│  ├─ __main__.py         # Server entry point
│  ├─ server.py           # Server implementation
│  └─ account_manager.py  # User account management
│
├─ common/                 # Shared code between client and server
│  ├─ __init__.py
│  ├─ config.py           # Configuration loading
│  ├─ security.py         # Password hashing and verification
│  ├─ user.py             # User and Message data models
│  │
│  └─ protocol/           # Protocol implementations
│     ├─ __init__.py
│     ├─ protocol.py      # Base protocol classes
│     ├─ custom_protocol.py # Binary protocol implementation
│     └─ json_protocol.py  # JSON protocol implementation
│
└─ tests/                  # Test suite
   ├─ __init__.py
   ├─ test_protocol.py
   ├─ test_server.py
   └─ test_accountmanager.py
```
