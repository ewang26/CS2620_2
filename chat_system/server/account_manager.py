from typing import Dict, Optional, List, Set
import re
from ..common.security import Security

class AccountManager:
    def __init__(self):
        self.accounts: Dict[str, tuple[bytes, bytes]] = {}  # username -> (password_hash, salt)
        self.online_users: Set[str] = set()
        
    def create_account(self, username: str, password: str) -> bool:
        """Create a new account. Return True if successful."""
        if username in self.accounts:
            return False
        
        password_hash, salt = Security.hash_password(password)
        self.accounts[username] = (password_hash, salt)
        return True
    
    def login(self, username: str, password: str) -> bool:
        """Attempt to log in. Return True if successful."""
        if username not in self.accounts:
            return False
            
        password_hash, salt = self.accounts[username]
        if Security.verify_password(password, password_hash, salt):
            self.online_users.add(username)
            return True
        return False
    
    def logout(self, username: str) -> None:
        """Log out a user."""
        self.online_users.discard(username)
    
    def list_accounts(self, pattern: Optional[str] = None) -> List[str]:
        """List accounts matching the pattern."""
        if not pattern:
            return list(self.accounts.keys())
            
        regex = re.compile(pattern.replace('*', '.*'))
        return [username for username in self.accounts.keys() 
                if regex.match(username)]
    
    def is_online(self, username: str) -> bool:
        """Check if a user is online."""
        return username in self.online_users 