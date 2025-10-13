"""Unit tests for web chat plugin."""

import asyncio
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
        settings = plugin.get_settings()
        assert settings is None

    def test_get_settings_with_custom(self):
        """Test get_settings with custom settings."""
        mock_settings = MagicMock()
        plugin = WebChatPlugin(settings=mock_settings)

        settings = plugin.get_settings()
        assert settings == mock_settings

    def test_validate_settings_default(self):
        """Test validate_settings with default settings."""
        plugin = WebChatPlugin()
        result = plugin.validate_settings({})
        assert result is True

    def test_validate_settings_with_custom(self):
        """Test validate_settings with custom settings."""
        mock_settings = MagicMock()
        mock_settings.validate.return_value = True
        plugin = WebChatPlugin(settings=mock_settings)

        test_settings = {"api_url": "http://test.com"}
        result = plugin.validate_settings(test_settings)
        assert result is True
        mock_settings.validate.assert_called_once_with(test_settings)

    def test_apply_settings_default(self):
        """Test apply_settings with default settings."""
        plugin = WebChatPlugin()

        test_settings = {"api_url": "http://test.com"}
        plugin.apply_settings(test_settings)

        # Should not raise an exception

    def test_apply_settings_with_custom(self):
        """Test apply_settings with custom settings."""
        mock_settings = MagicMock()
        plugin = WebChatPlugin(settings=mock_settings)

        test_settings = {"api_url": "http://test.com"}
        plugin.apply_settings(test_settings)

        mock_settings.update.assert_called_once_with(test_settings)

    @pytest.mark.asyncio
    async def test_start(self):
        """Test start method."""
        plugin = WebChatPlugin()

        with patch.object(
            plugin, "_initialize_components", new_callable=AsyncMock
        ) as mock_init:
            with patch.object(
                plugin, "_start_polling", new_callable=AsyncMock
            ) as mock_polling:
                await plugin.start()

                mock_init.assert_called_once()
                mock_polling.assert_called_once()
                assert plugin.is_running

    @pytest.mark.asyncio
    async def test_stop(self):
        """Test stop method."""
        plugin = WebChatPlugin()
        plugin.is_running = True
        plugin.polling_task = MagicMock()

        with patch.object(plugin, "_stop_polling", new_callable=AsyncMock) as mock_stop:
            await plugin.stop()

            mock_stop.assert_called_once()
            assert not plugin.is_running

    @pytest.mark.asyncio
    async def test_stop_not_running(self):
        """Test stop method when not running."""
        plugin = WebChatPlugin()
        plugin.is_running = False

        await plugin.stop()

        # Should not raise an exception

    @pytest.mark.asyncio
    async def test_initialize_components(self):
        """Test _initialize_components method."""
        mock_settings = MagicMock()
        mock_settings.api_url = "http://test.com"
        mock_settings.poll_interval = 5
        plugin = WebChatPlugin(settings=mock_settings)

        with patch("plugins.web_chat.plugin.WebChatAPIClient") as mock_api_client:
            with patch("plugins.web_chat.plugin.WebChatMessageHandler") as mock_handler:
                mock_api_instance = MagicMock()
                mock_api_client.return_value = mock_api_instance

                mock_handler_instance = MagicMock()
                mock_handler.return_value = mock_handler_instance

                await plugin._initialize_components()

                assert plugin.api_client == mock_api_instance
                assert plugin.message_handler == mock_handler_instance

    @pytest.mark.asyncio
    async def test_start_polling(self):
        """Test _start_polling method."""
        plugin = WebChatPlugin()
        plugin.is_running = True

        with patch.object(plugin, "_poll_messages", new_callable=AsyncMock):
            # Create a task that will be cancelled quickly
            async def quick_cancel():
                await asyncio.sleep(0.01)
                plugin.is_running = False

            cancel_task = asyncio.create_task(quick_cancel())

            await plugin._start_polling()

            # Clean up
            cancel_task.cancel()

    @pytest.mark.asyncio
    async def test_stop_polling(self):
        """Test _stop_polling method."""
        plugin = WebChatPlugin()

        # Create a mock task
        mock_task = MagicMock()
        plugin.polling_task = mock_task

        await plugin._stop_polling()

        mock_task.cancel.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_polling_no_task(self):
        """Test _stop_polling method with no task."""
        plugin = WebChatPlugin()
        plugin.polling_task = None

        await plugin._stop_polling()

        # Should not raise an exception

    @pytest.mark.asyncio
    async def test_poll_messages(self):
        """Test _poll_messages method."""
        plugin = WebChatPlugin()

        mock_api_client = MagicMock()
        mock_api_client.get_messages.return_value = [
            {"id": 1, "message": "Hello", "user_id": "user1"},
            {"id": 2, "message": "Hi", "user_id": "user2"},
        ]
        plugin.api_client = mock_api_client

        mock_message_handler = MagicMock()
        mock_message_handler.process_message = AsyncMock()
        plugin.message_handler = mock_message_handler

        await plugin._poll_messages()

        # Verify API was called
        mock_api_client.get_messages.assert_called_once()

        # Verify message handler was called for each message
        assert mock_message_handler.process_message.call_count == 2

    @pytest.mark.asyncio
    async def test_poll_messages_no_api_client(self):
        """Test _poll_messages method with no API client."""
        plugin = WebChatPlugin()
        plugin.api_client = None

        await plugin._poll_messages()

        # Should not raise an exception

    @pytest.mark.asyncio
    async def test_poll_messages_no_message_handler(self):
        """Test _poll_messages method with no message handler."""
        plugin = WebChatPlugin()

        mock_api_client = MagicMock()
        mock_api_client.get_messages.return_value = [
            {"id": 1, "message": "Hello", "user_id": "user1"}
        ]
        plugin.api_client = mock_api_client
        plugin.message_handler = None

        await plugin._poll_messages()

        # Should not raise an exception

    @pytest.mark.asyncio
    async def test_poll_messages_empty_response(self):
        """Test _poll_messages method with empty response."""
        plugin = WebChatPlugin()

        mock_api_client = MagicMock()
        mock_api_client.get_messages.return_value = []
        plugin.api_client = mock_api_client

        mock_message_handler = MagicMock()
        plugin.message_handler = mock_message_handler

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
        mock_api_client.post_response = AsyncMock()
        plugin.api_client = mock_api_client

        response = "Test response"
        profile = MagicMock()
        profile.user_id = "user1"
        message_id = 123

        await plugin._handle_response(response, profile, message_id)

        # Verify API was called
        mock_api_client.post_response.assert_called_once_with(
            user_id="user1", message=response, message_id=message_id
        )

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

    def test_register_event_handler(self):
        """Test register_event_handler method."""
        plugin = WebChatPlugin()

        mock_handler = MagicMock()
        plugin.register_event_handler("test_event", mock_handler)

        # Verify handler was registered
        assert "test_event" in plugin._event_handlers
        assert mock_handler in plugin._event_handlers["test_event"]

    def test_emit_event(self):
        """Test emit_event method."""
        plugin = WebChatPlugin()

        mock_event = MagicMock()
        mock_event.type = "test_event"

        mock_handler = MagicMock()
        plugin._event_handlers["test_event"] = [mock_handler]

        plugin.emit_event(mock_event)

        # Verify handler was called
        mock_handler.assert_called_once_with(mock_event)

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
