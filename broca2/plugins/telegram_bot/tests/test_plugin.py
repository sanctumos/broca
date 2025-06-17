"""Unit tests for the Telegram bot plugin."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
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
    return Message(
        message_id=1,
        date=datetime.now(),
        chat=Chat(id=123456789, type="private"),
        from_user=mock_user,
        text="Test message"
    )

@pytest.fixture
def plugin(mock_letta_client):
    """Create a plugin instance for testing."""
    return TelegramBotPlugin()

@pytest.mark.asyncio
async def test_plugin_initialization(plugin):
    """Test plugin initialization."""
    assert plugin.get_name() == "Telegram Bot"
    assert plugin.get_platform() == "telegram"
    assert plugin.get_message_handler() is not None
    assert plugin.get_settings() is not None

@pytest.mark.asyncio
async def test_plugin_start(plugin, mock_bot, mock_dispatcher):
    """Test plugin start."""
    with patch("aiogram.Bot", return_value=mock_bot), \
         patch("aiogram.Dispatcher", return_value=mock_dispatcher):
        await plugin.start()
        assert plugin.bot is not None
        assert plugin.dp is not None
        mock_dispatcher.start_polling.assert_called_once()

@pytest.mark.asyncio
async def test_plugin_stop(plugin, mock_bot):
    """Test plugin stop."""
    plugin.bot = mock_bot
    await plugin.stop()
    mock_bot.session.close.assert_called_once()

@pytest.mark.asyncio
async def test_handle_message(plugin, mock_message, mock_letta_client):
    """Test message handling."""
    plugin.bot = AsyncMock()
    await plugin._handle_message(mock_message)
    mock_letta_client.add_to_queue.assert_called_once()

@pytest.mark.asyncio
async def test_handle_response(plugin, mock_message):
    """Test response handling."""
    plugin.bot = AsyncMock()
    await plugin._handle_response("Test response", mock_message)
    mock_message.answer.assert_called_once_with("Test response")

@pytest.mark.asyncio
async def test_handle_start_command(plugin, mock_message):
    """Test start command handling."""
    await plugin._handle_start_command(mock_message)
    mock_message.answer.assert_called_once()

@pytest.mark.asyncio
async def test_handle_help_command(plugin, mock_message):
    """Test help command handling."""
    await plugin._handle_help_command(mock_message)
    mock_message.answer.assert_called_once()

@pytest.mark.asyncio
async def test_handle_unknown_command(plugin, mock_message):
    """Test unknown command handling."""
    await plugin._handle_unknown_command(mock_message)
    mock_message.answer.assert_called_once()

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
    plugin.register_event_handler("test_event", handler)
    assert "test_event" in plugin.event_handlers
    assert plugin.event_handlers["test_event"] == handler

@pytest.mark.asyncio
async def test_emit_event(plugin):
    """Test event emission."""
    handler = AsyncMock()
    plugin.register_event_handler("test_event", handler)
    await plugin.emit_event("test_event", {"data": "test"})
    handler.assert_called_once_with({"data": "test"})

@pytest.mark.asyncio
async def test_verify_owner_by_id(plugin, mock_user):
    """Test owner verification by ID."""
    plugin.settings = MagicMock(
        owner_id="123456789",
        owner_username=None
    )
    
    assert await plugin._verify_owner(mock_user)

@pytest.mark.asyncio
async def test_verify_owner_by_username(plugin, mock_user):
    """Test owner verification by username."""
    plugin.settings = MagicMock(
        owner_id=None,
        owner_username="testuser"
    )
    
    assert await plugin._verify_owner(mock_user)

@pytest.mark.asyncio
async def test_verify_owner_failure(plugin, mock_user):
    """Test owner verification failure."""
    plugin.settings = MagicMock(
        owner_id="987654321",
        owner_username="wronguser"
    )
    
    assert not await plugin._verify_owner(mock_user)

@pytest.mark.asyncio
async def test_handle_message_from_owner(plugin, mock_message):
    """Test handling message from owner."""
    plugin.settings = MagicMock(
        owner_id="123456789",
        owner_username=None
    )
    plugin.message_handler = AsyncMock()
    
    await plugin._handle_message(mock_message)
    
    plugin.message_handler.handle_private_message.assert_called_once()

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