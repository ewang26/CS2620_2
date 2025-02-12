from typing import Dict, Optional, List, Tuple
import base64
import re
from ..common.security import Security
from ..common.user import User, Message

class AccountManager:
    def __init__(self):
        self.accounts: Dict[int, User] = {}  # user id -> User
        self.login_info: Dict[int, Tuple[bytes, bytes]] = {}  # user id -> (password hash, salt)
        self.next_user_id = 0

    def get_state(self):
        """Save the account manager state to a file."""
        state = {}
        for user_id, user in self.accounts.items():
            password_hash, salt = self.login_info[user_id]
            state[str(user_id)] = {
                "name": user.name,
                "password_hash": base64.b64encode(password_hash).decode('ascii'),
                "salt": base64.b64encode(salt).decode('ascii'),
                "message_queue": [(m.id, m.sender, m.content) for m in user.message_queue],
                "read_mailbox": [(m.id, m.sender, m.content) for m in user.read_mailbox]
            }
        state["next_user_id"] = self.next_user_id
        return state

    def load_state(self, state: Dict):
        """Load the account manager state from a file."""
        self.accounts.clear()
        self.login_info.clear()

        self.next_user_id = state["next_user_id"]
        state.pop("next_user_id")

        for user_id_str, user_state in state.items():
            user_id = int(user_id_str)
            password_hash = base64.b64decode(user_state["password_hash"].encode('ascii'))
            salt = base64.b64decode(user_state["salt"].encode('ascii'))
            messages = [Message(*m) for m in user_state["message_queue"]]
            received_messages = [Message(*m) for m in user_state["read_mailbox"]]
            user = User(user_id, user_state["name"], messages, received_messages)
            self.accounts[user_id] = user
            self.login_info[user_id] = (password_hash, salt)

    def get_user(self, user_id: int) -> Optional[User]:
        """Get a user by id."""
        return self.accounts.get(user_id)

    def create_account(self, username: str, password: str) -> Optional[str]:
        """Create a new account. Return True if successful."""

        # Check if the username is already taken
        for user in self.accounts.values():
            if user.name == username:
                return "Username already taken"

        # New user exists, create the account
        user_id = self.next_user_id
        new_user = User(user_id, username, [], [])
        self.next_user_id += 1

        # Store new user
        password_hash, salt = Security.hash_password(password)
        self.login_info[user_id] = (password_hash, salt)
        self.accounts[user_id] = new_user

        return None

    def login(self, username: str, password: str) -> Optional[User]:
        """Attempt to log in. Return True if successful."""

        # Find the corresponding user
        user_id = None
        for id, user in self.accounts.items():
            if user.name == username:
                user_id = id
                break

        if user_id is None:
            return None

        # Verify password
        password_hash, salt = self.login_info[user_id]
        if Security.verify_password(password, password_hash, salt):
            return self.accounts[user_id]
        return None

    def list_accounts(self, pattern: str) -> List[User]:
        """List accounts matching the pattern."""
        regex = re.compile(pattern.replace('*', '.*'))
        return [user for user in self.accounts.values() if regex.match(user.name)]

    def delete_account(self, user_id: int):
        """Delete an account."""
        self.accounts.pop(user_id)
        self.login_info.pop(user_id)

    def get_user_id_by_username(self, username):
        """Get a user's ID from their username."""
        for user_id, user_data in self.accounts.items():
            if user_data['username'] == username:
                return user_id
        return None
