"""Comprehensive tests for plugins/telegram_bot/handlers.py."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from plugins.telegram_bot.handlers import MessageBuffer, MessageHandler


class TestMessageBuffer:
    """Test cases for MessageBuffer class."""

    def test_initialization_default_delay(self):
        """Test MessageBuffer initialization with default delay."""
        buffer = MessageBuffer()
        assert buffer.delay == 5
        assert buffer.messages == []
        assert buffer.letta_client is None

    def test_initialization_custom_delay(self):
        """Test MessageBuffer initialization with custom delay."""
        buffer = MessageBuffer(delay=10)
        assert buffer.delay == 10
        assert buffer.messages == []
        assert buffer.letta_client is None

    @pytest.mark.asyncio
    async def test_add_message_first_message(self):
        """Test adding first message starts flush timer."""
        buffer = MessageBuffer(delay=0.1)

        with patch("asyncio.create_task") as mock_create_task:
            await buffer.add_message({"test": "message"})

            assert len(buffer.messages) == 1
            assert buffer.messages[0] == {"test": "message"}
            mock_create_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_message_subsequent_messages(self):
        """Test adding subsequent messages doesn't start new timer."""
        buffer = MessageBuffer(delay=0.1)

        # Add first message
        with patch("asyncio.create_task") as mock_create_task:
            await buffer.add_message({"test": "message1"})
            mock_create_task.assert_called_once()

        # Add second message
        with patch("asyncio.create_task") as mock_create_task2:
            await buffer.add_message({"test": "message2"})
            mock_create_task2.assert_not_called()

        assert len(buffer.messages) == 2

    @pytest.mark.asyncio
    async def test_delayed_flush(self):
        """Test delayed flush functionality."""
        buffer = MessageBuffer(delay=0.1)

        with patch.object(buffer, "flush") as mock_flush:
            await buffer._delayed_flush()
            mock_flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_flush_empty_buffer(self):
        """Test flushing empty buffer."""
        buffer = MessageBuffer()

        # Should return early without error
        await buffer.flush()
        assert len(buffer.messages) == 0

    @pytest.mark.asyncio
    async def test_flush_with_letta_client_initialization(self):
        """Test flush with letta_client initialization."""
        buffer = MessageBuffer()
        buffer.messages = [
            {
                "message": "test message",
                "user_id": "123",
                "username": "testuser",
                "first_name": "Test",
                "timestamp": datetime.now(),
            }
        ]

        mock_letta_client = AsyncMock()
        mock_letta_client.add_to_queue = AsyncMock()

        with patch(
            "plugins.telegram_bot.handlers.LettaClient", return_value=mock_letta_client
        ):
            await buffer.flush()

            mock_letta_client.add_to_queue.assert_called_once()
            assert len(buffer.messages) == 0

    @pytest.mark.asyncio
    async def test_flush_with_existing_letta_client(self):
        """Test flush with existing letta_client."""
        buffer = MessageBuffer()
        buffer.messages = [
            {
                "message": "test message",
                "user_id": "123",
                "username": "testuser",
                "first_name": "Test",
                "timestamp": datetime.now(),
            }
        ]

        mock_letta_client = AsyncMock()
        mock_letta_client.add_to_queue = AsyncMock()
        buffer.letta_client = mock_letta_client

        await buffer.flush()

        mock_letta_client.add_to_queue.assert_called_once()
        assert len(buffer.messages) == 0

    @pytest.mark.asyncio
    async def test_flush_import_error(self):
        """Test flush with ImportError."""
        buffer = MessageBuffer()
        buffer.messages = [{"test": "message"}]

        with patch(
            "plugins.telegram_bot.handlers.LettaClient",
            side_effect=ImportError("Module not found"),
        ):
            with pytest.raises(ImportError, match="Module not found"):
                await buffer.flush()

    @pytest.mark.asyncio
    async def test_flush_general_exception(self):
        """Test flush with general exception."""
        buffer = MessageBuffer()
        buffer.messages = [
            {
                "message": "test message",
                "user_id": "123",
                "username": "testuser",
                "first_name": "Test",
                "timestamp": datetime.now(),
            }
        ]

        mock_letta_client = AsyncMock()
        mock_letta_client.add_to_queue.side_effect = Exception("Test error")

        with patch(
            "runtime.core.letta_client.LettaClient", return_value=mock_letta_client
        ):
            with pytest.raises(Exception, match="Test error"):
                await buffer.flush()

    @pytest.mark.asyncio
    async def test_flush_clears_messages_on_exception(self):
        """Test that flush clears messages even on exception."""
        buffer = MessageBuffer()
        buffer.messages = [
            {
                "message": "test message",
                "user_id": "123",
                "username": "testuser",
                "first_name": "Test",
                "timestamp": datetime.now(),
            }
        ]

        mock_letta_client = AsyncMock()
        mock_letta_client.add_to_queue.side_effect = Exception("Test error")

        with patch(
            "runtime.core.letta_client.LettaClient", return_value=mock_letta_client
        ):
            try:
                await buffer.flush()
            except Exception:
                pass

            # Messages should be cleared even on exception
            assert len(buffer.messages) == 0

    def test_clear(self):
        """Test clearing messages."""
        buffer = MessageBuffer()
        buffer.messages = [{"test": "message1"}, {"test": "message2"}]

        buffer.clear()
        assert len(buffer.messages) == 0


class TestMessageHandler:
    """Test cases for MessageHandler class."""

    def test_initialization_default_delay(self):
        """Test MessageHandler initialization with default delay."""
        handler = MessageHandler()
        assert handler.buffer.delay == 5
        assert handler.letta_client is None

    def test_initialization_custom_delay(self):
        """Test MessageHandler initialization with custom delay."""
        handler = MessageHandler(buffer_delay=10)
        assert handler.buffer.delay == 10
        assert handler.letta_client is None

    @pytest.mark.asyncio
    async def test_handle_message(self):
        """Test handle_message delegates to buffer."""
        handler = MessageHandler()

        with patch.object(
            handler.buffer, "add_message", new_callable=AsyncMock
        ) as mock_add:
            message = {"test": "message"}
            await handler.handle_message(message)
            mock_add.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_process_message_with_letta_client_initialization(self):
        """Test process_message with letta_client initialization."""
        handler = MessageHandler()

        mock_letta_client = AsyncMock()
        mock_letta_client.add_to_queue = AsyncMock()

        message = {
            "message": "test message",
            "user_id": "123",
            "username": "testuser",
            "first_name": "Test",
            "timestamp": datetime.now(),
        }

        with patch(
            "runtime.core.letta_client.LettaClient", return_value=mock_letta_client
        ):
            await handler.process_message(message)

            mock_letta_client.add_to_queue.assert_called_once()
            assert handler.letta_client == mock_letta_client

    @pytest.mark.asyncio
    async def test_process_message_with_existing_letta_client(self):
        """Test process_message with existing letta_client."""
        handler = MessageHandler()

        mock_letta_client = AsyncMock()
        mock_letta_client.add_to_queue = AsyncMock()
        handler.letta_client = mock_letta_client

        message = {
            "message": "test message",
            "user_id": "123",
            "username": "testuser",
            "first_name": "Test",
            "timestamp": datetime.now(),
        }

        await handler.process_message(message)
        mock_letta_client.add_to_queue.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_message_import_error(self):
        """Test process_message with ImportError."""
        handler = MessageHandler()

        message = {"test": "message"}

        with patch(
            "runtime.core.letta_client.LettaClient",
            side_effect=ImportError("Module not found"),
        ):
            with pytest.raises(ImportError, match="Module not found"):
                await handler.process_message(message)

    @pytest.mark.asyncio
    async def test_process_message_general_exception(self):
        """Test process_message with general exception."""
        handler = MessageHandler()

        mock_letta_client = AsyncMock()
        mock_letta_client.add_to_queue.side_effect = Exception("Test error")

        message = {
            "message": "test message",
            "user_id": "123",
            "username": "testuser",
            "first_name": "Test",
            "timestamp": datetime.now(),
        }

        with patch(
            "runtime.core.letta_client.LettaClient", return_value=mock_letta_client
        ):
            with pytest.raises(Exception, match="Test error"):
                await handler.process_message(message)

    def test_set_message_mode_valid_modes(self):
        """Test set_message_mode with valid modes."""
        handler = MessageHandler()

        for mode in ["echo", "listen", "live"]:
            handler.set_message_mode(mode)
            assert handler.message_mode == mode

    def test_set_message_mode_invalid_mode(self):
        """Test set_message_mode with invalid mode."""
        handler = MessageHandler()

        with pytest.raises(ValueError, match="Invalid message mode: invalid"):
            handler.set_message_mode("invalid")

    @pytest.mark.asyncio
    async def test_handle_private_message(self):
        """Test handle_private_message functionality."""
        handler = MessageHandler()

        # Mock the formatter
        handler.formatter = MagicMock()
        handler.formatter.sanitize_text.side_effect = lambda x: x if x else "Unknown"

        # Mock get_or_create_platform_profile
        mock_profile = MagicMock()
        mock_letta_user = MagicMock()
        mock_letta_user.id = "letta_123"

        event = {
            "message": "Hello world",
            "user_id": 123,
            "username": "testuser",
            "first_name": "Test User",
        }

        with patch(
            "plugins.telegram_bot.handlers.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile:
            mock_get_profile.return_value = (mock_profile, mock_letta_user)

            with patch.object(
                handler.buffer, "add_message", new_callable=AsyncMock
            ) as mock_add:
                await handler.handle_private_message(event)

                mock_get_profile.assert_called_once_with(
                    platform="telegram",
                    platform_user_id="123",
                    username="testuser",
                    display_name="Test User",
                )

                mock_add.assert_called_once()
                call_args = mock_add.call_args[0][0]
                assert call_args["user_id"] == "letta_123"
                assert call_args["username"] == "testuser"
                assert call_args["first_name"] == "Test User"
                assert call_args["message"] == "Hello world"
                assert isinstance(call_args["timestamp"], datetime)

    @pytest.mark.asyncio
    async def test_handle_private_message_no_username(self):
        """Test handle_private_message with no username."""
        handler = MessageHandler()

        # Mock the formatter
        handler.formatter = MagicMock()
        handler.formatter.sanitize_text.side_effect = lambda x: x if x else "Unknown"

        # Mock get_or_create_platform_profile
        mock_profile = MagicMock()
        mock_letta_user = MagicMock()
        mock_letta_user.id = "letta_123"

        event = {
            "message": "Hello world",
            "user_id": 123,
            "username": None,
            "first_name": "Test User",
        }

        with patch(
            "plugins.telegram_bot.handlers.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile:
            mock_get_profile.return_value = (mock_profile, mock_letta_user)

            with patch.object(handler.buffer, "add_message", new_callable=AsyncMock):
                await handler.handle_private_message(event)

                mock_get_profile.assert_called_once_with(
                    platform="telegram",
                    platform_user_id="123",
                    username=None,
                    display_name="Test User",
                )

    @pytest.mark.asyncio
    async def test_handle_private_message_no_first_name(self):
        """Test handle_private_message with no first_name."""
        handler = MessageHandler()

        # Mock the formatter
        handler.formatter = MagicMock()
        handler.formatter.sanitize_text.side_effect = lambda x: x if x else "Unknown"

        # Mock get_or_create_platform_profile
        mock_profile = MagicMock()
        mock_letta_user = MagicMock()
        mock_letta_user.id = "letta_123"

        event = {
            "message": "Hello world",
            "user_id": 123,
            "username": "testuser",
            "first_name": None,
        }

        with patch(
            "plugins.telegram_bot.handlers.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile:
            mock_get_profile.return_value = (mock_profile, mock_letta_user)

            with patch.object(handler.buffer, "add_message", new_callable=AsyncMock):
                await handler.handle_private_message(event)

                mock_get_profile.assert_called_once_with(
                    platform="telegram",
                    platform_user_id="123",
                    username="testuser",
                    display_name="Unknown",
                )

    @pytest.mark.asyncio
    async def test_handle_private_message_sanitizes_input(self):
        """Test handle_private_message sanitizes user input."""
        handler = MessageHandler()

        # Mock the formatter
        handler.formatter = MagicMock()
        handler.formatter.sanitize_text.side_effect = (
            lambda x: f"sanitized_{x}" if x else "Unknown"
        )

        # Mock get_or_create_platform_profile
        mock_profile = MagicMock()
        mock_letta_user = MagicMock()
        mock_letta_user.id = "letta_123"

        event = {
            "message": "Hello world",
            "user_id": 123,
            "username": "testuser",
            "first_name": "Test User",
        }

        with patch(
            "plugins.telegram_bot.handlers.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile:
            mock_get_profile.return_value = (mock_profile, mock_letta_user)

            with patch.object(
                handler.buffer, "add_message", new_callable=AsyncMock
            ) as mock_add:
                await handler.handle_private_message(event)

                # Verify sanitize_text was called
                assert handler.formatter.sanitize_text.call_count >= 3

                call_args = mock_add.call_args[0][0]
                assert call_args["message"] == "sanitized_Hello world"
                assert call_args["username"] == "sanitized_testuser"
                assert call_args["first_name"] == "sanitized_Test User"
