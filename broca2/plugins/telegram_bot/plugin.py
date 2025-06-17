"""Telegram bot plugin using aiogram."""
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.exceptions import TelegramAPIError

from runtime.core.plugin import Plugin
from runtime.core.message import MessageFormatter
from database.operations.users import get_or_create_platform_profile
from database.operations.messages import insert_message, update_message_status
from database.operations.queue import add_to_queue

from .settings import TelegramBotSettings, MessageMode
from .handlers import MessageHandler, MessageBuffer
from .message_handler import TelegramMessageHandler

logger = logging.getLogger(__name__)

class TelegramBotPlugin(Plugin):
    """Telegram bot plugin using aiogram."""
    
    def __init__(self):
        """Initialize the plugin."""
        super().__init__()
        self.settings = None
        self.bot = None
        self.dp = None
        self.message_handler = None
        self.message_buffer = None
        self.formatter = MessageFormatter()
        self._running = False
        self._owner_verified = False
        logger.info("TelegramBotPlugin initialized")
    
    def get_name(self) -> str:
        """Get the plugin name."""
        return "telegram_bot"
    
    def get_platform(self) -> str:
        """Get the platform name."""
        return "telegram"
    
    def get_message_handler(self) -> MessageHandler:
        """Get the message handler."""
        return self.message_handler
    
    async def _handle_response(self, message_id: int, response: str) -> None:
        """Handle a response message.
        
        Args:
            message_id: The message ID
            response: The response text
        """
        try:
            # Format the response
            formatted_response = self.formatter.format_message(response)
            
            # Get the message from the database
            message = await self._get_message(message_id)
            if not message:
                logger.error(f"Message {message_id} not found")
                return
            
            # Get the user's Telegram ID
            user_id = message.get("platform_user_id")
            if not user_id:
                logger.error(f"No platform_user_id found for message {message_id}")
                return
            
            # Send the response
            await self.bot.send_message(
                chat_id=user_id,
                text=formatted_response
            )
            
            # Update message status
            await update_message_status(message_id, "sent")
            logger.info(f"Response sent for message {message_id}")
            
        except TelegramAPIError as e:
            logger.error(f"Failed to send response for message {message_id}: {str(e)}")
            await update_message_status(message_id, "failed")
        except Exception as e:
            logger.error(f"Error handling response for message {message_id}: {str(e)}")
            await update_message_status(message_id, "failed")
    
    def get_settings(self) -> Dict[str, Any]:
        """Get the plugin settings."""
        return self.settings.to_dict() if self.settings else {}
    
    def validate_settings(self, settings: Dict[str, Any]) -> bool:
        """Validate the plugin settings.
        
        Args:
            settings: The settings to validate
            
        Returns:
            True if settings are valid, False otherwise
        """
        try:
            TelegramBotSettings.from_dict(settings)
            return True
        except Exception as e:
            logger.error(f"Invalid settings: {str(e)}")
            return False
    
    async def register_event_handler(self, event_type: str, handler: callable) -> None:
        """Register an event handler.
        
        Args:
            event_type: The event type
            handler: The handler function
        """
        if event_type == "message":
            self.message_handler = handler
            logger.info("Message event handler registered")
    
    async def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event.
        
        Args:
            event_type: The event type
            data: The event data
        """
        if event_type == "message" and self.message_handler:
            await self.message_handler(data)
            logger.info(f"Message event emitted: {data}")
    
    async def start(self) -> None:
        """Start the plugin."""
        try:
            # Load settings
            self.settings = TelegramBotSettings.from_env()
            if not self.settings:
                raise ValueError("Failed to load settings")
            
            # Initialize bot and dispatcher
            self.bot = Bot(token=self.settings.bot_token)
            self.dp = Dispatcher()
            
            # Initialize message handler and buffer
            self.message_handler = MessageHandler(self)
            self.message_buffer = MessageBuffer(delay=self.settings.buffer_delay)
            
            # Register command handlers
            self.dp.message.register(self._handle_start, Command(commands=["start"]))
            self.dp.message.register(self._handle_help, Command(commands=["help"]))
            self.dp.message.register(self._handle_message)
            
            # Start polling
            self._running = True
            await self.dp.start_polling(self.bot)
            logger.info("Telegram bot started")
            
        except Exception as e:
            logger.error(f"Failed to start plugin: {str(e)}")
            raise
    
    async def stop(self) -> None:
        """Stop the plugin."""
        try:
            self._running = False
            if self.bot:
                await self.bot.session.close()
            logger.info("Telegram bot stopped")
        except Exception as e:
            logger.error(f"Error stopping plugin: {str(e)}")
    
    async def _handle_start(self, message: Message) -> None:
        """Handle the /start command.
        
        Args:
            message: The message object
        """
        try:
            await message.answer(
                "Welcome! I'm your Telegram bot. "
                "Send me a message and I'll process it."
            )
            logger.info(f"Start command handled for user {message.from_user.id}")
        except Exception as e:
            logger.error(f"Error handling start command: {str(e)}")
    
    async def _handle_help(self, message: Message) -> None:
        """Handle the /help command.
        
        Args:
            message: The message object
        """
        try:
            await message.answer(
                "Available commands:\n"
                "/start - Start the bot\n"
                "/help - Show this help message"
            )
            logger.info(f"Help command handled for user {message.from_user.id}")
        except Exception as e:
            logger.error(f"Error handling help command: {str(e)}")
    
    async def _handle_message(self, message: Message) -> None:
        """Handle incoming messages.
        
        Args:
            message: The message object
        """
        try:
            # Check if message is from owner
            if not await self._verify_owner(message.from_user):
                logger.warning(f"Message from unauthorized user {message.from_user.id}")
                return
            
            # Process message
            event = {
                "message": message.text,
                "user_id": message.from_user.id,
                "username": message.from_user.username,
                "first_name": message.from_user.first_name,
                "timestamp": datetime.now()
            }
            
            await self.message_handler.handle_private_message(event)
            logger.info(f"Message handled for user {message.from_user.id}")
            
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
    
    async def _verify_owner(self, user: types.User) -> bool:
        """Verify if a user is the owner.
        
        Args:
            user: The user to verify
            
        Returns:
            True if user is owner, False otherwise
        """
        if not self.settings:
            return False
        
        # Check owner ID
        if self.settings.owner_id and str(user.id) == str(self.settings.owner_id):
            return True
        
        # Check owner username
        if self.settings.owner_username and user.username == self.settings.owner_username:
            return True
        
        return False 