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
