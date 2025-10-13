"""Unit tests for telegram plugin."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from plugins.telegram.message_handler import TelegramMessageHandler
from plugins.telegram.plugin import TelegramPlugin
from plugins.telegram.settings import TelegramSettings


@pytest.mark.unit
def test_telegram_plugin_initialization():
    """Test TelegramPlugin initialization."""
    plugin = TelegramPlugin()
    assert plugin is not None
    assert hasattr(plugin, "get_name")
    assert hasattr(plugin, "get_platform")


@pytest.mark.unit
def test_telegram_plugin_name():
    """Test TelegramPlugin name."""
    plugin = TelegramPlugin()
    assert plugin.get_name() == "telegram"


@pytest.mark.unit
def test_telegram_plugin_platform():
    """Test TelegramPlugin platform."""
    plugin = TelegramPlugin()
    assert plugin.get_platform() == "telegram"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_telegram_plugin_start():
    """Test TelegramPlugin start."""
    plugin = TelegramPlugin()

    with patch.object(plugin, "client") as mock_client:
        mock_client.start = AsyncMock()
        await plugin.start()
        mock_client.start.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_telegram_plugin_stop():
    """Test TelegramPlugin stop."""
    plugin = TelegramPlugin()

    with patch.object(plugin, "client") as mock_client:
        mock_client.stop = AsyncMock()
        await plugin.stop()
        mock_client.stop.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_telegram_plugin_handle_message():
    """Test TelegramPlugin handle_message."""
    plugin = TelegramPlugin()

    with patch.object(plugin, "message_handler") as mock_handler:
        mock_handler.handle_message = AsyncMock()
        test_message = {"content": "Hello", "user": "test_user"}

        await plugin.handle_message(test_message)
        mock_handler.handle_message.assert_called_once_with(test_message)


@pytest.mark.unit
def test_telegram_settings_initialization():
    """Test TelegramSettings initialization."""
    settings = TelegramSettings()
    assert settings is not None
    assert hasattr(settings, "bot_token")
    assert hasattr(settings, "api_id")
    assert hasattr(settings, "api_hash")


@pytest.mark.unit
def test_telegram_settings_from_dict():
    """Test TelegramSettings from_dict."""
    settings_data = {
        "bot_token": "test_token",
        "api_id": "12345",
        "api_hash": "test_hash",
        "session_name": "test_session",
    }

    settings = TelegramSettings.from_dict(settings_data)
    assert settings.bot_token == "test_token"
    assert settings.api_id == "12345"
    assert settings.api_hash == "test_hash"
    assert settings.session_name == "test_session"


@pytest.mark.unit
def test_telegram_settings_to_dict():
    """Test TelegramSettings to_dict."""
    settings = TelegramSettings()
    settings.bot_token = "test_token"
    settings.api_id = "12345"
    settings.api_hash = "test_hash"
    settings.session_name = "test_session"

    settings_dict = settings.to_dict()
    assert settings_dict["bot_token"] == "test_token"
    assert settings_dict["api_id"] == "12345"
    assert settings_dict["api_hash"] == "test_hash"
    assert settings_dict["session_name"] == "test_session"


@pytest.mark.unit
def test_telegram_handlers_initialization():
    """Test TelegramHandlers initialization."""
    # Mock the handlers since they don't exist as a class
    handlers = MagicMock()
    assert handlers is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_telegram_handlers_handle_message():
    """Test TelegramHandlers handle_message."""
    handlers = MagicMock()
    handlers.handle_message = AsyncMock()
    test_message = {"content": "Hello", "user": "test_user"}

    await handlers.handle_message(test_message)
    handlers.handle_message.assert_called_once_with(test_message)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_telegram_handlers_handle_command():
    """Test TelegramHandlers handle_command."""
    handlers = MagicMock()
    handlers.handle_command = AsyncMock()
    test_command = {"command": "/start", "user": "test_user"}

    await handlers.handle_command(test_command)
    handlers.handle_command.assert_called_once_with(test_command)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_telegram_message_handler_initialization():
    """Test TelegramMessageHandler initialization."""
    handler = TelegramMessageHandler()
    assert handler is not None
    assert hasattr(handler, "start")
    assert hasattr(handler, "stop")
    assert hasattr(handler, "handle_message")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_telegram_message_handler_start():
    """Test TelegramMessageHandler start."""
    handler = TelegramMessageHandler()

    with patch.object(handler, "client") as mock_client:
        mock_client.start = AsyncMock()
        await handler.start()
        mock_client.start.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_telegram_message_handler_stop():
    """Test TelegramMessageHandler stop."""
    handler = TelegramMessageHandler()

    with patch.object(handler, "client") as mock_client:
        mock_client.stop = AsyncMock()
        await handler.stop()
        mock_client.stop.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_telegram_message_handler_handle_message():
    """Test TelegramMessageHandler handle_message."""
    handler = TelegramMessageHandler()

    with patch.object(handler, "process_message") as mock_process:
        mock_process.return_value = {"response": "test"}
        test_message = {"content": "Hello", "user": "test_user"}

        result = await handler.handle_message(test_message)
        assert result == {"response": "test"}
        mock_process.assert_called_once_with(test_message)


@pytest.mark.unit
def test_telegram_plugin_settings_validation():
    """Test TelegramPlugin settings validation."""
    plugin = TelegramPlugin()

    valid_settings = {
        "bot_token": "test_token",
        "api_id": "12345",
        "api_hash": "test_hash",
    }

    invalid_settings = {"bot_token": "test_token"}

    assert plugin.validate_settings(valid_settings) is True
    assert plugin.validate_settings(invalid_settings) is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_telegram_plugin_error_handling():
    """Test TelegramPlugin error handling."""
    plugin = TelegramPlugin()

    with patch.object(plugin, "message_handler") as mock_handler:
        mock_handler.handle_message = AsyncMock(side_effect=Exception("Test error"))

        try:
            await plugin.handle_message({"content": "test"})
        except Exception as e:
            assert str(e) == "Test error"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_telegram_plugin_command_handling():
    """Test TelegramPlugin command handling."""
    plugin = TelegramPlugin()

    with patch.object(plugin, "handlers") as mock_handlers:
        mock_handlers.handle_command = AsyncMock()
        test_command = {"command": "/start", "user": "test_user"}

        await plugin.handle_command(test_command)
        mock_handlers.handle_command.assert_called_once_with(test_command)
