"""Unit tests for the Telegram bot settings."""
import pytest
from unittest.mock import patch
import os

from plugins.telegram_bot.settings import TelegramBotSettings, MessageMode

def test_settings_from_env():
    """Test creating settings from environment variables."""
    settings = TelegramBotSettings.from_env()
    assert settings.bot_token == "1234567890:test_token"
    assert settings.owner_id == 123456789
    assert settings.owner_username is None
    assert settings.message_mode == MessageMode.ECHO
    assert settings.buffer_delay == 5

def test_settings_from_env_with_username():
    """Test creating settings with username instead of ID."""
    with patch.dict(os.environ, {
        "TELEGRAM_BOT_TOKEN": "1234567890:test_token",
        "TELEGRAM_OWNER_USERNAME": "testuser",
        "TELEGRAM_MESSAGE_MODE": "echo",
        "TELEGRAM_BUFFER_DELAY": "5"
    }):
        settings = TelegramBotSettings.from_env()
        assert settings.bot_token == "1234567890:test_token"
        assert settings.owner_id is None
        assert settings.owner_username == "testuser"
        assert settings.message_mode == MessageMode.ECHO
        assert settings.buffer_delay == 5

def test_settings_from_env_missing_token():
    """Test creating settings with missing token."""
    with patch.dict(os.environ, {
        "TELEGRAM_OWNER_ID": "123456789",
        "TELEGRAM_MESSAGE_MODE": "echo",
        "TELEGRAM_BUFFER_DELAY": "5"
    }, clear=True):
        with pytest.raises(ValueError):
            TelegramBotSettings.from_env()

def test_settings_from_env_missing_owner():
    """Test creating settings with missing owner."""
    with patch.dict(os.environ, {
        "TELEGRAM_BOT_TOKEN": "1234567890:test_token",
        "TELEGRAM_MESSAGE_MODE": "echo",
        "TELEGRAM_BUFFER_DELAY": "5"
    }, clear=True):
        with pytest.raises(ValueError):
            TelegramBotSettings.from_env()

def test_settings_from_env_both_owner_fields():
    """Test creating settings with both owner ID and username."""
    with patch.dict(os.environ, {
        "TELEGRAM_BOT_TOKEN": "1234567890:test_token",
        "TELEGRAM_OWNER_ID": "123456789",
        "TELEGRAM_OWNER_USERNAME": "testuser",
        "TELEGRAM_MESSAGE_MODE": "echo",
        "TELEGRAM_BUFFER_DELAY": "5"
    }):
        with pytest.raises(ValueError):
            TelegramBotSettings.from_env()

def test_settings_to_dict():
    """Test converting settings to dictionary."""
    settings = TelegramBotSettings(
        bot_token="test_token",
        owner_id=123456789,
        message_mode=MessageMode.ECHO,
        buffer_delay=5
    )
    settings_dict = settings.to_dict()
    assert settings_dict["bot_token"] == "test_token"
    assert settings_dict["owner_id"] == 123456789
    assert settings_dict["owner_username"] is None
    assert settings_dict["message_mode"] == "echo"
    assert settings_dict["buffer_delay"] == 5

def test_settings_from_dict():
    """Test creating settings from dictionary."""
    settings_dict = {
        "bot_token": "test_token",
        "owner_id": 123456789,
        "owner_username": None,
        "message_mode": "echo",
        "buffer_delay": 5
    }
    settings = TelegramBotSettings.from_dict(settings_dict)
    assert settings.bot_token == "test_token"
    assert settings.owner_id == 123456789
    assert settings.owner_username is None
    assert settings.message_mode == MessageMode.ECHO
    assert settings.buffer_delay == 5

def test_settings_from_dict_with_username():
    """Test creating settings from dictionary with username."""
    settings_dict = {
        "bot_token": "test_token",
        "owner_id": None,
        "owner_username": "testuser",
        "message_mode": "echo",
        "buffer_delay": 5
    }
    settings = TelegramBotSettings.from_dict(settings_dict)
    assert settings.bot_token == "test_token"
    assert settings.owner_id is None
    assert settings.owner_username == "testuser"
    assert settings.message_mode == MessageMode.ECHO
    assert settings.buffer_delay == 5

def test_settings_from_dict_both_owner_fields():
    """Test creating settings from dictionary with both owner fields."""
    settings_dict = {
        "bot_token": "test_token",
        "owner_id": 123456789,
        "owner_username": "testuser",
        "message_mode": "echo",
        "buffer_delay": 5
    }
    with pytest.raises(ValueError):
        TelegramBotSettings.from_dict(settings_dict)

def test_settings_from_dict_missing_required():
    """Test creating settings from dictionary with missing required fields."""
    settings_dict = {
        "owner_id": 123456789,
        "message_mode": "echo",
        "buffer_delay": 5
    }
    with pytest.raises(ValueError):
        TelegramBotSettings.from_dict(settings_dict)

def test_settings_from_dict_invalid_mode():
    """Test creating settings from dictionary with invalid message mode."""
    settings_dict = {
        "bot_token": "test_token",
        "owner_id": 123456789,
        "owner_username": None,
        "message_mode": "invalid",
        "buffer_delay": 5
    }
    with pytest.raises(ValueError):
        TelegramBotSettings.from_dict(settings_dict) 