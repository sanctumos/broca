"""
Telegram bot plugin.

Copyright (C) 2024 Sanctum OS

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""Telegram bot plugin."""
import asyncio
import json
import logging
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

from dotenv import set_key

from plugins import Event, EventType, Plugin

logger = logging.getLogger(__name__)


class TelegramPlugin(Plugin):
    """Telegram plugin using Telethon client."""

    def __init__(self):
        """Initialize the Telegram plugin."""
        self.settings = None  # Initialize lazily
        self.formatter = None  # Initialize lazily
        self.ignored_bots: dict[str, dict[str, str]] = {}

        # Initialize client lazily
        self.client = None

        # Event handlers
        self._event_handlers: dict[EventType, set[Callable[[Event], None]]] = {
            event_type: set() for event_type in EventType
        }

    def _get_ignore_list_path(self) -> Path:
        """Get the path to the ignore list file."""
        return Path(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "telegram_ignore_list.json",
            )
        )

    def _load_ignore_list(self) -> None:
        """Load the ignore list from file."""
        path = self._get_ignore_list_path()
        if not path.exists():
            logger.info("No ignore list file found")
            return

        try:
            with open(path) as f:
                self.ignored_bots = json.load(f)
            logger.info(
                f"Loaded {len(self.ignored_bots)} ignored bots: {self.ignored_bots}"
            )
        except json.JSONDecodeError:
            logger.error("Failed to parse ignore list file")
            self.ignored_bots = {}

    def reload_ignore_list(self) -> None:
        """Reload the ignore list from file."""
        logger.debug("Reloading ignore list...")
        self._load_ignore_list()

    def is_bot_ignored(self, bot_id: str, username: str | None = None) -> bool:
        """Check if a bot is in the ignore list.

        Args:
            bot_id: The bot ID to check
            username: Optional bot username to check

        Returns:
            bool: True if the bot is ignored, False otherwise
        """
        # Reload the ignore list to get any changes
        self.reload_ignore_list()

        # Check by ID
        if str(bot_id) in self.ignored_bots:
            logger.info(f"Bot {bot_id} (@{username}) is ignored by ID")
            return True

        # Check by username
        if username:
            # Remove @ if present and convert to lowercase
            username = username[1:] if username.startswith("@") else username
            username = username.lower()

            for data in self.ignored_bots.values():
                if data.get("username", "").lower() == username:
                    logger.info(f"Bot {bot_id} (@{username}) is ignored by username")
                    return True

        logger.debug(f"Bot {bot_id} (@{username}) is not ignored")
        return False

    def get_name(self) -> str:
        """Get the plugin's name."""
        return "telegram"

    def get_platform(self) -> str:
        """Get the platform name this plugin handles."""
        return "telegram"

    def get_message_handler(self) -> Callable:
        """Get the message handler for this platform."""
        return self._handle_response

    async def _handle_response(self, response: str, profile, message_id: int) -> None:
        """Handle sending a response to a Telegram user.

        Args:
            response: The response message to send
            profile: The platform profile of the recipient
            message_id: The ID of the message being responded to
        """
        try:
            # Debug logging
            logger.info(
                f"🔵 _handle_response called with response: {response[:50]}..., profile: {profile}, message_id: {message_id}"
            )

            # Import database operations lazily
            from database.operations.messages import update_message_status

            # Initialize formatter lazily if needed
            if self.formatter is None:
                from plugins.telegram.message_handler import MessageFormatter

                self.formatter = MessageFormatter()

            # Format response for Telegram
            formatted = self.formatter.format_response(response)

            # Convert platform_user_id to integer for Telegram
            try:
                telegram_user_id = int(profile.platform_user_id)
            except ValueError:
                logger.error(
                    f"Invalid Telegram user ID format: {profile.platform_user_id}"
                )
                await update_message_status(
                    message_id=message_id,
                    status="failed",
                    response=f"Invalid Telegram user ID format: {profile.platform_user_id}",
                )
                return

            # Send message with typing indicator and markdown support
            async with self.client.action(telegram_user_id, "typing"):
                try:
                    await self.client.send_message(
                        telegram_user_id, formatted, parse_mode="markdown"
                    )
                except Exception as markdown_error:
                    logger.warning(
                        f"Markdown parsing failed, falling back to plain text: {str(markdown_error)}"
                    )
                    # Fallback to plain text if markdown fails
                    await self.client.send_message(telegram_user_id, formatted)
                logger.info(
                    f"Response sent to user {profile.username} ({telegram_user_id})"
                )

                # Update message status to success
                await update_message_status(
                    message_id=message_id, status="success", response=formatted
                )

        except ImportError as e:
            logger.error(f"Database operations not available: {e}")
            raise
        except Exception as e:
            error_msg = (
                f"Failed to send response to {profile.platform_user_id}: {str(e)}"
            )
            logger.error(error_msg)
            # Update message status to failed
            try:
                from database.operations.messages import update_message_status

                await update_message_status(
                    message_id=message_id, status="failed", response=error_msg
                )
            except ImportError:
                logger.error(
                    "Could not update message status - database operations not available"
                )
            raise

    def get_settings(self) -> dict[str, Any] | None:
        """Get the plugin's settings."""
        if self.settings is None:
            try:
                from plugins.telegram.settings import TelegramSettings

                self.settings = TelegramSettings.from_env()
            except Exception as e:
                logger.warning(f"Could not load Telegram settings: {e}")
                # Return a minimal settings object
                return {}
        return self.settings.to_dict()

    def validate_settings(self, settings: dict[str, Any]) -> bool:
        """Validate plugin settings."""
        try:
            from plugins.telegram.settings import TelegramSettings

            TelegramSettings.from_dict(settings)
            return True
        except (KeyError, ValueError):
            return False

    def register_event_handler(
        self, event_type: EventType, handler: Callable[[Event], None]
    ) -> None:
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
        try:
            # Import telethon only when needed
            from telethon import TelegramClient, events
            from telethon.sessions import StringSession

            # Get settings (this will initialize them if needed)
            settings = self.get_settings()
            if not settings:
                logger.warning(
                    "Telegram settings not configured - plugin will not start"
                )
                return

            # Initialize client if not already done
            if not self.client:
                self.client = TelegramClient(
                    StringSession(self.settings.session_string),
                    self.settings.api_id,
                    self.settings.api_hash,
                )

            logger.info("🔄 Starting Telegram client...")
            await self.client.start()

            if not await self.client.is_user_authorized():
                logger.error("❌ Telegram client not authorized")
                return

            # Load ignore list
            self._load_ignore_list()

            # Register message handler for incoming messages
            @self.client.on(events.NewMessage(incoming=True))
            async def handle_new_message(event):
                """Handle incoming messages."""
                logger.info(f"🔍 DEBUG: Message handler called! Event: {event}")
                try:
                    # Skip ignored bots
                    if self.is_bot_ignored(
                        event.sender_id, getattr(event.sender, "username", None)
                    ):
                        logger.info(f"🔍 DEBUG: Skipping ignored bot: {event.sender_id}")
                        return

                    # Skip messages from self
                    if event.sender_id == await self.client.get_peer_id("me"):
                        logger.info(
                            f"🔍 DEBUG: Skipping message from self: {event.sender_id}"
                        )
                        return

                    # Get message details
                    message = event.message.text
                    user_id = event.sender_id

                    # Try to get user info from event.sender, or fetch it if needed
                    username = None
                    first_name = "Unknown"

                    if event.sender:
                        username = getattr(event.sender, "username", None)
                        first_name = getattr(event.sender, "first_name", "Unknown")
                    else:
                        # Fetch user info from Telegram API
                        try:
                            user = await self.client.get_entity(user_id)
                            username = getattr(user, "username", None)
                            first_name = getattr(user, "first_name", "Unknown")
                            logger.info(
                                f"🔍 Debug - Fetched user info: {first_name} (@{username})"
                            )
                        except Exception as e:
                            logger.warning(f"🔍 Debug - Could not fetch user info: {e}")

                    # Debug logging for user info
                    logger.info(f"🔍 Debug - event.sender: {event.sender}")
                    logger.info(f"🔍 Debug - event.sender_id: {event.sender_id}")
                    logger.info(
                        f"🔍 Debug - username: {username}, first_name: {first_name}"
                    )

                    logger.info(
                        f"📨 Received message from {first_name} (@{username}): {message[:50]}..."
                    )

                    # Import database operations lazily
                    from database.operations.messages import insert_message
                    from database.operations.queue import add_to_queue
                    from database.operations.users import get_or_create_platform_profile

                    # Get or create user profile
                    profile, letta_user = await get_or_create_platform_profile(
                        platform="telegram",
                        platform_user_id=str(user_id),
                        username=username,
                        display_name=first_name,
                    )

                    # Insert message into database
                    message_id = await insert_message(
                        letta_user_id=letta_user.id,
                        platform_profile_id=profile.id,
                        role="user",
                        message=message,
                        timestamp=event.date.strftime("%Y-%m-%d %H:%M UTC"),
                    )

                    # Add to processing queue
                    await add_to_queue(letta_user.id, message_id)

                    logger.info(f"✅ Message queued for processing: {message_id}")

                except Exception as e:
                    logger.error(f"❌ Error handling incoming message: {str(e)}")

            # Save the session string if it's different from what we have
            if self.settings.auto_save_session:
                new_session_string = self.client.session.save()
                if new_session_string != self.settings.session_string:
                    logger.info("💾 Saving new Telegram session string...")
                    env_path = os.path.join(
                        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                        ".env",
                    )
                    set_key(env_path, "TELEGRAM_SESSION_STRING", new_session_string)
                    self.settings.session_string = new_session_string

            logger.info("✅ Telegram client started successfully")

            # Test if client is properly connected
            try:
                me = await self.client.get_me()
                logger.info(f"🔍 DEBUG: Connected as: {me.first_name} (@{me.username})")
            except Exception as e:
                logger.error(f"🔍 DEBUG: Error getting client info: {e}")

            # Start the client event loop in the background
            logger.info("🔄 Starting Telegram event loop...")
            asyncio.create_task(self.client.run_until_disconnected())
            logger.info("✅ Telegram event loop started")

        except ImportError as e:
            logger.error(f"telethon not available: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to start Telegram client: {str(e)}")
            raise

    async def stop(self) -> None:
        """Stop the Telegram client."""
        if self.client:
            await self.client.disconnect()

    def add_message_handler(self, callback: Callable, event) -> None:
        """Add a message handler to the client.

        Args:
            callback: The callback function to handle the message
            event: The event to handle
        """
        if self.client:
            self.client.add_event_handler(callback, event)

    def set_message_mode(self, mode) -> None:
        """Set the message handling mode.

        Args:
            mode: The message mode
        """
        from plugins.telegram.settings import MessageMode

        if isinstance(mode, str):
            mode = MessageMode(mode)
        self.settings.message_mode = mode
        logger.info(f"🔵 Message processing mode changed to: {mode.name}")
