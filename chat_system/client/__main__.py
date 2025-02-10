import sys
from .client import ChatClient
from ..common.config import load_config

def main():
    # Load config from file or use command line arguments
    if len(sys.argv) > 2:
        host = sys.argv[1]
        port = int(sys.argv[2])
    else:
        config = load_config()
        host = config["host"]
        port = config["port"]

    # Start client
    client = ChatClient(host, port)
    client.start()

if __name__ == "__main__":
    main()
