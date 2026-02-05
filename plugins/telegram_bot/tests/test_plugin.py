"""Unit tests for the Telegram bot plugin."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram import Bot, Dispatcher

from plugins.telegram_bot.plugin import TelegramBotPlugin
from plugins.telegram_bot.settings import MessageMode, TelegramBotSettings


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
    """Create a properly initialized plugin for testing."""
    plugin = TelegramBotPlugin()
    plugin.settings = TelegramBotSettings(
        bot_token="test_token",
        owner_id=123456789,
        message_mode=MessageMode.ECHO,
        buffer_delay=5,
        require_owner=False,
    )
    plugin.message_handler = MagicMock()
    plugin.message_handler.process_incoming_message = AsyncMock()
    return plugin


@pytest.mark.asyncio
async def test_plugin_initialization(plugin):
    """Test plugin initialization."""
    assert plugin.get_name() == "telegram_bot"
    assert plugin.get_platform() == "telegram"
    assert plugin.get_message_handler() is not None
    assert plugin.get_settings() is not None


@pytest.mark.asyncio
async def test_plugin_start(plugin):
    """Test plugin start."""
    with (
        patch("aiogram.Bot", new_callable=AsyncMock),
        patch("aiogram.Dispatcher") as mock_dispatcher,
        patch("asyncio.create_task") as mock_create_task,
    ):
        mock_dp = MagicMock()
        mock_dp.start_polling = AsyncMock()
        mock_dispatcher.return_value = mock_dp
        mock_task = MagicMock()
        mock_create_task.return_value = mock_task

        await plugin.start()
        assert plugin.bot is not None
        assert plugin.dp is not None
        mock_dp.start_polling.assert_called_once_with(plugin.bot)
        mock_create_task.assert_called_once()
        assert plugin.polling_task == mock_task


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
    mock_message.chat.type = "private"
    await plugin._handle_message(mock_message)
    plugin.message_handler.process_incoming_message.assert_awaited_once_with(
        mock_message
    )


@pytest.mark.asyncio
async def test_handle_response(plugin, mock_message):
    """Test response handling."""
    plugin.bot = AsyncMock()
    profile = MagicMock()
    profile.platform_user_id = "123456789"
    await plugin._handle_response("Test response", profile, 1)
    plugin.bot.send_message.assert_awaited()


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
        buffer_delay=5,
    )
    assert plugin.validate_settings(settings) is True


@pytest.mark.asyncio
async def test_apply_settings_empty_dict(plugin):
    """Test apply_settings with empty dict loads from environment."""
    with patch(
        "plugins.telegram_bot.plugin.TelegramBotSettings.from_env"
    ) as mock_from_env:
        mock_settings = TelegramBotSettings(
            bot_token="env_token",
            owner_id=123456789,
            message_mode=MessageMode.ECHO,
            buffer_delay=5,
        )
        mock_from_env.return_value = mock_settings

        plugin.apply_settings({})

        assert plugin.settings == mock_settings
        mock_from_env.assert_called_once()


@pytest.mark.asyncio
async def test_apply_settings_dict_with_values(plugin):
    """Test apply_settings with dict converts to TelegramBotSettings."""
    settings_dict = {
        "bot_token": "dict_token",
        "owner_id": 987654321,
        "message_mode": "live",
        "buffer_delay": 10,
    }

    plugin.apply_settings(settings_dict)

    assert plugin.settings is not None
    assert plugin.settings.bot_token == "dict_token"
    assert plugin.settings.owner_id == 987654321
    assert plugin.settings.message_mode == MessageMode.LIVE
    assert plugin.settings.buffer_delay == 10


@pytest.mark.asyncio
async def test_apply_settings_telegram_bot_settings_object(plugin):
    """Test apply_settings with TelegramBotSettings object uses directly."""
    settings_obj = TelegramBotSettings(
        bot_token="obj_token",
        owner_id=111222333,
        message_mode=MessageMode.LISTEN,
        buffer_delay=15,
    )

    plugin.apply_settings(settings_obj)

    assert plugin.settings == settings_obj
    assert plugin.settings.bot_token == "obj_token"
    assert plugin.settings.owner_id == 111222333


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
    plugin.settings.require_owner = True
    mock_message.chat.type = "private"
    await plugin._handle_message(mock_message)
    plugin.message_handler.process_incoming_message.assert_awaited_once_with(
        mock_message
    )


@pytest.mark.asyncio
async def test_handle_message_from_non_owner(plugin, mock_message):
    """Test handling message from non-owner when require_owner=True."""
    plugin.settings = TelegramBotSettings(
        bot_token="test_token",
        owner_id=987654321,
        message_mode=MessageMode.ECHO,
        buffer_delay=5,
        require_owner=True,
    )
    plugin.message_handler = MagicMock()
    plugin.message_handler.process_incoming_message = AsyncMock()
    plugin._verify_owner = MagicMock(return_value=False)

    await plugin._handle_message(mock_message)

    plugin.message_handler.process_incoming_message.assert_not_called()


@pytest.mark.asyncio
async def test_handle_message_require_owner_false(plugin, mock_message):
    """Test handling message when require_owner=False allows all users."""
    plugin.settings = TelegramBotSettings(
        bot_token="test_token",
        owner_id=123456789,
        message_mode=MessageMode.ECHO,
        buffer_delay=5,
        require_owner=False,
    )
    plugin.message_handler = MagicMock()
    plugin.message_handler.process_incoming_message = AsyncMock()
    mock_message.chat.type = "private"

    await plugin._handle_message(mock_message)

    # Should process message even without owner verification
    plugin.message_handler.process_incoming_message.assert_awaited_once_with(
        mock_message
    )
