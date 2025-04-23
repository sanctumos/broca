"""Telegram message handler implementation."""
import asyncio
from typing import Dict, Any, Tuple
from telethon import events
from datetime import datetime

from runtime.core.message import Message, MessageHandler, MessageFormatter
from database.operations.users import get_or_create_platform_profile
from database.operations.messages import insert_message
from database.operations.queue import add_to_queue
from .settings import TelegramSettings, MessageMode

class MessageBuffer:
    """Buffers messages for batch processing."""
    
    def __init__(self, settings: TelegramSettings):
        """Initialize the message buffer.
        
        Args:
            settings: Telegram plugin settings
        """
        self.delay = settings.buffer_delay
        self.buffers: Dict[int, Dict[str, Any]] = {}
        self.formatter = MessageFormatter()
        print(f"Message buffer initialized with {self.delay}s delay")
    
    async def add_message(
        self,
        platform_user_id: int,
        letta_user_id: int,
        platform_profile_id: int,
        message: str,
        timestamp: datetime
    ) -> None:
        """Add a message to the buffer.
        
        Args:
            platform_user_id: The platform-specific user ID
            letta_user_id: The Letta user ID
            platform_profile_id: The platform profile ID
            message: The message text
            timestamp: The message timestamp
        """
        print(f"Adding message to buffer for user {platform_user_id}: {message[:50]}...")
        
        buffer_key = (platform_user_id, letta_user_id, platform_profile_id)
        if buffer_key not in self.buffers:
            self.buffers[buffer_key] = {
                "messages": [],
                "task": None
            }
            print(f"Created new buffer for user {platform_user_id}")
        
        self.buffers[buffer_key]["messages"].append((message, timestamp))
        
        # Cancel any existing flush task
        if self.buffers[buffer_key]["task"] is not None:
            self.buffers[buffer_key]["task"].cancel()
            print(f"Cancelled existing flush task for user {platform_user_id}")
        
        # Schedule a new flush
        self.buffers[buffer_key]["task"] = asyncio.create_task(
            self._schedule_flush(buffer_key)
        )
        print(f"Scheduled new flush task for user {platform_user_id}")
    
    async def _schedule_flush(self, buffer_key: Tuple[int, int, int]) -> None:
        """Schedule a flush for the specified user's buffer.
        
        Args:
            buffer_key: Tuple of (platform_user_id, letta_user_id, platform_profile_id)
        """
        try:
            platform_user_id = buffer_key[0]
            print(f"Waiting {self.delay}s before flushing messages for user {platform_user_id}")
            await asyncio.sleep(self.delay)
            if buffer_key in self.buffers and self.buffers[buffer_key]["messages"]:
                print(f"Flushing messages for user {platform_user_id}")
                await self._flush_buffer(buffer_key)
        except asyncio.CancelledError:
            print(f"Flush task cancelled for user {platform_user_id}")
            pass
    
    async def _flush_buffer(self, buffer_key: Tuple[int, int, int]) -> None:
        """Flush the message buffer for a user.
        
        Args:
            buffer_key: Tuple of (platform_user_id, letta_user_id, platform_profile_id)
        """
        platform_user_id, letta_user_id, platform_profile_id = buffer_key
        buffer = self.buffers.get(buffer_key)
        if not buffer or not buffer["messages"]:
            print(f"No messages to flush for user {platform_user_id}")
            return
        
        print(f"Flushing {len(buffer['messages'])} messages for user {platform_user_id}")
        
        # Get raw messages and combine them with newlines
        messages = [msg for msg, _ in buffer["messages"]]
        combined_text = "\n".join(messages)
        
        # Get timestamp of first message
        first_msg_date = buffer["messages"][0][1].strftime("%Y-%m-%d %H:%M UTC")
        
        print(f"Inserting message into database: {combined_text[:50]}...")
        
        # Insert message and add to queue
        message_id = await insert_message(
            letta_user_id=letta_user_id,
            platform_profile_id=platform_profile_id,
            role="user",
            message=combined_text,
            timestamp=first_msg_date
        )
        await add_to_queue(letta_user_id, message_id)
        
        print(f"Message {message_id} added to queue for user {platform_user_id}")
        
        # Clear the buffer
        self.buffers[buffer_key] = {
            "messages": [],
            "task": None
        }
        print(f"Buffer cleared for user {platform_user_id}")

class TelegramMessageHandler(MessageHandler):
    """Handles Telegram message events."""
    
    def __init__(self, settings: TelegramSettings):
        """Initialize the message handler.
        
        Args:
            settings: Telegram plugin settings
        """
        print("Initializing TelegramMessageHandler")
        self.formatter = MessageFormatter()
        self.buffer = MessageBuffer(settings)
        self.message_mode = settings.message_mode
    
    def set_message_mode(self, mode: MessageMode) -> None:
        """Set the message handling mode.
        
        Args:
            mode: The message mode
        """
        self.message_mode = mode
        print(f"Message mode set to: {mode.value}")
    
    async def handle_message(self, message: Message) -> None:
        """Handle an incoming message.
        
        Args:
            message: The message to handle
        """
        if not message.user_id:
            print("Ignoring message without user ID")
            return
        
        print(f"Received message from user {message.user_id}")
        
        # Get or create Letta user and platform profile
        profile, letta_user = await get_or_create_platform_profile(
            platform="telegram",
            platform_user_id=message.user_id,
            username=message.username,
            display_name=message.metadata.get("display_name", "Unknown") if message.metadata else "Unknown"
        )
        print(f"Got profile for user {message.user_id}")
        
        # Always add message to buffer/queue regardless of mode
        await self.buffer.add_message(
            platform_user_id=int(message.user_id),
            letta_user_id=letta_user.id,
            platform_profile_id=profile.id,
            message=message.content,
            timestamp=message.timestamp or datetime.now()
        )
        print(f"Message added to queue in {self.message_mode.value} mode")
    
    async def send_message(self, message: Message) -> None:
        """Send a message.
        
        Args:
            message: The message to send
        """
        # This will be implemented when we have the Telegram client available
        pass 