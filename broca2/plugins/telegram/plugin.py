"""Telegram bot plugin."""
import logging
import os
from typing import Optional, Callable, Any
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from dotenv import load_dotenv, set_key

from common.config import get_env_var

logger = logging.getLogger(__name__)

class TelegramBot:
    """Telegram bot using Telethon client."""
    
    def __init__(self):
        """Initialize the Telegram bot."""
        self.api_id = get_env_var("TELEGRAM_API_ID")
        self.api_hash = get_env_var("TELEGRAM_API_HASH")
        self.session_string = get_env_var("TELEGRAM_SESSION_STRING", default="")
        
        # Initialize client
        self.client = TelegramClient(
            StringSession(self.session_string),
            self.api_id,
            self.api_hash
        )
    
    def add_event_handler(self, callback: Callable, event: events.NewMessage) -> None:
        """Add an event handler to the client.
        
        Args:
            callback: The callback function to handle the event
            event: The event to handle
        """
        if self.client:
            self.client.add_event_handler(callback, event)
    
    async def start(self) -> None:
        """Start the Telegram client."""
        if not self.client:
            logger.error("❌ Telegram client not initialized")
            return
        
        try:
            logger.info("🔄 Starting Telegram client...")
            await self.client.start()
            
            if not await self.client.is_user_authorized():
                logger.error("❌ Telegram client not authorized")
                return
            
            # Save the session string if it's different from what we have
            new_session_string = self.client.session.save()
            if new_session_string != self.session_string:
                logger.info("💾 Saving new Telegram session string...")
                env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
                set_key(env_path, "TELEGRAM_SESSION_STRING", new_session_string)
                self.session_string = new_session_string
            
            logger.info("✅ Telegram client started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Telegram client: {str(e)}")
            raise
    
    async def stop(self) -> None:
        """Stop the Telegram client."""
        if self.client:
            await self.client.disconnect()
