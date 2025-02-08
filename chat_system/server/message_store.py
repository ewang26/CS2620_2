from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ChatMessage:
    sender: str
    content: str
    timestamp: datetime
    delivered: bool = False

class MessageStore:
    def __init__(self):
        # username -> list of pending messages
        self.pending_messages: Dict[str, List[ChatMessage]] = {}
        
    def store_message(self, recipient: str, message: ChatMessage) -> None:
        """Store a message for later delivery."""
        if recipient not in self.pending_messages:
            self.pending_messages[recipient] = []
        self.pending_messages[recipient].append(message)
    
    def get_pending_messages(self, username: str) -> List[ChatMessage]:
        """Get all pending messages for a user."""
        return self.pending_messages.get(username, [])
    
    def mark_delivered(self, username: str, message: ChatMessage) -> None:
        """Mark a message as delivered."""
        if username in self.pending_messages:
            if message in self.pending_messages[username]:
                message.delivered = True
                self.pending_messages[username].remove(message)
    
    def count_unread(self, username: str) -> int:
        """Count unread messages for a user."""
        return len(self.pending_messages.get(username, [])) 