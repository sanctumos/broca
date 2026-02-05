"""Telegram bot plugin using aiogram."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from plugins.base import BasePluginWrapper
from plugins.telegram_bot.message_handler import (
    MessageFormatter,
    TelegramMessageHandler,
)
from plugins.telegram_bot.settings import TelegramBotSettings

logger = logging.getLogger(__name__)


class TelegramBotPluginWrapper(BasePluginWrapper):
    """Wrapper for TelegramBotPlugin to make it compatible with auto-discovery."""

    def __init__(self):
        """Initialize the wrapper."""
        super().__init__(TelegramBotPlugin())


class TelegramBotPlugin:
    """Telegram bot plugin using aiogram."""

    def __init__(self):
        """Initialize the plugin."""
        self.settings = None  # Initialize lazily
        self.bot = None
        self.dp = None
        self.message_handler = None  # Initialize lazily
        self.polling_task = None
        self.response_formatter = MessageFormatter()
        self.event_handlers: dict[str, Callable[[dict[str, Any]], Awaitable[None]]] = {}
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
        return "telegram"

    def get_message_handler(self) -> Callable[[str, Any, int], Awaitable[None]]:
        """Get the message handler.

        Returns:
            Callable: Message handler coroutine
        """
        return self._handle_response

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
                    bot_token="", owner_id=None, owner_username=None
                )
        return self.settings

    def apply_settings(self, settings: dict | TelegramBotSettings) -> None:
        """Apply settings to the plugin.

        Args:
            settings: Settings as dict or TelegramBotSettings object
        """
        try:
            if isinstance(settings, TelegramBotSettings):
                # Already a TelegramBotSettings object, use directly
                self.settings = settings
            elif isinstance(settings, dict):
                if not settings or len(settings) == 0:
                    # Empty dict, load from environment
                    self.settings = TelegramBotSettings.from_env()
                else:
                    # Dict with values, convert to TelegramBotSettings
                    self.settings = TelegramBotSettings.from_dict(settings)
            else:
                # Invalid type, try to load from environment as fallback
                logger.warning(
                    f"Invalid settings type {type(settings)}, loading from environment"
                )
                self.settings = TelegramBotSettings.from_env()
        except Exception as e:
            logger.error(f"Failed to apply settings: {e}")
            # Fallback to environment if conversion fails
            try:
                self.settings = TelegramBotSettings.from_env()
            except Exception as env_error:
                logger.error(f"Failed to load settings from environment: {env_error}")
                raise

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

    async def register_event_handler(
        self, event: str, handler: Callable[[dict[str, Any]], Awaitable[None]]
    ) -> None:
        """Register an event handler.

        Args:
            event: Event name
            handler: Event handler function
        """
        self.event_handlers[event] = handler

    async def emit_event(self, event: str, data: dict[str, Any]) -> None:
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
                logger.warning(
                    "Telegram bot token not configured - plugin will not start"
                )
                return

            # Initialize message handler before polling
            self.message_handler = TelegramMessageHandler()

            # Initialize bot and dispatcher
            self.bot = Bot(token=settings.bot_token)
            self.dp = Dispatcher()

            # Register command handlers
            self.dp.message.register(
                self._handle_start_command, Command(commands=["start"])
            )
            self.dp.message.register(
                self._handle_help_command, Command(commands=["help"])
            )
            self.dp.message.register(self._handle_message)

            # Start polling in the background so startup can continue (retry on transient network errors)
            async def _run_polling() -> None:
                from aiogram.exceptions import TelegramNetworkError

                max_retries = 5
                retry_delay = 15
                attempt = 0
                while True:
                    try:
                        await self.dp.start_polling(self.bot)
                        logger.warning(
                            "Telegram polling stopped unexpectedly (no exception). "
                            "Check bot token and Telegram API access."
                        )
                        break
                    except asyncio.CancelledError:
                        raise
                    except TelegramNetworkError as e:
                        attempt += 1
                        if attempt >= max_retries:
                            logger.error(
                                "Telegram polling failed after %s attempts (last: %s). "
                                "Check bot token and network (api.telegram.org).",
                                max_retries,
                                e,
                                exc_info=True,
                            )
                            raise
                        logger.warning(
                            "Telegram network error (attempt %s/%s): %s. Retrying in %ss.",
                            attempt,
                            max_retries,
                            e,
                            retry_delay,
                        )
                        await asyncio.sleep(retry_delay)
                    except Exception as e:
                        logger.error(
                            "Telegram polling exited with error: %s. Check bot token and network.",
                            e,
                            exc_info=True,
                        )
                        raise

            self.polling_task = asyncio.create_task(_run_polling())
            logger.info("Plugin started successfully (polling task running)")
        except ImportError as e:
            logger.error(f"aiogram not available: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to start plugin: {e}")
            raise

    async def stop(self) -> None:
        """Stop the plugin."""
        try:
            if self.polling_task:
                self.polling_task.cancel()
                try:
                    await self.polling_task
                except asyncio.CancelledError:
                    pass
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
            # Check if message is from owner (only if require_owner is True)
            if self.settings.require_owner:
                if not self._verify_owner(
                    message.from_user.id, message.from_user.username
                ):
                    logger.warning(
                        f"Message from unauthorized user {message.from_user.id}"
                    )
                    return

            # Process incoming message and enqueue
            await self.message_handler.process_incoming_message(message)
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            raise

    async def _handle_response(
        self, response: str, profile: Any, message_id: int
    ) -> None:
        """Handle outgoing responses.

        Args:
            response: The response to send
            profile: Platform profile for the target user
            message_id: The original message ID
        """
        if not self.bot:
            logger.error("Telegram bot is not initialized; cannot send response")
            return

        try:
            chat_id = int(profile.platform_user_id)
        except (TypeError, ValueError):
            logger.error(
                f"Invalid Telegram platform_user_id for message {message_id}: "
                f"{profile.platform_user_id}"
            )
            return

        formatted = self.response_formatter.format_response(response)
        try:
            await self.bot.send_message(
                chat_id=chat_id, text=formatted, parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Error handling response for message {message_id}: {e}")
            if "can't parse entities" in str(e).lower():
                await self.bot.send_message(chat_id=chat_id, text=formatted)
                return
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

    def _verify_owner(self, user_id: int, username: str | None) -> bool:
        """Verify if a user is the owner.

        Args:
            user_id: The user's ID
            username: The user's username

        Returns:
            bool: True if user is the owner
        """
        if self.settings.owner_id and user_id == self.settings.owner_id:
            return True
        if self.settings.owner_username:
            if not username:
                logger.warning(
                    "Owner username configured but incoming message has no username"
                )
                return False
            normalized_owner = self.settings.owner_username.lstrip("@").lower()
            normalized_user = username.lstrip("@").lower()
            if normalized_user == normalized_owner:
                return True
        return False
