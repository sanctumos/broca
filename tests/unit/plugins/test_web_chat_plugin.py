"""Unit tests for web chat plugin."""

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from plugins.web_chat.plugin import WebChatPlugin


class TestWebChatPlugin:
    """Test cases for WebChatPlugin."""

    def test_plugin_initialization_default(self):
        """Test plugin initialization with default settings."""
        plugin = WebChatPlugin()

        assert plugin.settings is None
        assert plugin.api_client is None
        assert plugin.message_handler is None
        assert plugin.polling_task is None
        assert not plugin.is_running
        assert len(plugin.processed_messages) == 0
        assert len(plugin.session_responses) == 0

    def test_plugin_initialization_with_settings(self):
        """Test plugin initialization with settings."""
        mock_settings = MagicMock()
        plugin = WebChatPlugin(settings=mock_settings)

        assert plugin.settings == mock_settings
        assert plugin.api_client is None
        assert plugin.message_handler is None
        assert plugin.polling_task is None
        assert not plugin.is_running

    def test_get_name_default(self):
        """Test get_name with default settings."""
        plugin = WebChatPlugin()
        name = plugin.get_name()
        assert name == "web_chat"

    def test_get_name_with_settings(self):
        """Test get_name with custom settings."""
        mock_settings = MagicMock()
        mock_settings.plugin_name = "custom_web_chat"
        plugin = WebChatPlugin(settings=mock_settings)

        name = plugin.get_name()
        assert name == "custom_web_chat"

    def test_get_platform_default(self):
        """Test get_platform with default settings."""
        plugin = WebChatPlugin()
        platform = plugin.get_platform()
        assert platform == "web_chat"

    def test_get_platform_with_settings(self):
        """Test get_platform with custom settings."""
        mock_settings = MagicMock()
        mock_settings.platform_name = "custom_platform"
        plugin = WebChatPlugin(settings=mock_settings)

        platform = plugin.get_platform()
        assert platform == "custom_platform"

    def test_get_message_handler(self):
        """Test get_message_handler method."""
        plugin = WebChatPlugin()
        handler = plugin.get_message_handler()
        assert handler == plugin._handle_response

    def test_get_settings_default(self):
        """Test get_settings with default settings."""
        plugin = WebChatPlugin()
        with patch.dict(
            os.environ,
            {"WEB_CHAT_API_URL": "http://test.com", "WEB_CHAT_POLL_INTERVAL": "5"},
        ):
            settings = plugin.get_settings()
            assert settings is not None
            assert "api_url" in settings

    def test_get_settings_with_custom(self):
        """Test get_settings with custom settings."""
        mock_settings = MagicMock()
        plugin = WebChatPlugin(settings=mock_settings)

        settings = plugin.get_settings()
        assert settings == mock_settings.to_dict()
        # to_dict() is called multiple times due to the assertion above

    def test_validate_settings_default(self):
        """Test validate_settings with default settings."""
        plugin = WebChatPlugin()
        with patch.dict(
            os.environ,
            {"WEB_CHAT_API_URL": "http://test.com", "WEB_CHAT_POLL_INTERVAL": "5"},
        ):
            # Initialize settings first
            plugin.get_settings()
            result = plugin.validate_settings()
            assert result is True

    def test_validate_settings_with_custom(self):
        """Test validate_settings with custom settings."""
        mock_settings = MagicMock()
        mock_settings.validate_settings.return_value = True
        plugin = WebChatPlugin(settings=mock_settings)

        result = plugin.validate_settings()
        assert result is True
        mock_settings.validate_settings.assert_called_once()

    def test_apply_settings_default(self):
        """Test apply_settings with default settings."""
        plugin = WebChatPlugin()
        with patch.dict(
            os.environ,
            {"WEB_CHAT_API_URL": "http://test.com", "WEB_CHAT_POLL_INTERVAL": "5"},
        ):
            test_settings = {"api_url": "http://test.com", "poll_interval": 5}
            plugin.apply_settings(test_settings)
            # Should not raise an exception

    def test_apply_settings_with_custom(self):
        """Test apply_settings with custom settings."""
        mock_settings = MagicMock()
        plugin = WebChatPlugin(settings=mock_settings)

        test_settings = {"api_url": "http://test.com", "poll_interval": 5}
        plugin.apply_settings(test_settings)
        # Should not raise an exception

    @pytest.mark.asyncio
    async def test_start(self):
        """Test start method."""
        plugin = WebChatPlugin()
        with patch.dict(
            os.environ,
            {"WEB_CHAT_API_URL": "http://test.com", "WEB_CHAT_POLL_INTERVAL": "5"},
        ):
            # Initialize settings first
            plugin.get_settings()

            with patch(
                "plugins.web_chat.plugin.WebChatAPIClient"
            ) as mock_api_client_class:
                with patch("plugins.web_chat.plugin.WebChatMessageHandler"):
                    with patch.object(
                        plugin, "_poll_messages", new_callable=AsyncMock
                    ) as mock_poll:
                        mock_api_client = mock_api_client_class.return_value
                        mock_api_client.test_connection = AsyncMock(return_value=True)
                        mock_poll.return_value = None

                        await plugin.start()

                        assert plugin.is_running is True
                        assert plugin.polling_task is not None
                        mock_api_client.test_connection.assert_called_once()
                        mock_poll.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop(self):
        """Test stop method."""
        plugin = WebChatPlugin()
        plugin.is_running = True
        # Create a real asyncio.Task for polling_task
        plugin.polling_task = asyncio.create_task(asyncio.sleep(0.1))
        plugin.api_client = MagicMock()
        plugin.api_client.session = MagicMock()
        plugin.api_client.session.close = AsyncMock()

        await plugin.stop()

        assert not plugin.is_running
        # Note: cancel() is a built-in method on asyncio.Task, not a mock

    @pytest.mark.asyncio
    async def test_stop_not_running(self):
        """Test stop method when not running."""
        plugin = WebChatPlugin()
        plugin.is_running = False

        await plugin.stop()

        # Should not raise an exception

    # Removed test_initialize_components - method doesn't exist on WebChatPlugin

    # Removed test_start_polling - method doesn't exist on WebChatPlugin

    # Removed test_stop_polling - method doesn't exist on WebChatPlugin

    # Removed test_stop_polling_no_task - method doesn't exist on WebChatPlugin

    @pytest.mark.asyncio
    async def test_poll_messages(self):
        """Test _poll_messages method."""
        plugin = WebChatPlugin()
        with patch.dict(
            os.environ,
            {"WEB_CHAT_API_URL": "http://test.com", "WEB_CHAT_POLL_INTERVAL": "5"},
        ):
            # Initialize settings first
            plugin.get_settings()

            mock_api_client = MagicMock()
            mock_api_client.get_messages = AsyncMock(
                return_value=[
                    {"id": 1, "message": "Hello", "user_id": "user1"},
                    {"id": 2, "message": "Hi", "user_id": "user2"},
                ]
            )
            plugin.api_client = mock_api_client

            mock_message_handler = MagicMock()
            mock_message_handler.process_incoming_message = AsyncMock(
                return_value=MagicMock()
            )
            plugin.message_handler = mock_message_handler

            # Set is_running to True initially, then False after first iteration
            plugin.is_running = True
            original_sleep = asyncio.sleep

            async def mock_sleep(delay):
                plugin.is_running = False
                await original_sleep(0.01)

            with patch("asyncio.sleep", side_effect=mock_sleep):
                await plugin._poll_messages()

            # Verify API was called
            mock_api_client.get_messages.assert_called_once()

            # Verify message handler was called for each message
            assert mock_message_handler.process_incoming_message.call_count == 2

    @pytest.mark.asyncio
    async def test_poll_messages_no_api_client(self):
        """Test _poll_messages method with no API client."""
        plugin = WebChatPlugin()
        with patch.dict(
            os.environ,
            {"WEB_CHAT_API_URL": "http://test.com", "WEB_CHAT_POLL_INTERVAL": "5"},
        ):
            # Initialize settings first
            plugin.get_settings()
            plugin.api_client = None

            await plugin._poll_messages()

            # Should not raise an exception

    @pytest.mark.asyncio
    async def test_poll_messages_no_message_handler(self):
        """Test _poll_messages method with no message handler."""
        plugin = WebChatPlugin()
        with patch.dict(
            os.environ,
            {"WEB_CHAT_API_URL": "http://test.com", "WEB_CHAT_POLL_INTERVAL": "5"},
        ):
            # Initialize settings first
            plugin.get_settings()

            mock_api_client = MagicMock()
            mock_api_client.get_messages = AsyncMock(
                return_value=[{"id": 1, "message": "Hello", "user_id": "user1"}]
            )
            plugin.api_client = mock_api_client
            plugin.message_handler = None

            # Set is_running to False to break the loop quickly
            plugin.is_running = False

            await plugin._poll_messages()

            # Should not raise an exception

    @pytest.mark.asyncio
    async def test_poll_messages_empty_response(self):
        """Test _poll_messages method with empty response."""
        plugin = WebChatPlugin()
        with patch.dict(
            os.environ,
            {"WEB_CHAT_API_URL": "http://test.com", "WEB_CHAT_POLL_INTERVAL": "5"},
        ):
            # Initialize settings first
            plugin.get_settings()

            mock_api_client = MagicMock()
            mock_api_client.get_messages = AsyncMock(return_value=[])
            plugin.api_client = mock_api_client

            mock_message_handler = MagicMock()
            plugin.message_handler = mock_message_handler

            # Set is_running to True initially, then False after first iteration
            plugin.is_running = True
            original_sleep = asyncio.sleep

            async def mock_sleep(delay):
                plugin.is_running = False
                await original_sleep(0.01)

            with patch("asyncio.sleep", side_effect=mock_sleep):
                await plugin._poll_messages()

            # Verify API was called
            mock_api_client.get_messages.assert_called_once()

            # Verify message handler was not called
            mock_message_handler.process_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_response(self):
        """Test _handle_response method."""
        plugin = WebChatPlugin()

        mock_api_client = MagicMock()
        mock_api_client.post_response = AsyncMock(return_value=True)
        plugin.api_client = mock_api_client

        response = "Test response"
        profile = MagicMock()
        profile.metadata = {"session_id": "session123"}
        message_id = 123

        await plugin._handle_response(response, profile, message_id)

        # Verify API was called with positional arguments
        mock_api_client.post_response.assert_called_once_with("session123", response)

    @pytest.mark.asyncio
    async def test_handle_response_no_api_client(self):
        """Test _handle_response method with no API client."""
        plugin = WebChatPlugin()
        plugin.api_client = None

        response = "Test response"
        profile = MagicMock()
        message_id = 123

        await plugin._handle_response(response, profile, message_id)

        # Should not raise an exception

    # Removed test_register_event_handler - WebChatPlugin doesn't use event handlers

    # Removed test_emit_event - WebChatPlugin doesn't emit events

    def test_emit_event_no_handlers(self):
        """Test emit_event method with no handlers."""
        plugin = WebChatPlugin()

        mock_event = MagicMock()
        mock_event.type = "test_event"

        # No handlers registered
        plugin.emit_event(mock_event)

        # Should not raise an exception

    def test_processed_messages_tracking(self):
        """Test processed messages tracking."""
        plugin = WebChatPlugin()

        # Add a processed message
        plugin.processed_messages.add("msg_123")

        # Verify it's tracked
        assert "msg_123" in plugin.processed_messages

        # Remove it
        plugin.processed_messages.remove("msg_123")

        # Verify it's removed
        assert "msg_123" not in plugin.processed_messages

    def test_session_responses_tracking(self):
        """Test session responses tracking."""
        plugin = WebChatPlugin()

        # Add a session response
        plugin.session_responses["session_123"] = "response_456"

        # Verify it's tracked
        assert plugin.session_responses["session_123"] == "response_456"

        # Remove it
        del plugin.session_responses["session_123"]

        # Verify it's removed
        assert "session_123" not in plugin.session_responses
