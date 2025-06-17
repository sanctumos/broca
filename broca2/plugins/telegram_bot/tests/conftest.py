"""Test configuration and fixtures."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import os
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.types import User, Message, Chat

@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for all tests."""
    with patch.dict(os.environ, {
        "AGENT_ENDPOINT": "http://test.endpoint",
        "AGENT_API_KEY": "test_api_key",
        "TELEGRAM_BOT_TOKEN": "1234567890:test_token",
        "TELEGRAM_OWNER_ID": "123456789",
        "TELEGRAM_MESSAGE_MODE": "echo",
        "TELEGRAM_BUFFER_DELAY": "5"
    }):
        yield

@pytest.fixture
def mock_letta_client():
    """Mock Letta client."""
    with patch("runtime.core.letta_client.LettaClient") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client

@pytest.fixture
def mock_bot():
    """Create a mock bot."""
    bot = AsyncMock(spec=Bot)
    bot.session = AsyncMock()
    return bot

@pytest.fixture
def mock_dispatcher():
    """Create a mock dispatcher."""
    return AsyncMock(spec=Dispatcher)

@pytest.fixture
def mock_user():
    """Create a mock user."""
    return User(
        id=123456789,
        is_bot=False,
        first_name="Test",
        username="testuser",
        language_code="en"
    )

@pytest.fixture
def mock_message(mock_user):
    """Create a mock message."""
    message = Message(
        message_id=1,
        date=datetime.now(),
        chat=Chat(id=123456789, type="private"),
        from_user=mock_user,
        text="Test message"
    )
    message.answer = AsyncMock()
    return message

@pytest.fixture
def mock_event():
    """Create a mock message event."""
    return {
        "message": "Test message",
        "user_id": 123456789,
        "username": "testuser",
        "first_name": "Test",
        "timestamp": datetime.now()
    } 