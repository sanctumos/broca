"""Tests for Telegram plugin."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest

from plugins import Event, EventType
from plugins.telegram.telegram_plugin import TelegramPlugin


class TestTelegramPlugin:
    """Test the TelegramPlugin class."""

    def test_init(self):
        """Test TelegramPlugin initialization."""
        plugin = TelegramPlugin()
        assert plugin.settings is None
        assert plugin.formatter is None
        assert plugin.ignored_bots == {}
        assert plugin.client is None
        assert len(plugin._event_handlers) == len(EventType)

    def test_get_ignore_list_path(self):
        """Test getting ignore list path."""
        plugin = TelegramPlugin()
        path = plugin._get_ignore_list_path()
        assert isinstance(path, Path)
        assert path.name == "telegram_ignore_list.json"

    def test_load_ignore_list_file_not_exists(self):
        """Test loading ignore list when file doesn't exist."""
        plugin = TelegramPlugin()

        with patch.object(plugin, "_get_ignore_list_path") as mock_path:
            mock_path.return_value = Path("/nonexistent/file.json")
            plugin._load_ignore_list()
            assert plugin.ignored_bots == {}

    def test_load_ignore_list_file_exists(self):
        """Test loading ignore list when file exists."""
        plugin = TelegramPlugin()

        test_data = {
            "123": {"username": "test_bot", "reason": "spam"},
            "456": {"username": "another_bot", "reason": "annoying"},
        }

        with patch.object(plugin, "_get_ignore_list_path") as mock_path, patch(
            "builtins.open", mock_open(read_data=json.dumps(test_data))
        ):
            mock_path.return_value = Path("/test/file.json")
            plugin._load_ignore_list()
            assert plugin.ignored_bots == test_data

    def test_load_ignore_list_invalid_json(self):
        """Test loading ignore list with invalid JSON."""
        plugin = TelegramPlugin()

        with patch.object(plugin, "_get_ignore_list_path") as mock_path, patch(
            "builtins.open", mock_open(read_data="invalid json")
        ):
            mock_path.return_value = Path("/test/file.json")
            plugin._load_ignore_list()
            assert plugin.ignored_bots == {}

    def test_reload_ignore_list(self):
        """Test reloading ignore list."""
        plugin = TelegramPlugin()

        with patch.object(plugin, "_load_ignore_list") as mock_load:
            plugin.reload_ignore_list()
            mock_load.assert_called_once()

    def test_is_bot_ignored_by_id(self):
        """Test checking if bot is ignored by ID."""
        plugin = TelegramPlugin()
        plugin.ignored_bots = {"123": {"username": "test_bot"}}

        with patch.object(plugin, "reload_ignore_list"):
            result = plugin.is_bot_ignored("123", "test_bot")
            assert result is True

    def test_is_bot_ignored_by_username(self):
        """Test checking if bot is ignored by username."""
        plugin = TelegramPlugin()
        plugin.ignored_bots = {
            "123": {"username": "test_bot"},
            "456": {"username": "another_bot"},
        }

        with patch.object(plugin, "reload_ignore_list"):
            result = plugin.is_bot_ignored("999", "test_bot")
            assert result is True

    def test_is_bot_ignored_by_username_with_at(self):
        """Test checking if bot is ignored by username with @ prefix."""
        plugin = TelegramPlugin()
        plugin.ignored_bots = {"123": {"username": "test_bot"}}

        with patch.object(plugin, "reload_ignore_list"):
            result = plugin.is_bot_ignored("999", "@test_bot")
            assert result is True

    def test_is_bot_ignored_case_insensitive(self):
        """Test checking if bot is ignored case insensitive."""
        plugin = TelegramPlugin()
        plugin.ignored_bots = {"123": {"username": "Test_Bot"}}

        with patch.object(plugin, "reload_ignore_list"):
            result = plugin.is_bot_ignored("999", "test_bot")
            assert result is True

    def test_is_bot_not_ignored(self):
        """Test checking if bot is not ignored."""
        plugin = TelegramPlugin()
        plugin.ignored_bots = {"123": {"username": "test_bot"}}

        with patch.object(plugin, "reload_ignore_list"):
            result = plugin.is_bot_ignored("999", "unknown_bot")
            assert result is False

    def test_is_bot_ignored_no_username(self):
        """Test checking if bot is ignored without username."""
        plugin = TelegramPlugin()
        plugin.ignored_bots = {"123": {"username": "test_bot"}}

        with patch.object(plugin, "reload_ignore_list"):
            result = plugin.is_bot_ignored("999", None)
            assert result is False

    def test_get_name(self):
        """Test getting plugin name."""
        plugin = TelegramPlugin()
        assert plugin.get_name() == "telegram"

    def test_get_platform(self):
        """Test getting platform name."""
        plugin = TelegramPlugin()
        assert plugin.get_platform() == "telegram"

    def test_get_message_handler(self):
        """Test getting message handler."""
        plugin = TelegramPlugin()
        handler = plugin.get_message_handler()
        assert handler == plugin._handle_response

    @pytest.mark.asyncio
    async def test_handle_response_success(self):
        """Test successful response handling."""
        plugin = TelegramPlugin()

        # Mock profile
        mock_profile = MagicMock()
        mock_profile.platform_user_id = "123"
        mock_profile.username = "test_user"

        # Mock client
        mock_client = MagicMock()
        mock_client.action = AsyncMock()
        mock_client.send_message = AsyncMock()
        plugin.client = mock_client

        # Mock formatter
        mock_formatter = MagicMock()
        mock_formatter.format_response.return_value = "Formatted response"
        plugin.formatter = mock_formatter

        with patch(
            "database.operations.messages.update_message_status", new_callable=AsyncMock
        ) as mock_update:
            await plugin._handle_response("Test response", mock_profile, 456)

            # Check formatter was called
            mock_formatter.format_response.assert_called_once_with("Test response")

            # Check client was called
            mock_client.send_message.assert_called_once_with(
                123, "Formatted response", parse_mode="markdown"
            )

            # Check status was updated
            mock_update.assert_called_once_with(
                message_id=456, status="success", response="Formatted response"
            )

    @pytest.mark.asyncio
    async def test_handle_response_markdown_fallback(self):
        """Test response handling with markdown fallback."""
        plugin = TelegramPlugin()

        # Mock profile
        mock_profile = MagicMock()
        mock_profile.platform_user_id = "123"
        mock_profile.username = "test_user"

        # Mock client
        mock_client = MagicMock()
        mock_client.action = AsyncMock()
        mock_client.send_message = AsyncMock(
            side_effect=[Exception("Markdown error"), None]
        )
        plugin.client = mock_client

        # Mock formatter
        mock_formatter = MagicMock()
        mock_formatter.format_response.return_value = "Formatted response"
        plugin.formatter = mock_formatter

        with patch(
            "database.operations.messages.update_message_status", new_callable=AsyncMock
        ) as mock_update:
            await plugin._handle_response("Test response", mock_profile, 456)

            # Check both markdown and plain text calls were made
            assert mock_client.send_message.call_count == 2
            mock_client.send_message.assert_any_call(
                123, "Formatted response", parse_mode="markdown"
            )
            mock_client.send_message.assert_any_call(123, "Formatted response")

            # Check status was updated
            mock_update.assert_called_once_with(
                message_id=456, status="success", response="Formatted response"
            )

    @pytest.mark.asyncio
    async def test_handle_response_invalid_user_id(self):
        """Test response handling with invalid user ID."""
        plugin = TelegramPlugin()

        # Mock profile with invalid user ID
        mock_profile = MagicMock()
        mock_profile.platform_user_id = "invalid"
        mock_profile.username = "test_user"

        with patch(
            "database.operations.messages.update_message_status", new_callable=AsyncMock
        ) as mock_update:
            await plugin._handle_response("Test response", mock_profile, 456)

            # Check status was updated to failed
            mock_update.assert_called_once_with(
                message_id=456,
                status="failed",
                response="Invalid Telegram user ID format: invalid",
            )

    @pytest.mark.asyncio
    async def test_handle_response_exception(self):
        """Test response handling with exception."""
        plugin = TelegramPlugin()

        # Mock profile
        mock_profile = MagicMock()
        mock_profile.platform_user_id = "123"

        # Mock client that raises exception
        mock_client = MagicMock()
        mock_client.action = AsyncMock()
        mock_client.send_message = AsyncMock(side_effect=Exception("Send failed"))
        plugin.client = mock_client

        # Mock formatter
        mock_formatter = MagicMock()
        mock_formatter.format_response.return_value = "Formatted response"
        plugin.formatter = mock_formatter

        with patch(
            "database.operations.messages.update_message_status", new_callable=AsyncMock
        ) as mock_update:
            with pytest.raises(Exception, match="Send failed"):
                await plugin._handle_response("Test response", mock_profile, 456)

            # Check status was updated to failed
            mock_update.assert_called_once_with(
                message_id=456,
                status="failed",
                response="Failed to send response to 123: Send failed",
            )

    def test_get_settings_success(self):
        """Test getting settings successfully."""
        plugin = TelegramPlugin()

        mock_settings = MagicMock()
        mock_settings.to_dict.return_value = {"api_id": "123", "api_hash": "abc"}

        with patch("plugins.telegram.settings.TelegramSettings") as mock_settings_class:
            mock_settings_class.from_env.return_value = mock_settings
            result = plugin.get_settings()

            assert result == {"api_id": "123", "api_hash": "abc"}
            assert plugin.settings == mock_settings

    def test_get_settings_exception(self):
        """Test getting settings with exception."""
        plugin = TelegramPlugin()

        with patch("plugins.telegram.settings.TelegramSettings") as mock_settings_class:
            mock_settings_class.from_env.side_effect = Exception("Settings error")
            result = plugin.get_settings()

            assert result == {}

    def test_validate_settings_valid(self):
        """Test validating valid settings."""
        plugin = TelegramPlugin()

        with patch("plugins.telegram.settings.TelegramSettings") as mock_settings_class:
            mock_settings_class.from_dict.return_value = MagicMock()
            result = plugin.validate_settings({"api_id": "123"})

            assert result is True

    def test_validate_settings_invalid(self):
        """Test validating invalid settings."""
        plugin = TelegramPlugin()

        with patch("plugins.telegram.settings.TelegramSettings") as mock_settings_class:
            mock_settings_class.from_dict.side_effect = ValueError("Invalid settings")
            result = plugin.validate_settings({"invalid": "data"})

            assert result is False

    def test_register_event_handler(self):
        """Test registering event handler."""
        plugin = TelegramPlugin()

        def test_handler(event):
            pass

        plugin.register_event_handler(EventType.MESSAGE_RECEIVED, test_handler)

        assert test_handler in plugin._event_handlers[EventType.MESSAGE_RECEIVED]

    def test_emit_event_success(self):
        """Test emitting event successfully."""
        plugin = TelegramPlugin()

        def test_handler(event):
            test_handler.called = True

        plugin.register_event_handler(EventType.MESSAGE_RECEIVED, test_handler)

        event = Event(type=EventType.MESSAGE_RECEIVED, data={"test": "data"})
        plugin.emit_event(event)

        assert test_handler.called is True

    def test_emit_event_handler_exception(self):
        """Test emitting event with handler exception."""
        plugin = TelegramPlugin()

        def failing_handler(event):
            raise Exception("Handler error")

        def working_handler(event):
            working_handler.called = True

        plugin.register_event_handler(EventType.MESSAGE_RECEIVED, failing_handler)
        plugin.register_event_handler(EventType.MESSAGE_RECEIVED, working_handler)

        event = Event(type=EventType.MESSAGE_RECEIVED, data={"test": "data"})

        # Should not raise exception
        plugin.emit_event(event)

        assert working_handler.called is True

    @pytest.mark.asyncio
    async def test_start_no_settings(self):
        """Test starting with no settings."""
        plugin = TelegramPlugin()

        with patch.object(plugin, "get_settings", return_value=None):
            await plugin.start()

            # Should return early without starting client
            assert plugin.client is None

    @pytest.mark.asyncio
    async def test_start_success(self):
        """Test successful start."""
        plugin = TelegramPlugin()

        # Mock settings
        mock_settings = MagicMock()
        mock_settings.session_string = "test_session"
        mock_settings.api_id = "123"
        mock_settings.api_hash = "abc"
        mock_settings.auto_save_session = False

        # Mock client
        mock_client = MagicMock()
        mock_client.start = AsyncMock()
        mock_client.is_user_authorized = AsyncMock(return_value=True)
        mock_client.get_me = AsyncMock(
            return_value=MagicMock(first_name="Test", username="test_user")
        )
        mock_client.run_until_disconnected = AsyncMock()

        with patch.object(
            plugin, "get_settings", return_value={"test": "settings"}
        ), patch("telethon.TelegramClient", return_value=mock_client), patch.object(
            plugin, "_load_ignore_list"
        ), patch(
            "asyncio.create_task"
        ):
            plugin.settings = mock_settings
            await plugin.start()

            # Check client was started
            mock_client.start.assert_called_once()
            mock_client.is_user_authorized.assert_called_once()
            assert plugin.client == mock_client

    @pytest.mark.asyncio
    async def test_start_not_authorized(self):
        """Test starting when not authorized."""
        plugin = TelegramPlugin()

        # Mock settings
        mock_settings = MagicMock()
        mock_settings.session_string = "test_session"
        mock_settings.api_id = "123"
        mock_settings.api_hash = "abc"

        # Mock client
        mock_client = MagicMock()
        mock_client.start = AsyncMock()
        mock_client.is_user_authorized = AsyncMock(return_value=False)

        with patch.object(
            plugin, "get_settings", return_value={"test": "settings"}
        ), patch("telethon.TelegramClient", return_value=mock_client):
            plugin.settings = mock_settings
            await plugin.start()

            # Should return early when not authorized
            mock_client.start.assert_called_once()
            mock_client.is_user_authorized.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop(self):
        """Test stopping the plugin."""
        plugin = TelegramPlugin()

        # Mock client
        mock_client = MagicMock()
        mock_client.disconnect = AsyncMock()
        plugin.client = mock_client

        await plugin.stop()

        mock_client.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_no_client(self):
        """Test stopping when no client exists."""
        plugin = TelegramPlugin()

        # Should not raise exception
        await plugin.stop()

    def test_add_message_handler(self):
        """Test adding message handler."""
        plugin = TelegramPlugin()

        mock_client = MagicMock()
        mock_client.add_event_handler = MagicMock()
        plugin.client = mock_client

        def test_callback():
            pass

        mock_event = MagicMock()

        plugin.add_message_handler(test_callback, mock_event)

        mock_client.add_event_handler.assert_called_once_with(test_callback, mock_event)

    def test_add_message_handler_no_client(self):
        """Test adding message handler when no client exists."""
        plugin = TelegramPlugin()

        def test_callback():
            pass

        mock_event = MagicMock()

        # Should not raise exception
        plugin.add_message_handler(test_callback, mock_event)

    def test_set_message_mode(self):
        """Test setting message mode."""
        plugin = TelegramPlugin()

        # Mock settings
        mock_settings = MagicMock()
        plugin.settings = mock_settings

        with patch("plugins.telegram.settings.MessageMode") as mock_mode_class:
            mock_mode = MagicMock()
            mock_mode.name = "echo"
            mock_mode_class.return_value = mock_mode

            plugin.set_message_mode("echo")

            assert plugin.settings.message_mode == mock_mode

    def test_set_message_mode_string(self):
        """Test setting message mode with string."""
        plugin = TelegramPlugin()

        # Mock settings
        mock_settings = MagicMock()
        plugin.settings = mock_settings

        with patch("plugins.telegram.settings.MessageMode") as mock_mode_class:
            mock_mode = MagicMock()
            mock_mode.name = "echo"
            mock_mode_class.return_value = mock_mode

            plugin.set_message_mode("echo")

            mock_mode_class.assert_called_once_with("echo")
            assert plugin.settings.message_mode == mock_mode
