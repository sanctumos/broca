"""
Comprehensive tests for Web Chat Plugin.

This module tests the WebChatPlugin class which handles
polling web chat API and processing messages through Broca2.
"""

import asyncio
import os
from unittest.mock import AsyncMock, Mock, patch

import pytest

from plugins.web_chat.plugin import WebChatPlugin
from plugins.web_chat.settings import WebChatSettings


class TestWebChatPlugin:
    """Test cases for WebChatPlugin class."""

    def test_initialization_default(self):
        """Test WebChatPlugin initialization with default settings."""
        plugin = WebChatPlugin()
        assert plugin.settings is None
        assert plugin.api_client is None
        assert plugin.message_handler is None
        assert plugin.polling_task is None
        assert plugin.is_running is False
        assert plugin.logger is not None
        assert plugin.processed_messages == set()
        assert plugin.session_responses == {}

    def test_initialization_with_settings(self):
        """Test WebChatPlugin initialization with settings."""
        settings = WebChatSettings(
            api_url="http://test.com",
            poll_interval=5,
            retry_delay=2,
            plugin_name="test_plugin",
            platform_name="test_platform",
        )
        plugin = WebChatPlugin(settings)
        assert plugin.settings == settings
        assert plugin.api_client is None
        assert plugin.message_handler is None
        assert plugin.polling_task is None
        assert plugin.is_running is False

    def test_get_name_default(self):
        """Test get_name with default settings."""
        plugin = WebChatPlugin()
        assert plugin.get_name() == "web_chat"

    def test_get_name_with_settings(self):
        """Test get_name with custom settings."""
        with patch.dict(
            os.environ,
            {"WEB_CHAT_API_URL": "http://test.com", "WEB_CHAT_POLL_INTERVAL": "5"},
        ):
            settings = WebChatSettings(
                plugin_name="custom_plugin", api_url="http://test.com", poll_interval=5
            )
            plugin = WebChatPlugin(settings)
            assert plugin.get_name() == "custom_plugin"

    def test_get_platform_default(self):
        """Test get_platform with default settings."""
        plugin = WebChatPlugin()
        assert plugin.get_platform() == "web_chat"

    def test_get_platform_with_settings(self):
        """Test get_platform with custom settings."""
        with patch.dict(
            os.environ,
            {"WEB_CHAT_API_URL": "http://test.com", "WEB_CHAT_POLL_INTERVAL": "5"},
        ):
            settings = WebChatSettings(
                platform_name="custom_platform",
                api_url="http://test.com",
                poll_interval=5,
            )
            plugin = WebChatPlugin(settings)
            assert plugin.get_platform() == "custom_platform"

    def test_get_message_handler(self):
        """Test get_message_handler returns correct method."""
        plugin = WebChatPlugin()
        handler = plugin.get_message_handler()
        assert handler == plugin._handle_response

    @pytest.mark.asyncio
    async def test_start_success(self):
        """Test successful plugin start."""
        settings = WebChatSettings(
            api_url="http://test.com", poll_interval=5, retry_delay=2
        )
        plugin = WebChatPlugin(settings)

        mock_api_client = AsyncMock()
        mock_message_handler = AsyncMock()
        mock_api_client.test_connection.return_value = True

        with patch(
            "plugins.web_chat.plugin.WebChatAPIClient", return_value=mock_api_client
        ), patch(
            "plugins.web_chat.plugin.WebChatMessageHandler",
            return_value=mock_message_handler,
        ), patch(
            "asyncio.create_task"
        ) as mock_create_task:
            mock_task = AsyncMock()
            mock_create_task.return_value = mock_task

            await plugin.start()

            assert plugin.is_running is True
            assert plugin.api_client == mock_api_client
            assert plugin.message_handler == mock_message_handler
            assert plugin.polling_task == mock_task
            mock_api_client.test_connection.assert_called_once()
            mock_create_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_already_running(self):
        """Test starting plugin that's already running."""
        plugin = WebChatPlugin()
        plugin.is_running = True

        await plugin.start()

        # Should not change state
        assert plugin.is_running is True

    @pytest.mark.asyncio
    async def test_start_connection_failed(self):
        """Test starting plugin with failed connection."""
        with patch.dict(
            os.environ,
            {"WEB_CHAT_API_URL": "http://test.com", "WEB_CHAT_POLL_INTERVAL": "5"},
        ):
            settings = WebChatSettings(api_url="http://test.com", poll_interval=5)
            plugin = WebChatPlugin(settings)

            mock_api_client = AsyncMock()
            mock_api_client.test_connection.return_value = False

            with patch(
                "plugins.web_chat.plugin.WebChatAPIClient", return_value=mock_api_client
            ):
                await plugin.start()

            assert plugin.is_running is False
            assert plugin.api_client == mock_api_client

    @pytest.mark.asyncio
    async def test_start_exception(self):
        """Test starting plugin with exception."""
        with patch.dict(
            os.environ,
            {"WEB_CHAT_API_URL": "http://test.com", "WEB_CHAT_POLL_INTERVAL": "5"},
        ):
            settings = WebChatSettings(api_url="http://test.com", poll_interval=5)
            plugin = WebChatPlugin(settings)

            with patch(
                "plugins.web_chat.plugin.WebChatAPIClient",
                side_effect=Exception("Connection error"),
            ):
                with pytest.raises(Exception, match="Connection error"):
                    await plugin.start()

                assert plugin.is_running is False

    @pytest.mark.asyncio
    async def test_stop_not_running(self):
        """Test stopping plugin that's not running."""
        plugin = WebChatPlugin()
        await plugin.stop()

        # Should not change state
        assert plugin.is_running is False

    @pytest.mark.asyncio
    async def test_stop_success(self):
        """Test successful plugin stop."""
        plugin = WebChatPlugin()
        plugin.is_running = True

        # Create a real asyncio task that can be cancelled and awaited
        async def dummy_task():
            await asyncio.sleep(1)

        plugin.polling_task = asyncio.create_task(dummy_task())
        plugin.polling_task.return_value = None  # Make it awaitable
        plugin.api_client = AsyncMock()
        plugin.api_client.session = AsyncMock()

        await plugin.stop()

        assert plugin.is_running is False
        # Note: can't assert cancel() was called on real asyncio task
        plugin.api_client.session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_with_cancelled_task(self):
        """Test stopping plugin with cancelled task."""
        plugin = WebChatPlugin()
        plugin.is_running = True

        # Create a real asyncio task that can be cancelled and awaited
        async def dummy_task():
            await asyncio.sleep(1)

        plugin.polling_task = asyncio.create_task(dummy_task())
        plugin.polling_task.side_effect = asyncio.CancelledError()

        await plugin.stop()

        assert plugin.is_running is False

    @pytest.mark.asyncio
    async def test_stop_no_api_client(self):
        """Test stopping plugin without API client."""
        plugin = WebChatPlugin()
        plugin.is_running = True

        # Create a real asyncio task that can be cancelled and awaited
        async def dummy_task():
            await asyncio.sleep(1)

        plugin.polling_task = asyncio.create_task(dummy_task())

        await plugin.stop()

        assert plugin.is_running is False

    def test_get_settings_default(self):
        """Test get_settings with default settings."""
        plugin = WebChatPlugin()

        with patch("plugins.web_chat.plugin.WebChatSettings.from_env") as mock_from_env:
            mock_settings = Mock()
            mock_settings.to_dict.return_value = {"test": "value"}
            mock_from_env.return_value = mock_settings

            result = plugin.get_settings()

            assert result == {"test": "value"}
            assert plugin.settings == mock_settings

    def test_get_settings_exception(self):
        """Test get_settings with exception."""
        plugin = WebChatPlugin()

        with patch(
            "plugins.web_chat.plugin.WebChatSettings.from_env",
            side_effect=Exception("Settings error"),
        ):
            result = plugin.get_settings()

            assert result == {}

    def test_get_settings_existing(self):
        """Test get_settings with existing settings."""
        with patch.dict(
            os.environ,
            {"WEB_CHAT_API_URL": "http://test.com", "WEB_CHAT_POLL_INTERVAL": "5"},
        ):
            settings = WebChatSettings(api_url="http://test.com", poll_interval=5)
            plugin = WebChatPlugin(settings)

            mock_settings = Mock()
            mock_settings.to_dict.return_value = {"test": "value"}
            plugin.settings = mock_settings

            result = plugin.get_settings()

            assert result == {"test": "value"}

    def test_validate_settings(self):
        """Test validate_settings."""
        with patch.dict(
            os.environ,
            {"WEB_CHAT_API_URL": "http://test.com", "WEB_CHAT_POLL_INTERVAL": "5"},
        ):
            settings = WebChatSettings(api_url="http://test.com", poll_interval=5)
            plugin = WebChatPlugin(settings)

            with patch.object(
                settings, "validate_settings", return_value=True
            ) as mock_validate:
                result = plugin.validate_settings()
                assert result is True
            mock_validate.assert_called_once()

    def test_apply_settings(self):
        """Test apply_settings."""
        plugin = WebChatPlugin()
        settings_dict = {"api_url": "http://test.com", "poll_interval": 5}

        with patch(
            "plugins.web_chat.plugin.WebChatSettings.from_dict"
        ) as mock_from_dict:
            mock_settings = Mock()
            mock_from_dict.return_value = mock_settings

            plugin.apply_settings(settings_dict)

            assert plugin.settings == mock_settings
            mock_from_dict.assert_called_once_with(settings_dict)

    def test_apply_settings_empty(self):
        """Test apply_settings with empty settings."""
        plugin = WebChatPlugin()
        plugin.apply_settings({})
        # Should not change settings
        assert plugin.settings is None

    @pytest.mark.asyncio
    async def test_poll_messages_success(self):
        """Test successful message polling."""
        with patch.dict(
            os.environ,
            {"WEB_CHAT_API_URL": "http://test.com", "WEB_CHAT_POLL_INTERVAL": "1"},
        ):
            settings = WebChatSettings(
                poll_interval=1, retry_delay=0.1, api_url="http://test.com"
            )
            plugin = WebChatPlugin(settings)
            plugin.is_running = True
            plugin.api_client = AsyncMock()
            plugin.message_handler = AsyncMock()

            messages = [
                {"session_id": "session1", "message": "Hello", "id": 1},
                {"session_id": "session2", "message": "World", "id": 2},
            ]
            plugin.api_client.get_messages.return_value = messages

            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                # Make sleep raise CancelledError to stop the loop
                mock_sleep.side_effect = asyncio.CancelledError()

                # The method catches CancelledError internally, so we don't expect it to be raised
                await plugin._poll_messages()

                plugin.api_client.get_messages.assert_called_once_with(limit=50)
                plugin.message_handler.process_incoming_message.assert_called()

    @pytest.mark.asyncio
    async def test_poll_messages_no_messages(self):
        """Test polling with no messages."""
        with patch.dict(
            os.environ,
            {"WEB_CHAT_API_URL": "http://test.com", "WEB_CHAT_POLL_INTERVAL": "1"},
        ):
            settings = WebChatSettings(
                poll_interval=1, retry_delay=0.1, api_url="http://test.com"
            )
            plugin = WebChatPlugin(settings)
            plugin.is_running = True
            plugin.api_client = AsyncMock()

            plugin.api_client.get_messages.return_value = []

            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                mock_sleep.side_effect = asyncio.CancelledError()

                # The method catches CancelledError internally, so we don't expect it to be raised
                await plugin._poll_messages()

                plugin.api_client.get_messages.assert_called_once()

    @pytest.mark.asyncio
    async def test_poll_messages_exception(self):
        """Test polling with exception."""
        with patch.dict(
            os.environ,
            {"WEB_CHAT_API_URL": "http://test.com", "WEB_CHAT_POLL_INTERVAL": "1"},
        ):
            settings = WebChatSettings(
                poll_interval=1, retry_delay=0.1, api_url="http://test.com"
            )
            plugin = WebChatPlugin(settings)
            plugin.is_running = True
            plugin.api_client = AsyncMock()

            plugin.api_client.get_messages.side_effect = Exception("API error")

            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                # Make the retry_delay sleep set is_running to False to exit the loop
                async def sleep_side_effect(delay):
                    if delay == plugin.settings.retry_delay:
                        plugin.is_running = False  # Exit the loop
                    return

                mock_sleep.side_effect = sleep_side_effect

                # The method catches the exception and sleeps for retry_delay, then exits
                await plugin._poll_messages()

                plugin.api_client.get_messages.assert_called_once()

    @pytest.mark.asyncio
    async def test_poll_messages_stopped(self):
        """Test polling when plugin is stopped."""
        with patch.dict(
            os.environ,
            {"WEB_CHAT_API_URL": "http://test.com", "WEB_CHAT_POLL_INTERVAL": "1"},
        ):
            settings = WebChatSettings(
                poll_interval=1, retry_delay=0.1, api_url="http://test.com"
            )
            plugin = WebChatPlugin(settings)
            plugin.is_running = False
            plugin.api_client = AsyncMock()

            await plugin._poll_messages()

            # Should not call get_messages when not running
            plugin.api_client.get_messages.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_message_success(self):
        """Test successful message processing."""
        plugin = WebChatPlugin()
        plugin.message_handler = AsyncMock()
        plugin.message_handler.process_incoming_message.return_value = 123

        message_data = {
            "session_id": "session1",
            "message": "Hello",
            "id": 1,
            "timestamp": "2024-01-01T12:00:00Z",
        }

        await plugin._process_message(message_data)

        assert len(plugin.processed_messages) == 1
        plugin.message_handler.process_incoming_message.assert_called_once_with(
            message_data
        )

    @pytest.mark.asyncio
    async def test_process_message_already_processed(self):
        """Test processing already processed message."""
        plugin = WebChatPlugin()
        plugin.message_handler = AsyncMock()

        message_data = {
            "session_id": "session1",
            "message": "Hello",
            "id": 1,
            "timestamp": "2024-01-01T12:00:00Z",
        }

        # Add message to processed set
        message_id = f"{message_data.get('session_id')}_{message_data.get('id')}_{message_data.get('timestamp')}"
        plugin.processed_messages.add(message_id)

        await plugin._process_message(message_data)

        # Should not process again
        plugin.message_handler.process_incoming_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_message_exception(self):
        """Test message processing with exception."""
        plugin = WebChatPlugin()
        plugin.message_handler = AsyncMock()
        plugin.message_handler.process_incoming_message.side_effect = Exception(
            "Processing error"
        )

        message_data = {
            "session_id": "session1",
            "message": "Hello",
            "id": 1,
            "timestamp": "2024-01-01T12:00:00Z",
        }

        await plugin._process_message(message_data)

        # Should not add to processed messages on error
        assert len(plugin.processed_messages) == 0

    @pytest.mark.asyncio
    async def test_send_response_success(self):
        """Test successful response sending."""
        plugin = WebChatPlugin()
        plugin.api_client = AsyncMock()
        plugin.message_handler = AsyncMock()
        plugin.api_client.post_response.return_value = True

        original_message = Mock()

        result = await plugin.send_response("session1", "Hello back!", original_message)

        assert result is True
        plugin.message_handler.process_outgoing_message.assert_called_once_with(
            "session1", "Hello back!", original_message
        )
        plugin.api_client.post_response.assert_called_once_with(
            "session1", "Hello back!"
        )

    @pytest.mark.asyncio
    async def test_send_response_no_api_client(self):
        """Test sending response without API client."""
        plugin = WebChatPlugin()
        result = await plugin.send_response("session1", "Hello back!")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_response_api_failure(self):
        """Test response sending with API failure."""
        plugin = WebChatPlugin()
        plugin.api_client = AsyncMock()
        plugin.message_handler = AsyncMock()
        plugin.api_client.post_response.return_value = False

        result = await plugin.send_response("session1", "Hello back!")

        assert result is False

    @pytest.mark.asyncio
    async def test_send_response_exception(self):
        """Test response sending with exception."""
        plugin = WebChatPlugin()
        plugin.api_client = AsyncMock()
        plugin.message_handler = AsyncMock()
        plugin.api_client.post_response.side_effect = Exception("API error")

        result = await plugin.send_response("session1", "Hello back!")

        assert result is False

    @pytest.mark.asyncio
    async def test_handle_response_success(self):
        """Test successful response handling."""
        plugin = WebChatPlugin()
        plugin.api_client = AsyncMock()
        plugin.api_client.post_response.return_value = True

        profile = Mock()
        profile.metadata = {"session_id": "session1"}
        message_id = 123

        await plugin._handle_response("Hello back!", profile, message_id)

        plugin.api_client.post_response.assert_called_once_with(
            "session1", "Hello back!"
        )

    @pytest.mark.asyncio
    async def test_handle_response_dict_metadata(self):
        """Test response handling with dict metadata."""
        plugin = WebChatPlugin()
        plugin.api_client = AsyncMock()
        plugin.api_client.post_response.return_value = True

        profile = Mock()
        profile.metadata = {"session_id": "session1"}
        message_id = 123

        await plugin._handle_response("Hello back!", profile, message_id)

        plugin.api_client.post_response.assert_called_once_with(
            "session1", "Hello back!"
        )

    @pytest.mark.asyncio
    async def test_handle_response_no_session_id(self):
        """Test response handling without session_id."""
        plugin = WebChatPlugin()
        plugin.api_client = AsyncMock()

        profile = Mock()
        profile.metadata = {}
        message_id = 123

        await plugin._handle_response("Hello back!", profile, message_id)

        plugin.api_client.post_response.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_response_exception(self):
        """Test response handling with exception."""
        plugin = WebChatPlugin()
        plugin.api_client = AsyncMock()
        plugin.api_client.post_response.side_effect = Exception("API error")

        profile = Mock()
        profile.metadata = {"session_id": "session1"}
        message_id = 123

        await plugin._handle_response("Hello back!", profile, message_id)

        # Should not raise exception

    @pytest.mark.asyncio
    async def test_handle_agent_response(self):
        """Test handling agent response."""
        plugin = WebChatPlugin()

        with patch.object(plugin, "send_response", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True

            result = await plugin.handle_agent_response("Hello back!", "session1")

            assert result is True
            mock_send.assert_called_once_with("session1", "Hello back!", None)

    def test_cleanup_processed_messages(self):
        """Test cleanup of processed messages."""
        plugin = WebChatPlugin()

        # Add many processed messages
        for i in range(1500):
            plugin.processed_messages.add(f"message_{i}")

        plugin.cleanup_processed_messages()

        assert len(plugin.processed_messages) == 0

    def test_cleanup_processed_messages_small_set(self):
        """Test cleanup with small set of processed messages."""
        plugin = WebChatPlugin()

        # Add few processed messages
        for i in range(100):
            plugin.processed_messages.add(f"message_{i}")

        plugin.cleanup_processed_messages()

        # Should not clear small sets
        assert len(plugin.processed_messages) == 100

    @pytest.mark.asyncio
    async def test_poll_messages_with_processed_message(self):
        """Test polling with message that gets processed."""
        with patch.dict(os.environ, {"WEB_CHAT_API_URL": "http://test.com"}):
            settings = WebChatSettings(
                api_url="http://test.com", poll_interval=1, retry_delay=0.1
            )
            plugin = WebChatPlugin(settings)
            plugin.is_running = True
            plugin.api_client = AsyncMock()
            plugin.message_handler = AsyncMock()

            messages = [
                {
                    "session_id": "session1",
                    "message": "Hello",
                    "id": 1,
                    "timestamp": "2024-01-01T12:00:00Z",
                }
            ]
            plugin.api_client.get_messages.return_value = messages
            plugin.message_handler.process_incoming_message.return_value = 123

            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                mock_sleep.side_effect = asyncio.CancelledError()

                # The method catches CancelledError internally, so we don't expect it to be raised
                await plugin._poll_messages()

                # Message should be processed and added to processed set
                assert len(plugin.processed_messages) == 1
                plugin.message_handler.process_incoming_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_poll_messages_stops_when_not_running(self):
        """Test polling stops when plugin is stopped during processing."""
        with patch.dict(os.environ, {"WEB_CHAT_API_URL": "http://test.com"}):
            settings = WebChatSettings(
                api_url="http://test.com", poll_interval=1, retry_delay=0.1
            )
            plugin = WebChatPlugin(settings)
            plugin.is_running = True
            plugin.api_client = AsyncMock()
            plugin.message_handler = AsyncMock()

        messages = [
            {
                "session_id": "session1",
                "message": "Hello",
                "id": 1,
                "timestamp": "2024-01-01T12:00:00Z",
            },
            {
                "session_id": "session2",
                "message": "World",
                "id": 2,
                "timestamp": "2024-01-01T12:01:00Z",
            },
        ]
        plugin.api_client.get_messages.return_value = messages

        # Set is_running to False before calling _poll_messages to simulate stopping
        plugin.is_running = False

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            mock_sleep.side_effect = asyncio.CancelledError()

            # The method catches CancelledError internally, so we don't expect it to be raised
            await plugin._poll_messages()

            # Should not process any messages since is_running is False
            assert len(plugin.processed_messages) == 0

    @pytest.mark.asyncio
    async def test_send_response_without_original_message(self):
        """Test sending response without original message."""
        plugin = WebChatPlugin()
        plugin.api_client = AsyncMock()
        plugin.api_client.post_response.return_value = True

        result = await plugin.send_response("session1", "Hello back!", None)

        assert result is True
        plugin.api_client.post_response.assert_called_once_with(
            "session1", "Hello back!"
        )

    @pytest.mark.asyncio
    async def test_handle_response_with_string_metadata(self):
        """Test response handling with string metadata."""
        plugin = WebChatPlugin()
        plugin.api_client = AsyncMock()
        plugin.api_client.post_response.return_value = True

        profile = Mock()
        profile.metadata = '{"session_id": "session1"}'
        message_id = 123

        await plugin._handle_response("Hello back!", profile, message_id)

        plugin.api_client.post_response.assert_called_once_with(
            "session1", "Hello back!"
        )

    @pytest.mark.asyncio
    async def test_handle_response_with_invalid_json_metadata(self):
        """Test response handling with invalid JSON metadata."""
        plugin = WebChatPlugin()
        plugin.api_client = AsyncMock()

        profile = Mock()
        profile.metadata = '{"invalid": json}'
        message_id = 123

        await plugin._handle_response("Hello back!", profile, message_id)

        plugin.api_client.post_response.assert_not_called()
