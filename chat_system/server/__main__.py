import sys
from .server import ChatServer
from ..common.config import load_config

def main():
    # Load config from file or use command line arguments
    if len(sys.argv) > 2:
        host = sys.argv[1]
        port = int(sys.argv[2])
        use_custom_protocol = len(sys.argv) > 3 and sys.argv[3] == "custom"
    else:
        config = load_config()
        host = config["host"]
        port = config["port"]
        use_custom_protocol = config["use_custom_protocol"]

    # Start server
    server = ChatServer(host, port, use_custom_protocol)
    server.start()

if __name__ == "__main__":
    main()
