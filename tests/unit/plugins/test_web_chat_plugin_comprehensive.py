"""Tests for Web Chat plugin."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from plugins.web_chat.plugin import WebChatPlugin


class TestWebChatPlugin:
    """Test the WebChatPlugin class."""

    def test_init_default(self):
        """Test WebChatPlugin initialization with defaults."""
        plugin = WebChatPlugin()
        assert plugin.settings is None
        assert plugin.api_client is None
        assert plugin.message_handler is None
        assert plugin.polling_task is None
        assert plugin.is_running is False
        assert plugin.processed_messages == set()
        assert plugin.session_responses == {}

    def test_init_with_settings(self):
        """Test WebChatPlugin initialization with settings."""
        mock_settings = MagicMock()
        plugin = WebChatPlugin(settings=mock_settings)
        assert plugin.settings == mock_settings

    def test_get_name_default(self):
        """Test getting plugin name with default settings."""
        plugin = WebChatPlugin()
        assert plugin.get_name() == "web_chat"

    def test_get_name_with_settings(self):
        """Test getting plugin name with settings."""
        mock_settings = MagicMock()
        mock_settings.plugin_name = "custom_web_chat"
        plugin = WebChatPlugin(settings=mock_settings)
        assert plugin.get_name() == "custom_web_chat"

    def test_get_platform_default(self):
        """Test getting platform name with default settings."""
        plugin = WebChatPlugin()
        assert plugin.get_platform() == "web_chat"

    def test_get_platform_with_settings(self):
        """Test getting platform name with settings."""
        mock_settings = MagicMock()
        mock_settings.platform_name = "custom_platform"
        plugin = WebChatPlugin(settings=mock_settings)
        assert plugin.get_platform() == "custom_platform"

    def test_get_message_handler(self):
        """Test getting message handler."""
        plugin = WebChatPlugin()
        handler = plugin.get_message_handler()
        assert handler == plugin._handle_response

    @pytest.mark.asyncio
    async def test_start_success(self):
        """Test successful plugin start."""
        plugin = WebChatPlugin()

        # Mock settings
        mock_settings = MagicMock()
        mock_settings.platform_name = "web_chat"
        plugin.settings = mock_settings

        # Mock API client
        mock_api_client = MagicMock()
        mock_api_client.test_connection = AsyncMock(return_value=True)

        # Mock message handler
        mock_message_handler = MagicMock()

        with patch(
            "plugins.web_chat.api_client.WebChatAPIClient", return_value=mock_api_client
        ), patch(
            "plugins.web_chat.message_handler.WebChatMessageHandler",
            return_value=mock_message_handler,
        ), patch(
            "asyncio.create_task"
        ) as mock_create_task:
            await plugin.start()

            assert plugin.is_running is True
            assert plugin.api_client == mock_api_client
            assert plugin.message_handler == mock_message_handler
            mock_create_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_already_running(self):
        """Test starting plugin when already running."""
        plugin = WebChatPlugin()
        plugin.is_running = True

        await plugin.start()

        # Should not start again
        assert plugin.is_running is True

    @pytest.mark.asyncio
    async def test_start_connection_failed(self):
        """Test starting plugin when connection fails."""
        plugin = WebChatPlugin()

        # Mock settings
        mock_settings = MagicMock()
        plugin.settings = mock_settings

        # Mock API client that fails connection
        mock_api_client = MagicMock()
        mock_api_client.test_connection = AsyncMock(return_value=False)

        with patch(
            "plugins.web_chat.api_client.WebChatAPIClient", return_value=mock_api_client
        ):
            await plugin.start()

            # Should not be running if connection failed
            assert plugin.is_running is False

    @pytest.mark.asyncio
    async def test_start_exception(self):
        """Test starting plugin with exception."""
        plugin = WebChatPlugin()

        with patch(
            "plugins.web_chat.api_client.WebChatAPIClient",
            side_effect=Exception("API error"),
        ):
            with pytest.raises(Exception, match="API error"):
                await plugin.start()

    @pytest.mark.asyncio
    async def test_stop_success(self):
        """Test successful plugin stop."""
        plugin = WebChatPlugin()
        plugin.is_running = True

        # Mock polling task
        mock_task = MagicMock()
        mock_task.cancel = MagicMock()
        mock_task.__await__ = AsyncMock(return_value=None)
        plugin.polling_task = mock_task

        # Mock API client
        mock_api_client = MagicMock()
        mock_api_client.session = MagicMock()
        mock_api_client.session.close = AsyncMock()
        plugin.api_client = mock_api_client

        await plugin.stop()

        assert plugin.is_running is False
        mock_task.cancel.assert_called_once()
        mock_api_client.session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_not_running(self):
        """Test stopping plugin when not running."""
        plugin = WebChatPlugin()
        plugin.is_running = False

        await plugin.stop()

        # Should not do anything
        assert plugin.is_running is False

    @pytest.mark.asyncio
    async def test_stop_cancelled_task(self):
        """Test stopping plugin with cancelled task."""
        plugin = WebChatPlugin()
        plugin.is_running = True

        # Mock polling task that raises CancelledError
        mock_task = MagicMock()
        mock_task.cancel = MagicMock()
        mock_task.__await__ = AsyncMock(side_effect=asyncio.CancelledError())
        plugin.polling_task = mock_task

        await plugin.stop()

        assert plugin.is_running is False
        mock_task.cancel.assert_called_once()

    def test_get_settings_success(self):
        """Test getting settings successfully."""
        plugin = WebChatPlugin()

        mock_settings = MagicMock()
        mock_settings.to_dict.return_value = {"api_url": "http://test.com"}

        with patch("plugins.web_chat.settings.WebChatSettings") as mock_settings_class:
            mock_settings_class.from_env.return_value = mock_settings
            result = plugin.get_settings()

            assert result == {"api_url": "http://test.com"}
            assert plugin.settings == mock_settings

    def test_get_settings_exception(self):
        """Test getting settings with exception."""
        plugin = WebChatPlugin()

        with patch("plugins.web_chat.settings.WebChatSettings") as mock_settings_class:
            mock_settings_class.from_env.side_effect = Exception("Settings error")
            result = plugin.get_settings()

            assert result == {}

    def test_get_settings_existing(self):
        """Test getting existing settings."""
        plugin = WebChatPlugin()

        mock_settings = MagicMock()
        mock_settings.to_dict.return_value = {"api_url": "http://test.com"}
        plugin.settings = mock_settings

        result = plugin.get_settings()

        assert result == {"api_url": "http://test.com"}

    def test_validate_settings(self):
        """Test validating settings."""
        plugin = WebChatPlugin()

        mock_settings = MagicMock()
        mock_settings.validate_settings.return_value = True
        plugin.settings = mock_settings

        result = plugin.validate_settings()

        assert result is True
        mock_settings.validate_settings.assert_called_once()

    def test_apply_settings(self):
        """Test applying settings."""
        plugin = WebChatPlugin()

        mock_settings = MagicMock()
        mock_settings.plugin_name = "test_plugin"

        with patch("plugins.web_chat.settings.WebChatSettings") as mock_settings_class:
            mock_settings_class.from_dict.return_value = mock_settings

            plugin.apply_settings({"api_url": "http://test.com"})

            assert plugin.settings == mock_settings

    def test_apply_settings_empty(self):
        """Test applying empty settings."""
        plugin = WebChatPlugin()

        plugin.apply_settings({})

        # Should not change settings
        assert plugin.settings is None

    @pytest.mark.asyncio
    async def test_poll_messages_success(self):
        """Test successful message polling."""
        plugin = WebChatPlugin()
        plugin.is_running = True

        # Mock settings
        mock_settings = MagicMock()
        mock_settings.poll_interval = 1
        plugin.settings = mock_settings

        # Mock API client
        mock_api_client = MagicMock()
        mock_api_client.get_messages = AsyncMock(
            return_value=[
                {"id": 1, "session_id": "session1", "text": "Hello"},
                {"id": 2, "session_id": "session2", "text": "World"},
            ]
        )
        plugin.api_client = mock_api_client

        # Mock message handler
        mock_message_handler = MagicMock()
        mock_message_handler.process_incoming_message = AsyncMock(
            return_value=MagicMock()
        )
        plugin.message_handler = mock_message_handler

        with patch("asyncio.sleep", side_effect=asyncio.CancelledError):
            with pytest.raises(asyncio.CancelledError):
                await plugin._poll_messages()

            # Check that messages were processed
            assert mock_api_client.get_messages.call_count >= 1
            assert mock_message_handler.process_incoming_message.call_count >= 2

    @pytest.mark.asyncio
    async def test_poll_messages_no_messages(self):
        """Test polling when no messages available."""
        plugin = WebChatPlugin()
        plugin.is_running = True

        # Mock settings
        mock_settings = MagicMock()
        mock_settings.poll_interval = 1
        plugin.settings = mock_settings

        # Mock API client
        mock_api_client = MagicMock()
        mock_api_client.get_messages = AsyncMock(return_value=[])
        plugin.api_client = mock_api_client

        with patch("asyncio.sleep", side_effect=asyncio.CancelledError):
            with pytest.raises(asyncio.CancelledError):
                await plugin._poll_messages()

            # Check that API was called
            assert mock_api_client.get_messages.call_count >= 1

    @pytest.mark.asyncio
    async def test_poll_messages_exception(self):
        """Test polling with exception."""
        plugin = WebChatPlugin()
        plugin.is_running = True

        # Mock settings
        mock_settings = MagicMock()
        mock_settings.poll_interval = 1
        mock_settings.retry_delay = 0.1
        plugin.settings = mock_settings

        # Mock API client that raises exception
        mock_api_client = MagicMock()
        mock_api_client.get_messages = AsyncMock(side_effect=Exception("API error"))
        plugin.api_client = mock_api_client

        with patch("asyncio.sleep", side_effect=asyncio.CancelledError):
            with pytest.raises(asyncio.CancelledError):
                await plugin._poll_messages()

    @pytest.mark.asyncio
    async def test_poll_messages_stopped(self):
        """Test polling when plugin is stopped."""
        plugin = WebChatPlugin()
        plugin.is_running = False

        # Mock settings
        mock_settings = MagicMock()
        mock_settings.poll_interval = 1
        plugin.settings = mock_settings

        # Mock API client
        mock_api_client = MagicMock()
        mock_api_client.get_messages = AsyncMock(return_value=[])
        plugin.api_client = mock_api_client

        await plugin._poll_messages()

        # Should not call API when not running
        mock_api_client.get_messages.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_message_success(self):
        """Test successful message processing."""
        plugin = WebChatPlugin()

        # Mock message handler
        mock_message_handler = MagicMock()
        mock_message_handler.process_incoming_message = AsyncMock(
            return_value=MagicMock()
        )
        plugin.message_handler = mock_message_handler

        message_data = {
            "id": 1,
            "session_id": "session1",
            "timestamp": "2023-01-01T12:00:00Z",
            "text": "Hello",
        }

        await plugin._process_message(message_data)

        # Check that message was processed
        mock_message_handler.process_incoming_message.assert_called_once_with(
            message_data
        )

        # Check that message was marked as processed
        message_id = f"{message_data['session_id']}_{message_data['id']}_{message_data['timestamp']}"
        assert message_id in plugin.processed_messages

    @pytest.mark.asyncio
    async def test_process_message_already_processed(self):
        """Test processing already processed message."""
        plugin = WebChatPlugin()

        # Mock message handler
        mock_message_handler = MagicMock()
        plugin.message_handler = mock_message_handler

        message_data = {
            "id": 1,
            "session_id": "session1",
            "timestamp": "2023-01-01T12:00:00Z",
            "text": "Hello",
        }

        # Mark message as already processed
        message_id = f"{message_data['session_id']}_{message_data['id']}_{message_data['timestamp']}"
        plugin.processed_messages.add(message_id)

        await plugin._process_message(message_data)

        # Should not process again
        mock_message_handler.process_incoming_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_message_exception(self):
        """Test message processing with exception."""
        plugin = WebChatPlugin()

        # Mock message handler that raises exception
        mock_message_handler = MagicMock()
        mock_message_handler.process_incoming_message = AsyncMock(
            side_effect=Exception("Processing error")
        )
        plugin.message_handler = mock_message_handler

        message_data = {
            "id": 1,
            "session_id": "session1",
            "timestamp": "2023-01-01T12:00:00Z",
            "text": "Hello",
        }

        await plugin._process_message(message_data)

        # Should not mark as processed if exception occurred
        message_id = f"{message_data['session_id']}_{message_data['id']}_{message_data['timestamp']}"
        assert message_id not in plugin.processed_messages

    @pytest.mark.asyncio
    async def test_send_response_success(self):
        """Test successful response sending."""
        plugin = WebChatPlugin()

        # Mock API client
        mock_api_client = MagicMock()
        mock_api_client.post_response = AsyncMock(return_value=True)
        plugin.api_client = mock_api_client

        # Mock message handler
        mock_message_handler = MagicMock()
        mock_message_handler.process_outgoing_message = AsyncMock()
        plugin.message_handler = mock_message_handler

        original_message = {"id": 1, "text": "Hello"}

        result = await plugin.send_response("session1", "Response", original_message)

        assert result is True
        mock_api_client.post_response.assert_called_once_with("session1", "Response")
        mock_message_handler.process_outgoing_message.assert_called_once_with(
            "session1", "Response", original_message
        )

    @pytest.mark.asyncio
    async def test_send_response_no_api_client(self):
        """Test sending response with no API client."""
        plugin = WebChatPlugin()

        result = await plugin.send_response("session1", "Response")

        assert result is False

    @pytest.mark.asyncio
    async def test_send_response_api_failure(self):
        """Test sending response when API fails."""
        plugin = WebChatPlugin()

        # Mock API client that fails
        mock_api_client = MagicMock()
        mock_api_client.post_response = AsyncMock(return_value=False)
        plugin.api_client = mock_api_client

        result = await plugin.send_response("session1", "Response")

        assert result is False

    @pytest.mark.asyncio
    async def test_send_response_exception(self):
        """Test sending response with exception."""
        plugin = WebChatPlugin()

        # Mock API client that raises exception
        mock_api_client = MagicMock()
        mock_api_client.post_response = AsyncMock(side_effect=Exception("API error"))
        plugin.api_client = mock_api_client

        result = await plugin.send_response("session1", "Response")

        assert result is False

    @pytest.mark.asyncio
    async def test_handle_response_success(self):
        """Test successful response handling."""
        plugin = WebChatPlugin()

        # Mock profile with metadata
        mock_profile = MagicMock()
        mock_profile.metadata = json.dumps({"session_id": "session1"})

        with patch.object(
            plugin, "send_response", new_callable=AsyncMock, return_value=True
        ) as mock_send:
            await plugin._handle_response("Response", mock_profile, 123)

            mock_send.assert_called_once_with("session1", "Response")

    @pytest.mark.asyncio
    async def test_handle_response_dict_metadata(self):
        """Test response handling with dict metadata."""
        plugin = WebChatPlugin()

        # Mock profile with dict metadata
        mock_profile = MagicMock()
        mock_profile.metadata = {"session_id": "session1"}

        with patch.object(
            plugin, "send_response", new_callable=AsyncMock, return_value=True
        ) as mock_send:
            await plugin._handle_response("Response", mock_profile, 123)

            mock_send.assert_called_once_with("session1", "Response")

    @pytest.mark.asyncio
    async def test_handle_response_no_session_id(self):
        """Test response handling with no session ID."""
        plugin = WebChatPlugin()

        # Mock profile with no session_id
        mock_profile = MagicMock()
        mock_profile.metadata = json.dumps({"other": "data"})

        with patch.object(plugin, "send_response", new_callable=AsyncMock) as mock_send:
            await plugin._handle_response("Response", mock_profile, 123)

            # Should not send response
            mock_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_response_exception(self):
        """Test response handling with exception."""
        plugin = WebChatPlugin()

        # Mock profile that raises exception
        mock_profile = MagicMock()
        mock_profile.metadata = json.dumps({"session_id": "session1"})

        with patch.object(
            plugin,
            "send_response",
            new_callable=AsyncMock,
            side_effect=Exception("Send error"),
        ):
            await plugin._handle_response("Response", mock_profile, 123)

            # Should not raise exception
