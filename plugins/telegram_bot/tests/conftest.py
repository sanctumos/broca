"""Test configuration and fixtures."""

import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram import Bot, Dispatcher


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for all tests."""
    with patch.dict(
        os.environ,
        {
            "AGENT_ENDPOINT": "http://test.endpoint",
            "AGENT_API_KEY": "test_api_key",
            "TELEGRAM_BOT_TOKEN": "1234567890:test_token",
            "TELEGRAM_OWNER_ID": "123456789",
            "TELEGRAM_MESSAGE_MODE": "echo",
            "TELEGRAM_BUFFER_DELAY": "5",
        },
    ):
        yield


@pytest.fixture(autouse=True)
def patch_db_ops():
    with (
        patch(
            "database.operations.users.get_or_create_letta_user", new_callable=AsyncMock
        ) as mock_get_user,
        patch(
            "database.operations.users.get_or_create_platform_profile",
            new_callable=AsyncMock,
        ) as mock_get_profile,
    ):
        mock_get_user.return_value = MagicMock()
        mock_get_profile.return_value = (MagicMock(), MagicMock())
        yield


@pytest.fixture(autouse=True)
def mock_letta_client():
    with patch("runtime.core.letta_client.LettaClient") as mock_class:
        instance = MagicMock()
        # Add all required async methods
        instance.add_to_queue = AsyncMock()
        instance.update_message_status = AsyncMock()
        instance.get_or_create_user = AsyncMock()
        instance.get_or_create_platform_profile = AsyncMock()
        mock_class.return_value = instance
        yield instance


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
    user = MagicMock()
    user.id = 123456789
    user.is_bot = False
    user.first_name = "Test"
    user.username = "testuser"
    user.language_code = "en"
    return user


@pytest.fixture
def mock_message(mock_user):
    """Create a mock message."""
    # Create a fully mocked message object
    message = MagicMock()
    message.message_id = 1
    message.date = datetime.now()

    # Create a mutable chat object
    chat = MagicMock()
    chat.id = 123456789
    chat.type = "private"
    message.chat = chat

    # Set user and text
    message.from_user = mock_user
    message.text = "Test message"

    # Mock the answer method
    message.answer = AsyncMock()

    # Mock any other required methods
    message.reply = AsyncMock()
    message.edit_text = AsyncMock()

    return message


@pytest.fixture
def mock_event():
    """Create a mock message event."""
    return {
        "message": "Test message",
        "user_id": 123456789,
        "username": "testuser",
        "first_name": "Test",
        "timestamp": datetime.now(),
    }
