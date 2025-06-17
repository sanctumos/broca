"""Unit tests for the Telegram bot plugin."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.types import User, Message, Chat

from ..plugin import TelegramBotPlugin
from ..settings import TelegramBotSettings, MessageMode

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
def plugin():
    """Create a plugin instance."""
    return TelegramBotPlugin()

@pytest.mark.asyncio
async def test_plugin_initialization(plugin):
    """Test plugin initialization."""
    assert plugin.get_name() == "telegram_bot"
    assert plugin.get_platform() == "telegram"
    assert plugin.settings is None
    assert plugin.bot is None
    assert plugin.dp is None
    assert plugin.message_handler is None
    assert plugin.message_buffer is None
    assert not plugin._running
    assert not plugin._owner_verified

@pytest.mark.asyncio
async def test_plugin_start(plugin, mock_bot, mock_dispatcher):
    """Test plugin start."""
    with patch("aiogram.Bot", return_value=mock_bot), \
         patch("aiogram.Dispatcher", return_value=mock_dispatcher), \
         patch.object(TelegramBotSettings, "from_env", return_value=MagicMock(
             bot_token="test_token",
             owner_id="123456789",
             message_mode=MessageMode.ECHO,
             buffer_delay=5
         )):
        
        await plugin.start()
        
        assert plugin.settings is not None
        assert plugin.bot is not None
        assert plugin.dp is not None
        assert plugin.message_handler is not None
        assert plugin.message_buffer is not None
        assert plugin._running

@pytest.mark.asyncio
async def test_plugin_stop(plugin, mock_bot):
    """Test plugin stop."""
    plugin.bot = mock_bot
    plugin._running = True
    
    await plugin.stop()
    
    assert not plugin._running
    mock_bot.session.close.assert_called_once()

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

@pytest.mark.asyncio
async def test_handle_start_command(plugin, mock_message):
    """Test handling /start command."""
    await plugin._handle_start(mock_message)
    
    mock_message.answer.assert_called_once()

@pytest.mark.asyncio
async def test_handle_help_command(plugin, mock_message):
    """Test handling /help command."""
    await plugin._handle_help(mock_message)
    
    mock_message.answer.assert_called_once()

@pytest.mark.asyncio
async def test_handle_response(plugin, mock_bot):
    """Test handling response message."""
    plugin.bot = mock_bot
    message_id = 1
    response = "Test response"
    
    with patch.object(plugin, "_get_message", return_value={
        "platform_user_id": "123456789"
    }):
        await plugin._handle_response(message_id, response)
        
        mock_bot.send_message.assert_called_once_with(
            chat_id="123456789",
            text=response
        ) 