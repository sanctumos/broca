"""Core message handling for Telegram bot."""
from typing import Dict, Any, Optional
from datetime import datetime
from runtime.core.message import MessageFormatter
from database.operations.users import get_or_create_platform_profile
from database.operations.messages import insert_message, update_message_status
from database.operations.queue import add_to_queue

class TelegramMessageHandler:
    """Handles core message processing for Telegram bot."""
    
    def __init__(self):
        """Initialize the message handler."""
        self.formatter = MessageFormatter()
    
    async def process_incoming_message(
        self,
        message: str,
        user_id: int,
        username: Optional[str],
        first_name: Optional[str],
        timestamp: datetime
    ) -> Dict[str, Any]:
        """Process an incoming message.
        
        Args:
            message: The message text
            user_id: The Telegram user ID
            username: The user's username
            first_name: The user's first name
            timestamp: The message timestamp
            
        Returns:
            Dict containing processing results
        """
        # Sanitize inputs
        message = self.formatter.sanitize_text(message)
        sender_first_name = self.formatter.sanitize_text(first_name) if first_name else "Unknown"
        sender_username = self.formatter.sanitize_text(username) if username else None
        
        # Get or create user profile
        profile, letta_user = await get_or_create_platform_profile(
            platform="telegram",
            platform_user_id=str(user_id),
            username=sender_username,
            display_name=sender_first_name
        )
        
        # Insert message
        message_id = await insert_message(
            letta_user_id=letta_user.id,
            platform_profile_id=profile.id,
            role="user",
            message=message,
            timestamp=timestamp.strftime("%Y-%m-%d %H:%M UTC")
        )
        
        # Add to queue
        await add_to_queue(letta_user.id, message_id)
        
        return {
            "message_id": message_id,
            "letta_user_id": letta_user.id,
            "platform_profile_id": profile.id
        }
    
    async def process_outgoing_message(
        self,
        message_id: int,
        message: str,
        status: str = "sent"
    ) -> None:
        """Process an outgoing message.
        
        Args:
            message_id: The message ID
            message: The message text
            status: The message status
        """
        await update_message_status(message_id, status)
    
    def format_message(self, message: str) -> str:
        """Format a message for sending.
        
        Args:
            message: The message text
            
        Returns:
            Formatted message text
        """
        return self.formatter.format_message(message) 