"""Telegram message handlers and event processing."""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from runtime.core.message import MessageFormatter
from database.operations.users import get_or_create_platform_profile
from database.operations.messages import insert_message
from database.operations.queue import add_to_queue

logger = logging.getLogger(__name__)

class MessageBuffer:
    """Buffers messages before sending them to the queue."""
    
    def __init__(self, delay: int = 5):
        """Initialize the message buffer.
        
        Args:
            delay: Delay in seconds before flushing messages
        """
        self.delay = delay
        self.messages: List[Dict[str, Any]] = []
        self.letta_client = None  # Initialize lazily
        logger.info(f"Message buffer initialized with {delay}s delay")
    
    async def add_message(self, message: Dict[str, Any]) -> None:
        """Add a message to the buffer.
        
        Args:
            message: The message to add
        """
        self.messages.append(message)
        if len(self.messages) == 1:
            # Start flush timer for first message
            asyncio.create_task(self._delayed_flush())
    
    async def _delayed_flush(self) -> None:
        """Flush messages after delay."""
        await asyncio.sleep(self.delay)
        await self.flush()
    
    async def flush(self) -> None:
        """Flush all buffered messages to the queue."""
        if not self.messages:
            return
        
        try:
            # Initialize letta_client lazily if needed
            if self.letta_client is None:
                from runtime.core.letta_client import LettaClient
                self.letta_client = LettaClient()
            
            # Add all messages to queue
            for message in self.messages:
                await self.letta_client.add_to_queue(
                    message=message["message"],
                    user_id=message["user_id"],
                    username=message["username"],
                    first_name=message["first_name"],
                    timestamp=message["timestamp"]
                )
        except ImportError as e:
            logger.error(f"letta_client not available: {e}")
            raise
        except Exception as e:
            logger.error(f"Error flushing messages: {e}")
            raise
        finally:
            self.clear()
    
    def clear(self) -> None:
        """Clear all buffered messages."""
        self.messages.clear()

class MessageHandler:
    """Handles message processing and buffering."""
    
    def __init__(self, buffer_delay: int = 5):
        """Initialize the message handler.
        
        Args:
            buffer_delay: Delay in seconds before flushing messages
        """
        self.buffer = MessageBuffer(delay=buffer_delay)
        self.letta_client = None  # Initialize lazily
    
    async def handle_message(self, message: Dict[str, Any]) -> None:
        """Handle a message.
        
        Args:
            message: The message to handle
        """
        await self.buffer.add_message(message)
    
    async def process_message(self, message: Dict[str, Any]) -> None:
        """Process a message immediately.
        
        Args:
            message: The message to process
        """
        try:
            # Initialize letta_client lazily if needed
            if self.letta_client is None:
                from runtime.core.letta_client import LettaClient
                self.letta_client = LettaClient()
            
            await self.letta_client.add_to_queue(
                message=message["message"],
                user_id=message["user_id"],
                username=message["username"],
                first_name=message["first_name"],
                timestamp=message["timestamp"]
            )
        except ImportError as e:
            logger.error(f"letta_client not available: {e}")
            raise
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise

    def set_message_mode(self, mode: str) -> None:
        """Set the message handling mode.
        
        Args:
            mode: The message mode ('echo', 'listen', or 'live')
        """
        if mode not in ['echo', 'listen', 'live']:
            raise ValueError(f"Invalid message mode: {mode}")
        self.message_mode = mode
        print(f"Message mode set to: {mode}")
    
    async def handle_private_message(self, event: Dict[str, Any]) -> None:
        """Handle a private message event.
        
        Args:
            event: The message event data
        """
        message = event["message"]
        user_id = event["user_id"]
        username = event["username"]
        first_name = event["first_name"]
        
        print(f"Received private message from {first_name} (@{username})")
        
        # Sanitize user input
        message = self.formatter.sanitize_text(message)
        sender_first_name = self.formatter.sanitize_text(first_name) if first_name else "Unknown"
        sender_username = self.formatter.sanitize_text(username) if username else None
        
        print(f"Sanitized message: {message[:50]}...")
        
        # Get or create Letta user and platform profile
        profile, letta_user = await get_or_create_platform_profile(
            platform="telegram",
            platform_user_id=str(user_id),
            username=sender_username,
            display_name=sender_first_name
        )
        print(f"Got profile for {sender_first_name} (@{sender_username})")
        
        # Always add message to buffer/queue regardless of mode
        await self.buffer.add_message(
            {
                "user_id": letta_user.id,
                "username": sender_username,
                "first_name": sender_first_name,
                "message": message,
                "timestamp": datetime.now()
            }
        )
        print(f"Message added to queue in {self.message_mode} mode") 