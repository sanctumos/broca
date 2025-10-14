"""Tests for Telegram message handlers."""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from plugins.telegram.handlers import MessageBuffer, MessageHandler


class TestMessageBuffer:
    """Test the MessageBuffer class."""

    def test_init_default_delay(self):
        """Test MessageBuffer initialization with default delay."""
        buffer = MessageBuffer()
        assert buffer.delay == 5
        assert buffer.buffers == {}
        assert buffer.formatter is not None

    def test_init_custom_delay(self):
        """Test MessageBuffer initialization with custom delay."""
        buffer = MessageBuffer(delay=10)
        assert buffer.delay == 10
        assert buffer.buffers == {}
        assert buffer.formatter is not None

    @pytest.mark.asyncio
    async def test_add_message_new_user(self):
        """Test adding message for new user."""
        buffer = MessageBuffer(delay=0.1)

        with patch("asyncio.create_task") as mock_create_task:
            await buffer.add_message(
                platform_user_id=123,
                letta_user_id=456,
                platform_profile_id=789,
                message="Hello world",
                timestamp=datetime.now(),
            )

            # Check buffer was created
            buffer_key = (123, 456, 789)
            assert buffer_key in buffer.buffers
            assert len(buffer.buffers[buffer_key]["messages"]) == 1
            assert buffer.buffers[buffer_key]["messages"][0][0] == "Hello world"
            assert buffer.buffers[buffer_key]["task"] is not None

            # Check task was created
            mock_create_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_message_existing_user(self):
        """Test adding message for existing user."""
        buffer = MessageBuffer(delay=0.1)
        buffer_key = (123, 456, 789)

        # Add first message
        with patch("asyncio.create_task"):
            await buffer.add_message(
                platform_user_id=123,
                letta_user_id=456,
                platform_profile_id=789,
                message="First message",
                timestamp=datetime.now(),
            )

            # Add second message
            await buffer.add_message(
                platform_user_id=123,
                letta_user_id=456,
                platform_profile_id=789,
                message="Second message",
                timestamp=datetime.now(),
            )

            # Check both messages are in buffer
            assert len(buffer.buffers[buffer_key]["messages"]) == 2
            assert buffer.buffers[buffer_key]["messages"][0][0] == "First message"
            assert buffer.buffers[buffer_key]["messages"][1][0] == "Second message"

    @pytest.mark.asyncio
    async def test_schedule_flush_success(self):
        """Test successful flush scheduling."""
        buffer = MessageBuffer(delay=0.01)
        buffer_key = (123, 456, 789)

        # Add message to buffer
        buffer.buffers[buffer_key] = {
            "messages": [("test message", datetime.now())],
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
        buffer = MessageBuffer(delay=0.01)
        buffer_key = (123, 456, 789)

        # Add message to buffer
        buffer.buffers[buffer_key] = {
            "messages": [("test message", datetime.now())],
            "task": None,
        }

        # Create a task that will be cancelled
        async def cancel_task():
            await asyncio.sleep(0.005)
            raise asyncio.CancelledError()

        with patch("asyncio.sleep", side_effect=cancel_task):
            await buffer._schedule_flush(buffer_key)
            # Should not raise exception

    @pytest.mark.asyncio
    async def test_schedule_flush_empty_buffer(self):
        """Test flush scheduling with empty buffer."""
        buffer = MessageBuffer(delay=0.01)
        buffer_key = (123, 456, 789)

        # Add empty buffer
        buffer.buffers[buffer_key] = {"messages": [], "task": None}

        with patch.object(
            buffer, "_flush_buffer", new_callable=AsyncMock
        ) as mock_flush:
            await buffer._schedule_flush(buffer_key)
            # Should not call flush for empty buffer
            mock_flush.assert_not_called()

    @pytest.mark.asyncio
    async def test_schedule_flush_missing_buffer(self):
        """Test flush scheduling with missing buffer."""
        buffer = MessageBuffer(delay=0.01)
        buffer_key = (123, 456, 789)

        with patch.object(
            buffer, "_flush_buffer", new_callable=AsyncMock
        ) as mock_flush:
            await buffer._schedule_flush(buffer_key)
            # Should not call flush for missing buffer
            mock_flush.assert_not_called()

    @pytest.mark.asyncio
    async def test_flush_buffer_success(self):
        """Test successful buffer flush."""
        buffer = MessageBuffer()
        buffer_key = (123, 456, 789)

        # Add messages to buffer
        buffer.buffers[buffer_key] = {
            "messages": [
                ("First message", datetime(2023, 1, 1, 12, 0, 0)),
                ("Second message", datetime(2023, 1, 1, 12, 1, 0)),
            ],
            "task": None,
        }

        with patch(
            "database.operations.messages.insert_message", new_callable=AsyncMock
        ) as mock_insert, patch(
            "database.operations.queue.add_to_queue", new_callable=AsyncMock
        ) as mock_add_queue:
            mock_insert.return_value = 999

            await buffer._flush_buffer(buffer_key)

            # Check database calls
            mock_insert.assert_called_once_with(
                letta_user_id=456,
                platform_profile_id=789,
                role="user",
                message="First message\nSecond message",
                timestamp="2023-01-01 12:00 UTC",
            )
            mock_add_queue.assert_called_once_with(456, 999)

            # Check buffer was cleared
            assert buffer.buffers[buffer_key]["messages"] == []
            assert buffer.buffers[buffer_key]["task"] is None

    @pytest.mark.asyncio
    async def test_flush_buffer_empty(self):
        """Test flush buffer with empty messages."""
        buffer = MessageBuffer()
        buffer_key = (123, 456, 789)

        # Add empty buffer
        buffer.buffers[buffer_key] = {"messages": [], "task": None}

        with patch(
            "database.operations.messages.insert_message", new_callable=AsyncMock
        ) as mock_insert, patch(
            "database.operations.queue.add_to_queue", new_callable=AsyncMock
        ) as mock_add_queue:
            await buffer._flush_buffer(buffer_key)

            # Should not call database functions
            mock_insert.assert_not_called()
            mock_add_queue.assert_not_called()

    @pytest.mark.asyncio
    async def test_flush_buffer_missing(self):
        """Test flush buffer with missing buffer."""
        buffer = MessageBuffer()
        buffer_key = (123, 456, 789)

        with patch(
            "database.operations.messages.insert_message", new_callable=AsyncMock
        ) as mock_insert, patch(
            "database.operations.queue.add_to_queue", new_callable=AsyncMock
        ) as mock_add_queue:
            await buffer._flush_buffer(buffer_key)

            # Should not call database functions
            mock_insert.assert_not_called()
            mock_add_queue.assert_not_called()


class TestMessageHandler:
    """Test the MessageHandler class."""

    def test_init_default(self):
        """Test MessageHandler initialization with defaults."""
        handler = MessageHandler()
        assert handler.formatter is not None
        assert handler.buffer is not None
        assert handler.message_mode == "echo"
        assert handler.telegram_plugin is None

    def test_init_with_plugin(self):
        """Test MessageHandler initialization with plugin."""
        mock_plugin = MagicMock()
        handler = MessageHandler(telegram_plugin=mock_plugin)
        assert handler.telegram_plugin == mock_plugin

    def test_set_message_mode_valid(self):
        """Test setting valid message modes."""
        handler = MessageHandler()

        for mode in ["echo", "listen", "live"]:
            handler.set_message_mode(mode)
            assert handler.message_mode == mode

    def test_set_message_mode_invalid(self):
        """Test setting invalid message mode."""
        handler = MessageHandler()

        with pytest.raises(ValueError, match="Invalid message mode: invalid"):
            handler.set_message_mode("invalid")

    @pytest.mark.asyncio
    async def test_handle_private_message_success(self):
        """Test handling private message successfully."""
        handler = MessageHandler()

        # Mock event
        mock_event = MagicMock()
        mock_event.is_private = True
        mock_event.text = "Hello world"
        mock_event.message.date = datetime.now()

        # Mock sender
        mock_sender = MagicMock()
        mock_sender.bot = False
        mock_sender.id = 123
        mock_sender.first_name = "John"
        mock_sender.username = "john_doe"

        mock_event.get_sender = AsyncMock(return_value=mock_sender)

        with patch(
            "database.operations.users.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile, patch.object(
            handler.buffer, "add_message", new_callable=AsyncMock
        ) as mock_add_message:
            # Mock profile and user
            mock_profile = MagicMock()
            mock_profile.id = 456
            mock_user = MagicMock()
            mock_user.id = 789
            mock_get_profile.return_value = (mock_profile, mock_user)

            await handler.handle_private_message(mock_event)

            # Check profile was retrieved
            mock_get_profile.assert_called_once_with(
                platform="telegram",
                platform_user_id="123",
                username="john_doe",
                display_name="John",
            )

            # Check message was added to buffer
            mock_add_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_private_message_non_private(self):
        """Test handling non-private message."""
        handler = MessageHandler()

        # Mock event
        mock_event = MagicMock()
        mock_event.is_private = False

        with patch(
            "database.operations.users.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile, patch.object(
            handler.buffer, "add_message", new_callable=AsyncMock
        ) as mock_add_message:
            await handler.handle_private_message(mock_event)

            # Should not process non-private messages
            mock_get_profile.assert_not_called()
            mock_add_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_private_message_ignored_bot(self):
        """Test handling message from ignored bot."""
        mock_plugin = MagicMock()
        mock_plugin.is_bot_ignored.return_value = True
        handler = MessageHandler(telegram_plugin=mock_plugin)

        # Mock event
        mock_event = MagicMock()
        mock_event.is_private = True
        mock_event.text = "Bot message"
        mock_event.message.date = datetime.now()

        # Mock sender (bot)
        mock_sender = MagicMock()
        mock_sender.bot = True
        mock_sender.id = 123
        mock_sender.first_name = "Bot"
        mock_sender.username = "test_bot"

        mock_event.get_sender = AsyncMock(return_value=mock_sender)

        with patch(
            "database.operations.users.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile, patch.object(
            handler.buffer, "add_message", new_callable=AsyncMock
        ) as mock_add_message:
            await handler.handle_private_message(mock_event)

            # Should not process ignored bot messages
            mock_get_profile.assert_not_called()
            mock_add_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_private_message_bot_not_ignored(self):
        """Test handling message from bot that's not ignored."""
        mock_plugin = MagicMock()
        mock_plugin.is_bot_ignored.return_value = False
        handler = MessageHandler(telegram_plugin=mock_plugin)

        # Mock event
        mock_event = MagicMock()
        mock_event.is_private = True
        mock_event.text = "Bot message"
        mock_event.message.date = datetime.now()

        # Mock sender (bot)
        mock_sender = MagicMock()
        mock_sender.bot = True
        mock_sender.id = 123
        mock_sender.first_name = "Bot"
        mock_sender.username = "test_bot"

        mock_event.get_sender = AsyncMock(return_value=mock_sender)

        with patch(
            "database.operations.users.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile, patch.object(
            handler.buffer, "add_message", new_callable=AsyncMock
        ) as mock_add_message:
            # Mock profile and user
            mock_profile = MagicMock()
            mock_profile.id = 456
            mock_user = MagicMock()
            mock_user.id = 789
            mock_get_profile.return_value = (mock_profile, mock_user)

            await handler.handle_private_message(mock_event)

            # Should process non-ignored bot messages
            mock_get_profile.assert_called_once()
            mock_add_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_private_message_no_username(self):
        """Test handling message from user with no username."""
        handler = MessageHandler()

        # Mock event
        mock_event = MagicMock()
        mock_event.is_private = True
        mock_event.text = "Hello world"
        mock_event.message.date = datetime.now()

        # Mock sender without username
        mock_sender = MagicMock()
        mock_sender.bot = False
        mock_sender.id = 123
        mock_sender.first_name = "John"
        mock_sender.username = None

        mock_event.get_sender = AsyncMock(return_value=mock_sender)

        with patch(
            "database.operations.users.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile, patch.object(
            handler.buffer, "add_message", new_callable=AsyncMock
        ):
            # Mock profile and user
            mock_profile = MagicMock()
            mock_profile.id = 456
            mock_user = MagicMock()
            mock_user.id = 789
            mock_get_profile.return_value = (mock_profile, mock_user)

            await handler.handle_private_message(mock_event)

            # Check profile was retrieved with None username
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

        # Mock event
        mock_event = MagicMock()
        mock_event.is_private = True
        mock_event.text = "Hello world"
        mock_event.message.date = datetime.now()

        # Mock sender without first name
        mock_sender = MagicMock()
        mock_sender.bot = False
        mock_sender.id = 123
        mock_sender.first_name = None
        mock_sender.username = "john_doe"

        mock_event.get_sender = AsyncMock(return_value=mock_sender)

        with patch(
            "database.operations.users.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile, patch.object(
            handler.buffer, "add_message", new_callable=AsyncMock
        ):
            # Mock profile and user
            mock_profile = MagicMock()
            mock_profile.id = 456
            mock_user = MagicMock()
            mock_user.id = 789
            mock_get_profile.return_value = (mock_profile, mock_user)

            await handler.handle_private_message(mock_event)

            # Check profile was retrieved with "Unknown" display name
            mock_get_profile.assert_called_once_with(
                platform="telegram",
                platform_user_id="123",
                username="john_doe",
                display_name="Unknown",
            )
