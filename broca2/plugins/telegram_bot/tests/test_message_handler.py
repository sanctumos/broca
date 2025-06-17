"""Unit tests for the Telegram message handler."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from plugins.telegram_bot.message_handler import TelegramMessageHandler
from plugins.telegram_bot.handlers import MessageHandler, MessageBuffer

@pytest.fixture
def message_handler(mock_letta_client):
    """Create a message handler instance for testing."""
    return TelegramMessageHandler()

@pytest.fixture
def message_buffer():
    """Create a message buffer instance for testing."""
    return MessageBuffer()

@pytest.fixture
def mock_message():
    """Create a mock message object."""
    return MagicMock()

@pytest.fixture
def mock_letta_client():
    """Create a mock Letta client."""
    return MagicMock()

@pytest.mark.asyncio
async def test_process_incoming_message(message_handler, mock_message, mock_letta_client):
    """Test processing incoming message."""
    await message_handler.process_incoming_message(mock_message)
    mock_letta_client.add_to_queue.assert_called_once()

@pytest.mark.asyncio
async def test_process_outgoing_message(message_handler, mock_message):
    """Test processing outgoing message."""
    with patch.object(message_handler, "update_message_status") as mock_update:
        await message_handler.process_outgoing_message(mock_message, "Test response")
        mock_update.assert_called_once()

@pytest.mark.asyncio
async def test_message_buffer_flush(message_buffer, mock_letta_client):
    """Test message buffer flush."""
    message = {
        "message": "Test message",
        "user_id": 123456789,
        "username": "testuser",
        "first_name": "Test",
        "timestamp": datetime.now()
    }
    message_buffer.add_message(message)
    await message_buffer.flush()
    mock_letta_client.add_to_queue.assert_called_once()

@pytest.mark.asyncio
async def test_message_handler_handle_private_message(message_handler, mock_message, mock_letta_client):
    """Test handling private message."""
    await message_handler.handle_private_message(mock_message)
    mock_letta_client.add_to_queue.assert_called_once()

@pytest.mark.asyncio
async def test_message_handler_handle_group_message(message_handler, mock_message):
    """Test handling group message."""
    mock_message.chat.type = "group"
    await message_handler.handle_group_message(mock_message)
    mock_message.answer.assert_called_once()

@pytest.mark.asyncio
async def test_message_handler_handle_channel_message(message_handler, mock_message):
    """Test handling channel message."""
    mock_message.chat.type = "channel"
    await message_handler.handle_channel_message(mock_message)
    mock_message.answer.assert_called_once()

@pytest.mark.asyncio
async def test_message_handler_update_message_status(message_handler, mock_message):
    """Test updating message status."""
    with patch.object(message_handler, "update_message_status") as mock_update:
        await message_handler.update_message_status(mock_message, "sent")
        mock_update.assert_called_once()

@pytest.mark.asyncio
async def test_message_buffer_add_message(message_buffer):
    """Test adding message to buffer."""
    message = {
        "message": "Test message",
        "user_id": 123456789,
        "username": "testuser",
        "first_name": "Test",
        "timestamp": datetime.now()
    }
    message_buffer.add_message(message)
    assert len(message_buffer.messages) == 1
    assert message_buffer.messages[0] == message

@pytest.mark.asyncio
async def test_message_buffer_clear(message_buffer):
    """Test clearing message buffer."""
    message = {
        "message": "Test message",
        "user_id": 123456789,
        "username": "testuser",
        "first_name": "Test",
        "timestamp": datetime.now()
    }
    message_buffer.add_message(message)
    message_buffer.clear()
    assert len(message_buffer.messages) == 0 