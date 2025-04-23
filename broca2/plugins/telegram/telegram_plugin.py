"""Telegram bot plugin."""
import logging
import os
from typing import Dict, Any, Optional, Callable
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from dotenv import load_dotenv, set_key

from common.config import get_env_var
from plugins import Plugin, Event, EventType
from .settings import TelegramSettings, MessageMode

logger = logging.getLogger(__name__)

class TelegramPlugin(Plugin):
    """Telegram plugin using Telethon client."""
    
    def __init__(self):
        """Initialize the Telegram plugin."""
        self.settings = TelegramSettings.from_env()
        
        # Initialize client
        self.client = TelegramClient(
            StringSession(self.settings.session_string),
            self.settings.api_id,
            self.settings.api_hash
        )
        
        # Event handlers
        self._event_handlers: Dict[EventType, set[Callable[[Event], None]]] = {
            event_type: set() for event_type in EventType
        }
    
    def get_name(self) -> str:
        """Get the plugin's name."""
        return "telegram"
    
    def get_settings(self) -> Optional[Dict[str, Any]]:
        """Get the plugin's settings."""
        return self.settings.to_dict()
    
    def validate_settings(self, settings: Dict[str, Any]) -> bool:
        """Validate plugin settings."""
        try:
            TelegramSettings.from_dict(settings)
            return True
        except (KeyError, ValueError):
            return False
    
    def register_event_handler(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """Register an event handler."""
        self._event_handlers[event_type].add(handler)
    
    def emit_event(self, event: Event) -> None:
        """Emit an event to registered handlers."""
        handlers = self._event_handlers[event.type]
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in event handler for {event.type}: {e}")
    
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
            if self.settings.auto_save_session:
                new_session_string = self.client.session.save()
                if new_session_string != self.settings.session_string:
                    logger.info("💾 Saving new Telegram session string...")
                    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
                    set_key(env_path, "TELEGRAM_SESSION_STRING", new_session_string)
                    self.settings.session_string = new_session_string
            
            logger.info("✅ Telegram client started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Telegram client: {str(e)}")
            raise
    
    async def stop(self) -> None:
        """Stop the Telegram client."""
        if self.client:
            await self.client.disconnect()
    
    def add_message_handler(self, callback: Callable, event: events.NewMessage) -> None:
        """Add a message handler to the client.
        
        Args:
            callback: The callback function to handle the message
            event: The event to handle
        """
        if self.client:
            self.client.add_event_handler(callback, event)
    
    def set_message_mode(self, mode: MessageMode) -> None:
        """Set the message handling mode.
        
        Args:
            mode: The message mode
        """
        self.settings.message_mode = mode
        logger.info(f"🔵 Message processing mode changed to: {mode.name}") 