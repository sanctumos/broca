"""Telegram bot plugin using aiogram."""
import logging
from typing import Dict, Any, Optional, Callable, Awaitable

from plugins.telegram_bot.settings import TelegramBotSettings, MessageMode
from plugins.telegram_bot.message_handler import TelegramMessageHandler
from plugins.telegram_bot.handlers import MessageHandler
from plugins import Plugin

logger = logging.getLogger(__name__)

class TelegramBotPluginWrapper(Plugin):
    """Wrapper for TelegramBotPlugin to make it compatible with auto-discovery."""
    
    def __init__(self):
        """Initialize the wrapper."""
        self._plugin = TelegramBotPlugin()
    
    def get_name(self) -> str:
        """Get the plugin name."""
        return self._plugin.get_name()
    
    def get_platform(self) -> str:
        """Get the platform name."""
        return self._plugin.get_platform()
    
    def get_message_handler(self):
        """Get the message handler."""
        return self._plugin.get_message_handler()
    
    def get_settings(self):
        """Get plugin settings."""
        return self._plugin.get_settings()
    
    def apply_settings(self, settings):
        """Apply settings to the plugin."""
        if hasattr(self._plugin, 'apply_settings'):
            self._plugin.apply_settings(settings)
        else:
            # Fallback for backward compatibility
            if hasattr(self._plugin, 'validate_settings'):
                self._plugin.validate_settings(settings)
    
    def validate_settings(self, settings):
        """Validate plugin settings."""
        if hasattr(self._plugin, 'validate_settings'):
            return self._plugin.validate_settings(settings)
        return True
    
    async def start(self):
        """Start the plugin."""
        await self._plugin.start()
    
    async def stop(self):
        """Stop the plugin."""
        await self._plugin.stop()
    
    def register_event_handler(self, event_type, handler):
        """Register an event handler."""
        if hasattr(self._plugin, 'register_event_handler'):
            self._plugin.register_event_handler(event_type, handler)
    
    def emit_event(self, event):
        """Emit an event."""
        if hasattr(self._plugin, 'emit_event'):
            self._plugin.emit_event(event)

class TelegramBotPlugin:
    """Telegram bot plugin using aiogram."""

    def __init__(self):
        """Initialize the plugin."""
        self.settings = None  # Initialize lazily
        self.bot = None
        self.dp = None
        self.message_handler = None  # Initialize lazily
        self.event_handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[None]]] = {}
        logger.info("Initialized TelegramBotPlugin")

    def get_name(self) -> str:
        """Get the plugin name.

        Returns:
            str: Plugin name
        """
        return "telegram_bot"

    def get_platform(self) -> str:
        """Get the platform name.

        Returns:
            str: Platform name
        """
        return "telegram_bot"

    def get_message_handler(self) -> MessageHandler:
        """Get the message handler.

        Returns:
            MessageHandler: Message handler instance
        """
        if self.message_handler is None:
            try:
                self.message_handler = TelegramMessageHandler()
            except Exception as e:
                logger.warning(f"Could not initialize TelegramMessageHandler: {e}")
                return None
        return self.message_handler

    def get_settings(self) -> TelegramBotSettings:
        """Get the plugin settings.

        Returns:
            TelegramBotSettings: Settings instance
        """
        if self.settings is None:
            try:
                self.settings = TelegramBotSettings.from_env()
            except Exception as e:
                logger.warning(f"Could not load Telegram bot settings: {e}")
                # Return a minimal settings object
                return TelegramBotSettings(
                    bot_token="",
                    owner_id=None,
                    owner_username=None
                )
        return self.settings

    def validate_settings(self, settings: TelegramBotSettings) -> bool:
        """Validate plugin settings.

        Args:
            settings: Settings to validate

        Returns:
            bool: True if settings are valid
        """
        try:
            if not settings.bot_token:
                return False
            if not settings.owner_id and not settings.owner_username:
                return False
            if settings.owner_id and settings.owner_username:
                return False
            return True
        except Exception as e:
            logger.error(f"Invalid settings: {e}")
            return False

    async def register_event_handler(self, event: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """Register an event handler.

        Args:
            event: Event name
            handler: Event handler function
        """
        self.event_handlers[event] = handler

    async def emit_event(self, event: str, data: Dict[str, Any]) -> None:
        """Emit an event.

        Args:
            event: Event name
            data: Event data
        """
        if event in self.event_handlers:
            await self.event_handlers[event](data)

    async def start(self) -> None:
        """Start the plugin."""
        try:
            # Import aiogram only when needed
            from aiogram import Bot, Dispatcher
            from aiogram.filters import Command
            
            # Get settings (this will initialize them if needed)
            settings = self.get_settings()
            
            # Check if we have valid settings
            if not settings.bot_token:
                logger.warning("Telegram bot token not configured - plugin will not start")
                return
            
            # Initialize bot and dispatcher
            self.bot = Bot(token=settings.bot_token)
            self.dp = Dispatcher()

            # Register command handlers
            self.dp.message.register(self._handle_start_command, Command(commands=["start"]))
            self.dp.message.register(self._handle_help_command, Command(commands=["help"]))
            self.dp.message.register(self._handle_message)

            # Start polling
            await self.dp.start_polling(self.bot)
            logger.info("Plugin started successfully")
        except ImportError as e:
            logger.error(f"aiogram not available: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to start plugin: {e}")
            raise

    async def stop(self) -> None:
        """Stop the plugin."""
        try:
            if self.bot:
                await self.bot.session.close()
            logger.info("Plugin stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping plugin: {e}")
            raise

    async def _handle_message(self, message) -> None:
        """Handle incoming messages.

        Args:
            message: The incoming message
        """
        try:
            # Check if message is from owner
            if not self._verify_owner(message.from_user.id, message.from_user.username):
                logger.warning(f"Message from unauthorized user {message.from_user.id}")
                return

            # Process message based on chat type
            if message.chat.type == "private":
                await self.message_handler.handle_private_message(message)
            elif message.chat.type == "group":
                await self.message_handler.handle_group_message(message)
            elif message.chat.type == "channel":
                await self.message_handler.handle_channel_message(message)
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            raise

    async def _handle_response(self, response: str, message) -> None:
        """Handle outgoing responses.

        Args:
            response: The response to send
            message: The original message
        """
        try:
            await self.message_handler.process_outgoing_message(message, response)
        except Exception as e:
            logger.error(f"Error handling response for message {response}: {e}")
            raise

    async def _handle_start_command(self, message) -> None:
        """Handle /start command.

        Args:
            message: The command message
        """
        await message.answer("Welcome! I'm your Telegram bot.")

    async def _handle_help_command(self, message) -> None:
        """Handle /help command.

        Args:
            message: The command message
        """
        help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
        """
        await message.answer(help_text)

    def _verify_owner(self, user_id: int, username: Optional[str]) -> bool:
        """Verify if a user is the owner.

        Args:
            user_id: The user's ID
            username: The user's username

        Returns:
            bool: True if user is the owner
        """
        if self.settings.owner_id and user_id == self.settings.owner_id:
            return True
        if self.settings.owner_username and username == self.settings.owner_username:
            return True
        return False 