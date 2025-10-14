"""Comprehensive unit tests for plugins/telegram/handlers.py."""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from plugins.telegram.handlers import MessageBuffer, MessageHandler


class TestMessageBuffer:
    """Test cases for MessageBuffer class."""

    def test_message_buffer_init(self):
        """Test MessageBuffer initialization."""
        buffer = MessageBuffer(delay=10)
        assert buffer.delay == 10
        assert buffer.buffers == {}
        assert buffer.formatter is not None

    def test_message_buffer_init_default_delay(self):
        """Test MessageBuffer initialization with default delay."""
        buffer = MessageBuffer()
        assert buffer.delay == 5
        assert buffer.buffers == {}
        assert buffer.formatter is not None

    @pytest.mark.asyncio
    async def test_add_message_new_buffer(self):
        """Test adding message to new buffer."""
        buffer = MessageBuffer(delay=0.1)  # Short delay for testing

        with patch("asyncio.create_task") as mock_create_task:
            await buffer.add_message(
                platform_user_id=123,
                letta_user_id=456,
                platform_profile_id=789,
                message="Test message",
                timestamp=datetime.now(),
            )

            buffer_key = (123, 456, 789)
            assert buffer_key in buffer.buffers
            assert len(buffer.buffers[buffer_key]["messages"]) == 1
            assert buffer.buffers[buffer_key]["messages"][0][0] == "Test message"
            mock_create_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_message_existing_buffer(self):
        """Test adding message to existing buffer."""
        buffer = MessageBuffer(delay=0.1)
        buffer_key = (123, 456, 789)
        buffer.buffers[buffer_key] = {"messages": [], "task": None}

        with patch("asyncio.create_task") as mock_create_task:
            await buffer.add_message(
                platform_user_id=123,
                letta_user_id=456,
                platform_profile_id=789,
                message="First message",
                timestamp=datetime.now(),
            )

            await buffer.add_message(
                platform_user_id=123,
                letta_user_id=456,
                platform_profile_id=789,
                message="Second message",
                timestamp=datetime.now(),
            )

            assert len(buffer.buffers[buffer_key]["messages"]) == 2
            assert buffer.buffers[buffer_key]["messages"][0][0] == "First message"
            assert buffer.buffers[buffer_key]["messages"][1][0] == "Second message"
            assert mock_create_task.call_count == 2

    @pytest.mark.asyncio
    async def test_add_message_cancels_existing_task(self):
        """Test adding message cancels existing flush task."""
        buffer = MessageBuffer(delay=0.1)
        buffer_key = (123, 456, 789)
        mock_task = AsyncMock()
        buffer.buffers[buffer_key] = {"messages": [], "task": mock_task}

        with patch("asyncio.create_task") as mock_create_task:
            await buffer.add_message(
                platform_user_id=123,
                letta_user_id=456,
                platform_profile_id=789,
                message="Test message",
                timestamp=datetime.now(),
            )

            mock_task.cancel.assert_called_once()
            mock_create_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_schedule_flush_success(self):
        """Test successful flush scheduling."""
        buffer = MessageBuffer(delay=0.01)  # Very short delay
        buffer_key = (123, 456, 789)
        buffer.buffers[buffer_key] = {
            "messages": [("Test message", datetime.now())],
            "task": None,
        }

        with patch.object(
            buffer, "_flush_buffer", new_callable=AsyncMock
        ) as mock_flush:
            await buffer._schedule_flush(buffer_key)
            mock_flush.assert_called_once_with(buffer_key)

    @pytest.mark.asyncio
    async def test_schedule_flush_cancelled(self):
        """Test flush scheduling when cancelled."""
        buffer = MessageBuffer(delay=0.1)
        buffer_key = (123, 456, 789)
        buffer.buffers[buffer_key] = {
            "messages": [("Test message", datetime.now())],
            "task": None,
        }

        with patch("asyncio.sleep", side_effect=asyncio.CancelledError):
            await buffer._schedule_flush(buffer_key)
            # Should not raise exception

    @pytest.mark.asyncio
    async def test_schedule_flush_empty_buffer(self):
        """Test flush scheduling with empty buffer."""
        buffer = MessageBuffer(delay=0.01)
        buffer_key = (123, 456, 789)
        buffer.buffers[buffer_key] = {"messages": [], "task": None}

        with patch.object(
            buffer, "_flush_buffer", new_callable=AsyncMock
        ) as mock_flush:
            await buffer._schedule_flush(buffer_key)
            mock_flush.assert_not_called()

    @pytest.mark.asyncio
    async def test_schedule_flush_buffer_removed(self):
        """Test flush scheduling when buffer is removed."""
        buffer = MessageBuffer(delay=0.01)
        buffer_key = (123, 456, 789)
        buffer.buffers[buffer_key] = {
            "messages": [("Test message", datetime.now())],
            "task": None,
        }

        # Remove buffer before flush
        del buffer.buffers[buffer_key]

        with patch.object(
            buffer, "_flush_buffer", new_callable=AsyncMock
        ) as mock_flush:
            await buffer._schedule_flush(buffer_key)
            mock_flush.assert_not_called()

    @pytest.mark.asyncio
    async def test_flush_buffer_success(self):
        """Test successful buffer flush."""
        buffer = MessageBuffer()
        buffer_key = (123, 456, 789)
        timestamp = datetime.now()
        buffer.buffers[buffer_key] = {
            "messages": [("First message", timestamp), ("Second message", timestamp)],
            "task": None,
        }

        with patch(
            "plugins.telegram.handlers.insert_message", new_callable=AsyncMock
        ) as mock_insert, patch(
            "plugins.telegram.handlers.add_to_queue", new_callable=AsyncMock
        ) as mock_add_queue:
            mock_insert.return_value = 999

            await buffer._flush_buffer(buffer_key)

            mock_insert.assert_called_once()
            args = mock_insert.call_args
            assert args[1]["letta_user_id"] == 456
            assert args[1]["platform_profile_id"] == 789
            assert args[1]["role"] == "user"
            assert args[1]["message"] == "First message\nSecond message"

            mock_add_queue.assert_called_once_with(456, 999)

            # Buffer should be cleared
            assert buffer.buffers[buffer_key]["messages"] == []
            assert buffer.buffers[buffer_key]["task"] is None

    @pytest.mark.asyncio
    async def test_flush_buffer_empty_messages(self):
        """Test flush buffer with empty messages."""
        buffer = MessageBuffer()
        buffer_key = (123, 456, 789)
        buffer.buffers[buffer_key] = {"messages": [], "task": None}

        with patch(
            "plugins.telegram.handlers.insert_message", new_callable=AsyncMock
        ) as mock_insert:
            await buffer._flush_buffer(buffer_key)
            mock_insert.assert_not_called()

    @pytest.mark.asyncio
    async def test_flush_buffer_no_buffer(self):
        """Test flush buffer when buffer doesn't exist."""
        buffer = MessageBuffer()
        buffer_key = (123, 456, 789)

        with patch(
            "plugins.telegram.handlers.insert_message", new_callable=AsyncMock
        ) as mock_insert:
            await buffer._flush_buffer(buffer_key)
            mock_insert.assert_not_called()


class TestMessageHandler:
    """Test cases for MessageHandler class."""

    def test_message_handler_init(self):
        """Test MessageHandler initialization."""
        handler = MessageHandler()
        assert handler.formatter is not None
        assert handler.buffer is not None
        assert handler.message_mode == "echo"
        assert handler.telegram_plugin is None

    def test_message_handler_init_with_plugin(self):
        """Test MessageHandler initialization with plugin."""
        mock_plugin = MagicMock()
        handler = MessageHandler(telegram_plugin=mock_plugin)
        assert handler.telegram_plugin == mock_plugin

    def test_set_message_mode_valid(self):
        """Test setting valid message mode."""
        handler = MessageHandler()
        handler.set_message_mode("live")
        assert handler.message_mode == "live"

    def test_set_message_mode_invalid(self):
        """Test setting invalid message mode."""
        handler = MessageHandler()
        with pytest.raises(ValueError, match="Invalid message mode: invalid"):
            handler.set_message_mode("invalid")

    @pytest.mark.asyncio
    async def test_handle_private_message_success(self):
        """Test successful private message handling."""
        handler = MessageHandler()

        # Mock event
        mock_event = MagicMock()
        mock_event.is_private = True
        mock_event.text = "Hello world"
        mock_event.message.date = datetime.now()

        # Mock sender
        mock_sender = MagicMock()
        mock_sender.id = 123
        mock_sender.first_name = "John"
        mock_sender.username = "john_doe"
        mock_sender.bot = False
        mock_event.get_sender = AsyncMock(return_value=mock_sender)

        with patch(
            "plugins.telegram.handlers.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile, patch.object(
            handler.buffer, "add_message", new_callable=AsyncMock
        ) as mock_add_message:
            mock_profile = MagicMock()
            mock_profile.id = 456
            mock_letta_user = MagicMock()
            mock_letta_user.id = 789
            mock_get_profile.return_value = (mock_profile, mock_letta_user)

            await handler.handle_private_message(mock_event)

            mock_get_profile.assert_called_once_with(
                platform="telegram",
                platform_user_id="123",
                username="john_doe",
                display_name="John",
            )

            mock_add_message.assert_called_once_with(
                platform_user_id=123,
                letta_user_id=789,
                platform_profile_id=456,
                message="Hello world",
                timestamp=mock_event.message.date,
            )

    @pytest.mark.asyncio
    async def test_handle_private_message_non_private(self):
        """Test handling non-private message."""
        handler = MessageHandler()

        mock_event = MagicMock()
        mock_event.is_private = False

        with patch(
            "database.operations.users.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile:
            await handler.handle_private_message(mock_event)
            mock_get_profile.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_private_message_ignored_bot(self):
        """Test handling message from ignored bot."""
        mock_plugin = MagicMock()
        mock_plugin.is_bot_ignored.return_value = True
        handler = MessageHandler(telegram_plugin=mock_plugin)

        mock_event = MagicMock()
        mock_event.is_private = True
        mock_event.text = "Bot message"

        mock_sender = MagicMock()
        mock_sender.id = 123
        mock_sender.first_name = "Bot"
        mock_sender.username = "test_bot"
        mock_sender.bot = True
        mock_event.get_sender = AsyncMock(return_value=mock_sender)

        with patch(
            "database.operations.users.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile:
            await handler.handle_private_message(mock_event)
            mock_get_profile.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_private_message_bot_not_ignored(self):
        """Test handling message from bot that's not ignored."""
        mock_plugin = MagicMock()
        mock_plugin.is_bot_ignored.return_value = False
        handler = MessageHandler(telegram_plugin=mock_plugin)

        mock_event = MagicMock()
        mock_event.is_private = True
        mock_event.text = "Bot message"
        mock_event.message.date = datetime.now()

        mock_sender = MagicMock()
        mock_sender.id = 123
        mock_sender.first_name = "Bot"
        mock_sender.username = "test_bot"
        mock_sender.bot = True
        mock_event.get_sender = AsyncMock(return_value=mock_sender)

        with patch(
            "plugins.telegram.handlers.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile, patch.object(
            handler.buffer, "add_message", new_callable=AsyncMock
        ) as mock_add_message:
            mock_profile = MagicMock()
            mock_profile.id = 456
            mock_letta_user = MagicMock()
            mock_letta_user.id = 789
            mock_get_profile.return_value = (mock_profile, mock_letta_user)

            await handler.handle_private_message(mock_event)
            mock_get_profile.assert_called_once()
            mock_add_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_private_message_no_username(self):
        """Test handling message from user with no username."""
        handler = MessageHandler()

        mock_event = MagicMock()
        mock_event.is_private = True
        mock_event.text = "Hello world"
        mock_event.message.date = datetime.now()

        mock_sender = MagicMock()
        mock_sender.id = 123
        mock_sender.first_name = "John"
        mock_sender.username = None
        mock_sender.bot = False
        mock_event.get_sender = AsyncMock(return_value=mock_sender)

        with patch(
            "plugins.telegram.handlers.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile, patch.object(
            handler.buffer, "add_message", new_callable=AsyncMock
        ):
            mock_profile = MagicMock()
            mock_profile.id = 456
            mock_letta_user = MagicMock()
            mock_letta_user.id = 789
            mock_get_profile.return_value = (mock_profile, mock_letta_user)

            await handler.handle_private_message(mock_event)

            mock_get_profile.assert_called_once_with(
                platform="telegram",
                platform_user_id="123",
                username=None,
                display_name="John",
            )

    @pytest.mark.asyncio
    async def test_handle_private_message_no_first_name(self):
        """Test handling message from user with no first name."""
        handler = MessageHandler()

        mock_event = MagicMock()
        mock_event.is_private = True
        mock_event.text = "Hello world"
        mock_event.message.date = datetime.now()

        mock_sender = MagicMock()
        mock_sender.id = 123
        mock_sender.first_name = None
        mock_sender.username = "john_doe"
        mock_sender.bot = False
        mock_event.get_sender = AsyncMock(return_value=mock_sender)

        with patch(
            "plugins.telegram.handlers.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile, patch.object(
            handler.buffer, "add_message", new_callable=AsyncMock
        ):
            mock_profile = MagicMock()
            mock_profile.id = 456
            mock_letta_user = MagicMock()
            mock_letta_user.id = 789
            mock_get_profile.return_value = (mock_profile, mock_letta_user)

            await handler.handle_private_message(mock_event)

            mock_get_profile.assert_called_once_with(
                platform="telegram",
                platform_user_id="123",
                username="john_doe",
                display_name="Unknown",
            )

    @pytest.mark.asyncio
    async def test_handle_private_message_no_plugin(self):
        """Test handling message when no plugin is set."""
        handler = MessageHandler()  # No plugin

        mock_event = MagicMock()
        mock_event.is_private = True
        mock_event.text = "Hello world"
        mock_event.message.date = datetime.now()

        mock_sender = MagicMock()
        mock_sender.id = 123
        mock_sender.first_name = "John"
        mock_sender.username = "john_doe"
        mock_sender.bot = True  # Bot but no plugin to check
        mock_event.get_sender = AsyncMock(return_value=mock_sender)

        with patch(
            "plugins.telegram.handlers.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile, patch.object(
            handler.buffer, "add_message", new_callable=AsyncMock
        ) as mock_add_message:
            mock_profile = MagicMock()
            mock_profile.id = 456
            mock_letta_user = MagicMock()
            mock_letta_user.id = 789
            mock_get_profile.return_value = (mock_profile, mock_letta_user)

            await handler.handle_private_message(mock_event)

            # Should process the message even if it's from a bot when no plugin is set
            mock_get_profile.assert_called_once()
            mock_add_message.assert_called_once()
