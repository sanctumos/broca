"""Unit tests for the Telegram bot plugin."""
from unittest.mock import AsyncMock, MagicMock, patch

# Patch DB and LettaClient at the module level before any code under test is imported
patch("database.operations.users.get_or_create_letta_user", new_callable=AsyncMock).start()
patch("database.operations.users.get_or_create_platform_profile", new_callable=AsyncMock).start()
patch("runtime.core.letta_client.LettaClient").start()

import pytest
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.types import User, Message, Chat

from plugins.telegram_bot.plugin import TelegramBotPlugin
from plugins.telegram_bot.settings import TelegramBotSettings, MessageMode

@pytest.fixture
def mock_bot():
    """Create a mock bot."""
    return AsyncMock(spec=Bot)

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
def plugin():
    return TelegramBotPlugin()

@pytest.fixture
def mock_bot():
    bot = MagicMock()
    bot.send_message = AsyncMock()
    return bot

@pytest.mark.asyncio
async def test_plugin_initialization(plugin):
    """Test plugin initialization."""
    assert plugin.get_name() == "Telegram Bot"
    assert plugin.get_platform() == "telegram"
    assert plugin.get_message_handler() is not None
    assert plugin.get_settings() is not None

@pytest.mark.asyncio
async def test_plugin_start(plugin):
    """Test plugin start."""
    with patch("aiogram.Bot", new_callable=AsyncMock) as mock_bot, \
         patch("aiogram.Dispatcher.start_polling", new_callable=AsyncMock) as mock_poll:
        plugin.bot = mock_bot
        plugin.dp = MagicMock()
        plugin.dp.start_polling = mock_poll
        await plugin.start()
        assert plugin.bot is not None
        assert plugin.dp is not None
        mock_poll.assert_awaited()

@pytest.mark.asyncio
async def test_plugin_stop(plugin):
    """Test plugin stop."""
    mock_bot = AsyncMock()
    mock_bot.session = AsyncMock()
    plugin.bot = mock_bot
    await plugin.stop()
    mock_bot.session.close.assert_awaited_once()

@pytest.mark.asyncio
async def test_handle_message(plugin, mock_message):
    """Test message handling."""
    plugin._verify_owner = MagicMock(return_value=True)
    plugin.message_handler.handle_private_message = AsyncMock()
    mock_message.chat.type = "private"
    await plugin._handle_message(mock_message)
    plugin.message_handler.handle_private_message.assert_awaited_once_with(mock_message)

@pytest.mark.asyncio
async def test_handle_response(plugin, mock_message):
    """Test response handling."""
    plugin.message_handler.process_outgoing_message = AsyncMock()
    await plugin._handle_response("Test response", mock_message)
    plugin.message_handler.process_outgoing_message.assert_awaited_once_with(mock_message, "Test response")

@pytest.mark.asyncio
async def test_handle_start_command(plugin, mock_message, mock_bot):
    """Test start command handling."""
    plugin.bot = mock_bot
    await plugin._handle_start_command(mock_message)
    mock_message.answer.assert_awaited_once_with("Welcome! I'm your Telegram bot.")

@pytest.mark.asyncio
async def test_handle_help_command(plugin, mock_message, mock_bot):
    """Test help command handling."""
    plugin.bot = mock_bot
    await plugin._handle_help_command(mock_message)
    mock_message.answer.assert_awaited()

@pytest.mark.asyncio
async def test_validate_settings(plugin):
    """Test settings validation."""
    settings = TelegramBotSettings(
        bot_token="test_token",
        owner_id=123456789,
        message_mode=MessageMode.ECHO,
        buffer_delay=5
    )
    assert plugin.validate_settings(settings) is True

@pytest.mark.asyncio
async def test_register_event_handler(plugin):
    """Test event handler registration."""
    handler = AsyncMock()
    await plugin.register_event_handler("test_event", handler)
    assert "test_event" in plugin.event_handlers
    assert plugin.event_handlers["test_event"] == handler

@pytest.mark.asyncio
async def test_emit_event(plugin):
    """Test event emission."""
    handler = AsyncMock()
    await plugin.register_event_handler("test_event", handler)
    await plugin.emit_event("test_event", {"data": "test"})
    handler.assert_awaited_once_with({"data": "test"})

@pytest.mark.asyncio
async def test_verify_owner_by_id(plugin, mock_user):
    """Test owner verification by ID."""
    plugin.settings.owner_id = 123456789
    plugin.settings.owner_username = None
    assert plugin._verify_owner(mock_user.id, mock_user.username)

@pytest.mark.asyncio
async def test_verify_owner_by_username(plugin, mock_user):
    """Test owner verification by username."""
    plugin.settings.owner_id = None
    plugin.settings.owner_username = "testuser"
    assert plugin._verify_owner(mock_user.id, mock_user.username)

@pytest.mark.asyncio
async def test_verify_owner_failure(plugin, mock_user):
    """Test owner verification failure."""
    plugin.settings.owner_id = 987654321
    plugin.settings.owner_username = "wronguser"
    assert not plugin._verify_owner(mock_user.id, mock_user.username)

@pytest.mark.asyncio
async def test_handle_message_from_owner(plugin, mock_message):
    """Test handling message from owner."""
    plugin._verify_owner = MagicMock(return_value=True)
    plugin.message_handler.handle_private_message = AsyncMock()
    mock_message.chat.type = "private"
    await plugin._handle_message(mock_message)
    plugin.message_handler.handle_private_message.assert_awaited_once_with(mock_message)

@pytest.mark.asyncio
async def test_handle_message_from_non_owner(plugin, mock_message):
    """Test handling message from non-owner."""
    plugin.settings = MagicMock(
        owner_id="987654321",
        owner_username=None
    )
    plugin.message_handler = AsyncMock()
    
    await plugin._handle_message(mock_message)
    
    plugin.message_handler.handle_private_message.assert_not_called() 