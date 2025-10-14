"""Comprehensive tests for plugins/telegram/telegram_plugin.py."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest

from plugins import Event, EventType
from plugins.telegram.telegram_plugin import TelegramPlugin


class TestTelegramPluginComprehensive:
    """Comprehensive tests for TelegramPlugin class."""

    def test_telegram_plugin_init(self):
        """Test TelegramPlugin initialization."""
        plugin = TelegramPlugin()

        assert plugin.settings is None
        assert plugin.formatter is None
        assert plugin.ignored_bots == {}
        assert plugin.client is None
        assert len(plugin._event_handlers) == len(EventType)
        for event_type in EventType:
            assert event_type in plugin._event_handlers
            assert isinstance(plugin._event_handlers[event_type], set)

    def test_get_ignore_list_path(self):
        """Test _get_ignore_list_path returns correct path."""
        plugin = TelegramPlugin()

        with patch("os.path.dirname") as mock_dirname, patch(
            "os.path.join"
        ) as mock_join:
            mock_dirname.side_effect = [
                "/path/to/plugins/telegram",
                "/path/to/plugins",
                "/path/to",
            ]
            mock_join.return_value = "/path/to/telegram_ignore_list.json"

            path = plugin._get_ignore_list_path()

            assert isinstance(path, Path)
            # Use pathlib.Path for cross-platform compatibility
            expected_path = Path("/path/to/telegram_ignore_list.json")
            assert path == expected_path

    def test_load_ignore_list_file_not_exists(self):
        """Test _load_ignore_list when file doesn't exist."""
        plugin = TelegramPlugin()

        with patch.object(plugin, "_get_ignore_list_path") as mock_path, patch(
            "pathlib.Path.exists", return_value=False
        ), patch("plugins.telegram.telegram_plugin.logger") as mock_logger:
            mock_path.return_value = Path("test.json")

            plugin._load_ignore_list()

            mock_logger.info.assert_called_once_with("No ignore list file found")
            assert plugin.ignored_bots == {}

    def test_load_ignore_list_file_exists_success(self):
        """Test _load_ignore_list when file exists and loads successfully."""
        plugin = TelegramPlugin()

        test_data = {"bot1": {"username": "testbot", "reason": "spam"}}

        with patch.object(plugin, "_get_ignore_list_path") as mock_path, patch(
            "pathlib.Path.exists", return_value=True
        ), patch("builtins.open", mock_open(read_data=json.dumps(test_data))), patch(
            "plugins.telegram.telegram_plugin.logger"
        ) as mock_logger:
            mock_path.return_value = Path("test.json")

            plugin._load_ignore_list()

            assert plugin.ignored_bots == test_data
            mock_logger.info.assert_called_once_with(
                f"Loaded {len(test_data)} ignored bots: {test_data}"
            )

    def test_load_ignore_list_json_decode_error(self):
        """Test _load_ignore_list handles JSON decode error."""
        plugin = TelegramPlugin()

        with patch.object(plugin, "_get_ignore_list_path") as mock_path, patch(
            "pathlib.Path.exists", return_value=True
        ), patch("builtins.open", mock_open(read_data="invalid json")), patch(
            "plugins.telegram.telegram_plugin.logger"
        ) as mock_logger:
            mock_path.return_value = Path("test.json")

            plugin._load_ignore_list()

            assert plugin.ignored_bots == {}
            mock_logger.error.assert_called_once_with(
                "Failed to parse ignore list file"
            )

    def test_reload_ignore_list(self):
        """Test reload_ignore_list calls _load_ignore_list."""
        plugin = TelegramPlugin()

        with patch.object(plugin, "_load_ignore_list") as mock_load, patch(
            "plugins.telegram.telegram_plugin.logger"
        ) as mock_logger:
            plugin.reload_ignore_list()

            mock_load.assert_called_once()
            mock_logger.debug.assert_called_once_with("Reloading ignore list...")

    def test_is_bot_ignored_by_id(self):
        """Test is_bot_ignored returns True when bot is ignored by ID."""
        plugin = TelegramPlugin()
        plugin.ignored_bots = {"123": {"username": "testbot", "reason": "spam"}}

        with patch.object(plugin, "reload_ignore_list"), patch(
            "plugins.telegram.telegram_plugin.logger"
        ) as mock_logger:
            result = plugin.is_bot_ignored("123", "testbot")

            assert result is True
            mock_logger.info.assert_called_with("Bot 123 (@testbot) is ignored by ID")

    def test_is_bot_ignored_by_username(self):
        """Test is_bot_ignored returns True when bot is ignored by username."""
        plugin = TelegramPlugin()
        plugin.ignored_bots = {"456": {"username": "testbot", "reason": "spam"}}

        with patch.object(plugin, "reload_ignore_list"), patch(
            "plugins.telegram.telegram_plugin.logger"
        ) as mock_logger:
            result = plugin.is_bot_ignored("789", "testbot")

            assert result is True
            mock_logger.info.assert_called_with(
                "Bot 789 (@testbot) is ignored by username"
            )

    def test_is_bot_ignored_by_username_with_at(self):
        """Test is_bot_ignored handles username with @ prefix."""
        plugin = TelegramPlugin()
        plugin.ignored_bots = {"456": {"username": "testbot", "reason": "spam"}}

        with patch.object(plugin, "reload_ignore_list"), patch(
            "plugins.telegram.telegram_plugin.logger"
        ) as mock_logger:
            result = plugin.is_bot_ignored("789", "@testbot")

            assert result is True
            mock_logger.info.assert_called_with(
                "Bot 789 (@testbot) is ignored by username"
            )

    def test_is_bot_ignored_by_username_case_insensitive(self):
        """Test is_bot_ignored handles username case insensitively."""
        plugin = TelegramPlugin()
        plugin.ignored_bots = {"456": {"username": "TestBot", "reason": "spam"}}

        with patch.object(plugin, "reload_ignore_list"), patch(
            "plugins.telegram.telegram_plugin.logger"
        ) as mock_logger:
            result = plugin.is_bot_ignored("789", "testbot")

            assert result is True
            mock_logger.info.assert_called_with(
                "Bot 789 (@testbot) is ignored by username"
            )

    def test_is_bot_ignored_not_ignored(self):
        """Test is_bot_ignored returns False when bot is not ignored."""
        plugin = TelegramPlugin()
        plugin.ignored_bots = {"456": {"username": "otherbot", "reason": "spam"}}

        with patch.object(plugin, "reload_ignore_list"), patch(
            "plugins.telegram.telegram_plugin.logger"
        ) as mock_logger:
            result = plugin.is_bot_ignored("789", "testbot")

            assert result is False
            mock_logger.debug.assert_called_with("Bot 789 (@testbot) is not ignored")

    def test_is_bot_ignored_no_username(self):
        """Test is_bot_ignored with no username provided."""
        plugin = TelegramPlugin()
        plugin.ignored_bots = {"456": {"username": "otherbot", "reason": "spam"}}

        with patch.object(plugin, "reload_ignore_list"), patch(
            "plugins.telegram.telegram_plugin.logger"
        ) as mock_logger:
            result = plugin.is_bot_ignored("789")

            assert result is False
            mock_logger.debug.assert_called_with("Bot 789 (@None) is not ignored")

    def test_get_name(self):
        """Test get_name returns correct name."""
        plugin = TelegramPlugin()
        assert plugin.get_name() == "telegram"

    def test_get_platform(self):
        """Test get_platform returns correct platform."""
        plugin = TelegramPlugin()
        assert plugin.get_platform() == "telegram"

    def test_get_message_handler(self):
        """Test get_message_handler returns _handle_response."""
        plugin = TelegramPlugin()
        handler = plugin.get_message_handler()
        assert handler == plugin._handle_response

    @pytest.mark.asyncio
    async def test_handle_response_success(self):
        """Test _handle_response sends message successfully."""
        plugin = TelegramPlugin()

        # Mock dependencies
        mock_profile = MagicMock()
        mock_profile.platform_user_id = "123456"
        mock_profile.username = "testuser"

        mock_formatter = MagicMock()
        mock_formatter.format_response.return_value = "Formatted response"
        plugin.formatter = mock_formatter

        mock_client = MagicMock()
        mock_client.action.return_value.__aenter__ = AsyncMock()
        mock_client.action.return_value.__aexit__ = AsyncMock()
        mock_client.send_message = AsyncMock()
        plugin.client = mock_client

        with patch(
            "database.operations.messages.update_message_status", new_callable=AsyncMock
        ) as mock_update:
            await plugin._handle_response("Test response", mock_profile, 1)

            mock_formatter.format_response.assert_called_once_with("Test response")
            mock_client.send_message.assert_called_once_with(
                123456, "Formatted response", parse_mode="markdown"
            )
            mock_update.assert_called_once_with(
                message_id=1, status="success", response="Formatted response"
            )

    @pytest.mark.asyncio
    async def test_handle_response_invalid_user_id(self):
        """Test _handle_response handles invalid user ID."""
        plugin = TelegramPlugin()

        mock_profile = MagicMock()
        mock_profile.platform_user_id = "invalid"
        mock_profile.username = "testuser"

        with patch(
            "database.operations.messages.update_message_status", new_callable=AsyncMock
        ) as mock_update, patch(
            "plugins.telegram.telegram_plugin.logger"
        ) as mock_logger:
            await plugin._handle_response("Test response", mock_profile, 1)

            mock_logger.error.assert_called_with(
                "Invalid Telegram user ID format: invalid"
            )
            mock_update.assert_called_once_with(
                message_id=1,
                status="failed",
                response="Invalid Telegram user ID format: invalid",
            )

    @pytest.mark.asyncio
    async def test_handle_response_markdown_fallback(self):
        """Test _handle_response falls back to plain text when markdown fails."""
        plugin = TelegramPlugin()

        mock_profile = MagicMock()
        mock_profile.platform_user_id = "123456"
        mock_profile.username = "testuser"

        mock_formatter = MagicMock()
        mock_formatter.format_response.return_value = "Formatted response"
        plugin.formatter = mock_formatter

        mock_client = MagicMock()
        mock_client.action.return_value.__aenter__ = AsyncMock()
        mock_client.action.return_value.__aexit__ = AsyncMock()
        mock_client.send_message = AsyncMock(
            side_effect=[Exception("Markdown error"), None]
        )
        plugin.client = mock_client

        with patch(
            "database.operations.messages.update_message_status", new_callable=AsyncMock
        ), patch("plugins.telegram.telegram_plugin.logger") as mock_logger:
            await plugin._handle_response("Test response", mock_profile, 1)

            assert mock_client.send_message.call_count == 2
            mock_client.send_message.assert_any_call(
                123456, "Formatted response", parse_mode="markdown"
            )
            mock_client.send_message.assert_any_call(123456, "Formatted response")
            mock_logger.warning.assert_called_with(
                "Markdown parsing failed, falling back to plain text: Markdown error"
            )

    @pytest.mark.asyncio
    async def test_handle_response_exception(self):
        """Test _handle_response handles exceptions."""
        plugin = TelegramPlugin()

        mock_profile = MagicMock()
        mock_profile.platform_user_id = "123456"
        mock_profile.username = "testuser"

        mock_client = MagicMock()
        mock_client.action.side_effect = Exception("Connection error")
        plugin.client = mock_client

        with patch(
            "database.operations.messages.update_message_status", new_callable=AsyncMock
        ) as mock_update, patch(
            "plugins.telegram.telegram_plugin.logger"
        ) as mock_logger:
            with pytest.raises(Exception, match="Connection error"):
                await plugin._handle_response("Test response", mock_profile, 1)

            mock_logger.error.assert_called_with(
                "Failed to send response to 123456: Connection error"
            )
            mock_update.assert_called_once_with(
                message_id=1,
                status="failed",
                response="Failed to send response to 123456: Connection error",
            )

    def test_get_settings_success(self):
        """Test get_settings returns settings successfully."""
        plugin = TelegramPlugin()

        mock_settings = MagicMock()
        mock_settings.to_dict.return_value = {"api_id": "123", "api_hash": "abc"}

        with patch("plugins.telegram.settings.TelegramSettings") as mock_settings_class:
            mock_settings_class.from_env.return_value = mock_settings

            result = plugin.get_settings()

            assert result == {"api_id": "123", "api_hash": "abc"}
            assert plugin.settings == mock_settings

    def test_get_settings_exception(self):
        """Test get_settings handles exceptions."""
        plugin = TelegramPlugin()

        with patch(
            "plugins.telegram.settings.TelegramSettings"
        ) as mock_settings_class, patch(
            "plugins.telegram.telegram_plugin.logger"
        ) as mock_logger:
            mock_settings_class.from_env.side_effect = Exception("Settings error")

            result = plugin.get_settings()

            assert result == {}
            mock_logger.warning.assert_called_with(
                "Could not load Telegram settings: Settings error"
            )

    def test_validate_settings_success(self):
        """Test validate_settings returns True for valid settings."""
        plugin = TelegramPlugin()

        with patch("plugins.telegram.settings.TelegramSettings") as mock_settings_class:
            mock_settings_class.from_dict.return_value = MagicMock()

            result = plugin.validate_settings({"api_id": "123", "api_hash": "abc"})

            assert result is True

    def test_validate_settings_failure(self):
        """Test validate_settings returns False for invalid settings."""
        plugin = TelegramPlugin()

        with patch("plugins.telegram.settings.TelegramSettings") as mock_settings_class:
            mock_settings_class.from_dict.side_effect = ValueError("Invalid settings")

            result = plugin.validate_settings({"invalid": "data"})

            assert result is False

    def test_register_event_handler(self):
        """Test register_event_handler adds handler."""
        plugin = TelegramPlugin()

        handler = MagicMock()
        plugin.register_event_handler(EventType.MESSAGE, handler)

        assert handler in plugin._event_handlers[EventType.MESSAGE]

    def test_emit_event_success(self):
        """Test emit_event calls handlers successfully."""
        plugin = TelegramPlugin()

        handler1 = MagicMock()
        handler2 = MagicMock()
        plugin._event_handlers[EventType.MESSAGE].add(handler1)
        plugin._event_handlers[EventType.MESSAGE].add(handler2)

        event = Event(type=EventType.MESSAGE, data={"test": "data"}, source="test")
        plugin.emit_event(event)

        handler1.assert_called_once_with(event)
        handler2.assert_called_once_with(event)

    def test_emit_event_handler_exception(self):
        """Test emit_event handles handler exceptions."""
        plugin = TelegramPlugin()

        handler1 = MagicMock(side_effect=Exception("Handler error"))
        handler2 = MagicMock()
        plugin._event_handlers[EventType.MESSAGE].add(handler1)
        plugin._event_handlers[EventType.MESSAGE].add(handler2)

        event = Event(type=EventType.MESSAGE, data={"test": "data"}, source="test")

        with patch("plugins.telegram.telegram_plugin.logger") as mock_logger:
            plugin.emit_event(event)

            handler1.assert_called_once_with(event)
            handler2.assert_called_once_with(event)
            mock_logger.error.assert_called_with(
                "Error in event handler for EventType.MESSAGE: Handler error"
            )

    @pytest.mark.asyncio
    async def test_start_no_settings(self):
        """Test start returns early when no settings."""
        plugin = TelegramPlugin()

        with patch.object(plugin, "get_settings", return_value=None), patch(
            "plugins.telegram.telegram_plugin.logger"
        ) as mock_logger:
            await plugin.start()

            mock_logger.warning.assert_called_with(
                "Telegram settings not configured - plugin will not start"
            )

    @pytest.mark.asyncio
    async def test_start_import_error(self):
        """Test start handles ImportError."""
        plugin = TelegramPlugin()

        mock_settings = MagicMock()
        mock_settings.session_string = "session"
        mock_settings.api_id = "123"
        mock_settings.api_hash = "abc"
        plugin.settings = mock_settings

        with patch.object(
            plugin, "get_settings", return_value={"api_id": "123"}
        ), patch(
            "telethon.TelegramClient", side_effect=ImportError("telethon not available")
        ), patch(
            "telethon.sessions.StringSession"
        ), patch(
            "plugins.telegram.telegram_plugin.logger"
        ) as mock_logger:
            with pytest.raises(ImportError, match="telethon not available"):
                await plugin.start()

            mock_logger.error.assert_called_with(
                "telethon not available: telethon not available"
            )

    @pytest.mark.asyncio
    async def test_start_client_not_authorized(self):
        """Test start handles unauthorized client."""
        plugin = TelegramPlugin()

        mock_settings = MagicMock()
        mock_settings.session_string = "session"
        mock_settings.api_id = "123"
        mock_settings.api_hash = "abc"
        plugin.settings = mock_settings

        mock_client = AsyncMock()
        mock_client.is_user_authorized.return_value = False
        plugin.client = mock_client

        with patch("plugins.telegram.telegram_plugin.logger") as mock_logger:
            await plugin.start()

            mock_logger.error.assert_called_with("❌ Telegram client not authorized")

    @pytest.mark.asyncio
    async def test_stop(self):
        """Test stop disconnects client."""
        plugin = TelegramPlugin()

        mock_client = AsyncMock()
        plugin.client = mock_client

        await plugin.stop()

        mock_client.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_no_client(self):
        """Test stop handles no client."""
        plugin = TelegramPlugin()
        plugin.client = None

        # Should not raise exception
        await plugin.stop()

    def test_add_message_handler(self):
        """Test add_message_handler adds handler to client."""
        plugin = TelegramPlugin()

        mock_client = MagicMock()
        plugin.client = mock_client

        callback = MagicMock()
        event = MagicMock()

        plugin.add_message_handler(callback, event)

        mock_client.add_event_handler.assert_called_once_with(callback, event)

    def test_add_message_handler_no_client(self):
        """Test add_message_handler handles no client."""
        plugin = TelegramPlugin()
        plugin.client = None

        callback = MagicMock()
        event = MagicMock()

        # Should not raise exception
        plugin.add_message_handler(callback, event)

    def test_set_message_mode_string(self):
        """Test set_message_mode with string mode."""
        plugin = TelegramPlugin()

        mock_settings = MagicMock()
        plugin.settings = mock_settings

        with patch("plugins.telegram.settings.MessageMode") as mock_mode_class, patch(
            "plugins.telegram.telegram_plugin.logger"
        ) as mock_logger:
            mock_mode_instance = MagicMock()
            mock_mode_instance.name = "ECHO"
            mock_mode_class.return_value = mock_mode_instance

            plugin.set_message_mode("echo")

            mock_mode_class.assert_called_once_with("echo")
            assert plugin.settings.message_mode == mock_mode_instance
            mock_logger.info.assert_called_with(
                "🔵 Message processing mode changed to: ECHO"
            )

    def test_set_message_mode_object(self):
        """Test set_message_mode with MessageMode object."""
        plugin = TelegramPlugin()

        mock_settings = MagicMock()
        plugin.settings = mock_settings

        mock_mode = MagicMock()
        mock_mode.name = "LIVE"

        with patch("plugins.telegram.telegram_plugin.logger") as mock_logger:
            plugin.set_message_mode(mock_mode)

            assert plugin.settings.message_mode == mock_mode
            mock_logger.info.assert_called_with(
                "🔵 Message processing mode changed to: LIVE"
            )
