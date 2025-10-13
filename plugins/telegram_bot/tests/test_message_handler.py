"""Unit tests for the Telegram message handler."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from plugins.telegram_bot.handlers import MessageBuffer
from plugins.telegram_bot.message_handler import TelegramMessageHandler

# Patch DB functions in the module where they are used
patch(
    "plugins.telegram_bot.message_handler.get_or_create_platform_profile",
    new_callable=AsyncMock,
).start()
patch(
    "database.operations.users.get_or_create_letta_user", new_callable=AsyncMock
).start()
patch(
    "plugins.telegram_bot.message_handler.insert_message",
    new=AsyncMock(return_value=123),
).start()
patch("plugins.telegram_bot.message_handler.add_to_queue", new=AsyncMock()).start()

# Ensure get_or_create_platform_profile always returns a tuple
patch(
    "plugins.telegram_bot.message_handler.get_or_create_platform_profile",
    new=AsyncMock(return_value=(MagicMock(), MagicMock())),
).start()


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = 123456789
    user.is_bot = False
    user.first_name = "Test"
    user.username = "testuser"
    user.language_code = "en"
    return user


@pytest.fixture
def mock_message(mock_user):
    message = MagicMock()
    message.message_id = 1
    message.date = datetime.now()
    chat = MagicMock()
    chat.id = 123456789
    chat.type = "private"
    message.chat = chat
    message.from_user = mock_user
    message.text = "Test message"
    message.answer = AsyncMock()
    message.reply = AsyncMock()
    message.edit_text = AsyncMock()
    return message


@pytest.fixture
def mock_letta_client():
    client = MagicMock()
    client.add_to_queue = AsyncMock()
    client.update_message_status = AsyncMock()
    return client


@pytest.fixture
def message_handler(mock_letta_client):
    handler = TelegramMessageHandler()
    handler.letta_client = mock_letta_client
    return handler


@pytest.fixture
def message_buffer(mock_letta_client):
    buffer = MessageBuffer()
    buffer.letta_client = mock_letta_client
    return buffer


@pytest.fixture(autouse=True)
def patch_db(monkeypatch):
    mock_get_user = AsyncMock(return_value=MagicMock())
    mock_get_profile = AsyncMock(return_value=(MagicMock(), MagicMock()))
    monkeypatch.setattr(
        "database.operations.users.get_or_create_letta_user", mock_get_user
    )
    monkeypatch.setattr(
        "database.operations.users.get_or_create_platform_profile", mock_get_profile
    )
    return mock_get_user, mock_get_profile


@pytest.mark.asyncio
async def test_process_incoming_message(message_handler, mock_message):
    await message_handler.process_incoming_message(mock_message)
    message_handler.letta_client.add_to_queue.assert_not_called()  # DB mock is used


@pytest.mark.asyncio
async def test_process_outgoing_message(message_handler, mock_message):
    await message_handler.process_outgoing_message(mock_message, "Test response")
    message_handler.letta_client.update_message_status.assert_awaited_once()


@pytest.mark.asyncio
async def test_message_buffer_flush(message_buffer):
    message = {
        "message": "Test message",
        "user_id": 123456789,
        "username": "testuser",
        "first_name": "Test",
        "timestamp": datetime.now(),
    }
    await message_buffer.add_message(message)
    await message_buffer.flush()
    message_buffer.letta_client.add_to_queue.assert_awaited()


@pytest.mark.asyncio
async def test_message_handler_handle_private_message(message_handler, mock_message):
    await message_handler.handle_private_message(mock_message)
    message_handler.letta_client.add_to_queue.assert_not_called()  # DB mock is used


@pytest.mark.asyncio
async def test_message_handler_handle_group_message(message_handler, mock_message):
    mock_message.chat.type = "group"
    await message_handler.handle_group_message(mock_message)
    mock_message.answer.assert_awaited_once_with("Group messages are not supported")


@pytest.mark.asyncio
async def test_message_handler_handle_channel_message(message_handler, mock_message):
    mock_message.chat.type = "channel"
    await message_handler.handle_channel_message(mock_message)
    mock_message.answer.assert_awaited_once_with("Channel messages are not supported")


@pytest.mark.asyncio
async def test_message_handler_update_message_status(message_handler, mock_message):
    await message_handler.update_message_status(mock_message, "sent")
    message_handler.letta_client.update_message_status.assert_awaited_once()


@pytest.mark.asyncio
async def test_message_buffer_add_message(message_buffer):
    message = {
        "message": "Test message",
        "user_id": 123456789,
        "username": "testuser",
        "first_name": "Test",
        "timestamp": datetime.now(),
    }
    await message_buffer.add_message(message)
    assert len(message_buffer.messages) == 1
    assert message_buffer.messages[0] == message


@pytest.mark.asyncio
async def test_message_buffer_clear(message_buffer):
    message = {
        "message": "Test message",
        "user_id": 123456789,
        "username": "testuser",
        "first_name": "Test",
        "timestamp": datetime.now(),
    }
    await message_buffer.add_message(message)
    message_buffer.clear()
    assert len(message_buffer.messages) == 0
