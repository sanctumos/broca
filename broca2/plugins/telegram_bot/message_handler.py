"""Message handler for the Telegram bot plugin."""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from runtime.core.message import MessageFormatter
from database.operations.users import get_or_create_platform_profile
from database.operations.messages import insert_message, update_message_status
from database.operations.queue import add_to_queue

logger = logging.getLogger(__name__)

class TelegramMessageHandler:
    """Handles incoming and outgoing messages for the Telegram bot."""

    def __init__(self):
        """Initialize the message handler."""
        self.formatter = MessageFormatter()
        self.letta_client = None  # Initialize lazily
        logger.info("Initialized MessageHandler")
    
    async def process_incoming_message(self, message) -> Dict[str, Any]:
        """Process an incoming message.
        
        Args:
            message: The incoming message
            
        Returns:
            dict: Message processing result
        """
        try:
            # Extract message data
            user_id = message.from_user.id
            username = message.from_user.username
            first_name = message.from_user.first_name
            timestamp = message.date

            # Sanitize inputs
            message = self.formatter.sanitize_text(message.text)
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
                "platform_profile_id": profile.id,
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "timestamp": timestamp
            }
        except Exception as e:
            logger.error(f"Error processing incoming message: {e}")
            raise
    
    async def process_outgoing_message(self, message, response: str) -> None:
        """Process an outgoing message.
        
        Args:
            message: The original message
            response: The response to send
        """
        try:
            # Send response
            await message.answer(response)

            # Update message status
            await self.update_message_status(message, "sent")
        except Exception as e:
            logger.error(f"Error processing outgoing message: {e}")
            raise

    async def update_message_status(self, message, status: str) -> None:
        """Update the status of a message.
        
        Args:
            message: The message to update
            status: The new status
        """
        try:
            # Initialize letta_client lazily if needed
            if self.letta_client is None:
                from runtime.core.letta_client import LettaClient
                self.letta_client = LettaClient()
            
            # Update message status in database
            await self.letta_client.update_message_status(
                message_id=message.message_id,
                status=status
            )
        except ImportError as e:
            logger.error(f"letta_client not available: {e}")
            raise
        except Exception as e:
            logger.error(f"Error updating message status: {e}")
            raise

    async def handle_private_message(self, message) -> None:
        """Handle a private message.
        
        Args:
            message: The message to handle
        """
        await self.process_incoming_message(message)

    async def handle_group_message(self, message) -> None:
        """Handle a group message.
        
        Args:
            message: The message to handle
        """
        await message.answer("Group messages are not supported")

    async def handle_channel_message(self, message) -> None:
        """Handle a channel message.
        
        Args:
            message: The message to handle
        """
        await message.answer("Channel messages are not supported")
    
    def format_message(self, message: str) -> str:
        """Format a message for sending.
        
        Args:
            message: The message text
            
        Returns:
            Formatted message text
        """
        return self.formatter.format_message(message) 