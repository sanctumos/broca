"""Telegram message handler implementation."""
import asyncio
import re
from typing import Dict, Any, Tuple
from telethon import events
from datetime import datetime

from runtime.core.message import Message, MessageHandler, MessageFormatter as BaseMessageFormatter
from database.operations.users import get_or_create_platform_profile
from database.operations.messages import insert_message
from database.operations.queue import add_to_queue
from plugins.telegram.settings import TelegramSettings, MessageMode

class MessageFormatter(BaseMessageFormatter):
    """Telegram-specific message formatter."""
    
    def format_response(self, response: str) -> str:
        """Format a response for Telegram with markdown support.
        
        This method preserves markdown formatting from Letta/Broca responses
        while ensuring compatibility with Telegram's MarkdownV2 format.
        
        Args:
            response: The response to format
            
        Returns:
            str: The formatted response with preserved markdown
        """
        return self.preserve_markdown(response)
    
    def preserve_markdown(self, text: str) -> str:
        """Preserve markdown formatting while ensuring Telegram compatibility.
        
        Args:
            text: The text to format
            
        Returns:
            str: Text with preserved markdown formatting
        """
        if not text:
            return text
            
        # Simple, direct approach - just preserve the original formatting
        # Don't over-process or convert unnecessarily
        
        # Only handle the specific cases that Telegram has trouble with
        # Convert _italic_ to __italic__ (Telegram uses double underscores)
        # Remove word boundary requirement - it's too restrictive
        text = re.sub(r'_([^_]+)_', r'__\1__', text)
        
        # Convert *italic* to __italic__ (standardize to Telegram format)
        # But be careful not to break **bold** - only convert single asterisks
        # First protect bold patterns
        text = re.sub(r'\*\*([^*]+)\*\*', r'<BOLD>\1</BOLD>', text)
        # Then convert remaining single asterisks
        text = re.sub(r'\*([^*]+)\*', r'__\1__', text)
        # Finally restore bold patterns
        text = re.sub(r'<BOLD>([^<]+)</BOLD>', r'**\1**', text)
        
        # Handle non-standard code block delimiters
        # Convert ..code.. to ```code```
        text = re.sub(r'\.\.\n(.*?)\.\.', r'```\n\1\n```', text, flags=re.DOTALL)
        
        # Handle quote blocks - convert to italic prefix (more subtle)
        text = re.sub(r'^>\s*(.*?)$', r'*Quote:* \1', text, flags=re.MULTILINE)
        
        # That's it - preserve everything else as-is
        return text.strip()

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
            message: The message content
            timestamp: The message timestamp
        """
        buffer_key = (platform_user_id, letta_user_id, platform_profile_id)
        
        if buffer_key not in self.buffers:
            self.buffers[buffer_key] = {
                "messages": [],
                "flush_task": None
            }
        
        # Add message to buffer
        self.buffers[buffer_key]["messages"].append({
            "message": message,
            "timestamp": timestamp
        })
        
        # Schedule or reschedule flush
        if self.buffers[buffer_key]["flush_task"]:
            self.buffers[buffer_key]["flush_task"].cancel()
        
        self.buffers[buffer_key]["flush_task"] = asyncio.create_task(
            self._schedule_flush(buffer_key)
        )
    
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
        """Flush the buffer for a specific user.
        
        Args:
            buffer_key: Tuple of (platform_user_id, letta_user_id, platform_profile_id)
        """
        if buffer_key not in self.buffers:
            return
            
        platform_user_id, letta_user_id, platform_profile_id = buffer_key
        buffer = self.buffers[buffer_key]
        
        try:
            # Process each message in the buffer
            for msg in buffer["messages"]:
                # Insert message into database
                message_id = await insert_message(
                    letta_user_id=letta_user_id,
                    platform_profile_id=platform_profile_id,
                    role="user",
                    message=msg["message"],
                    timestamp=msg["timestamp"].isoformat()
                )
                
                # Add to processing queue
                await add_to_queue(
                    message_id=message_id,
                    letta_user_id=letta_user_id
                )
                
            print(f"Flushed {len(buffer['messages'])} messages for user {platform_user_id}")
            
        except Exception as e:
            print(f"Error flushing buffer for user {platform_user_id}: {str(e)}")
            
        finally:
            # Clear the buffer
            buffer["messages"].clear()
            buffer["flush_task"] = None

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