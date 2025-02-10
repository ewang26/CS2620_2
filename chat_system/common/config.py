import json
from typing import Dict, Any

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8888

def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load connection settings from config file."""
    try:
        with open(config_path) as f:
            print("Loading config from", config_path)
            return json.load(f)
    except FileNotFoundError:
        print("Config file not found, using default settings")
        return {"host": DEFAULT_HOST, "port": DEFAULT_PORT, "use_custom_protocol": True}
