"""Unit tests for the Telegram bot settings."""

import os
from unittest.mock import patch

import pytest

from plugins.telegram_bot.settings import MessageMode, TelegramBotSettings


def test_settings_from_env():
    with patch.dict(
        os.environ,
        {
            "TELEGRAM_BOT_TOKEN": "1234567890:test_token",
            "TELEGRAM_OWNER_ID": "123456789",
            "TELEGRAM_MESSAGE_MODE": "echo",
            "TELEGRAM_BUFFER_DELAY": "5",
        },
        clear=True,
    ):
        settings = TelegramBotSettings.from_env()
        assert settings.bot_token == "1234567890:test_token"
        assert settings.owner_id == 123456789
        assert settings.owner_username is None
        assert settings.message_mode == MessageMode.ECHO
        assert settings.buffer_delay == 5


def test_settings_from_env_with_username():
    with patch.dict(
        os.environ,
        {
            "TELEGRAM_BOT_TOKEN": "1234567890:test_token",
            "TELEGRAM_OWNER_USERNAME": "testuser",
            "TELEGRAM_MESSAGE_MODE": "echo",
            "TELEGRAM_BUFFER_DELAY": "5",
        },
        clear=True,
    ):
        settings = TelegramBotSettings.from_env()
        assert settings.bot_token == "1234567890:test_token"
        assert settings.owner_id is None
        assert settings.owner_username == "testuser"
        assert settings.message_mode == MessageMode.ECHO
        assert settings.buffer_delay == 5


def test_settings_from_env_missing_token():
    with patch.dict(
        os.environ,
        {
            "TELEGRAM_OWNER_ID": "123456789",
            "TELEGRAM_MESSAGE_MODE": "echo",
            "TELEGRAM_BUFFER_DELAY": "5",
        },
        clear=True,
    ):
        with pytest.raises(EnvironmentError):
            TelegramBotSettings.from_env()


def test_settings_from_env_missing_owner():
    with patch.dict(
        os.environ,
        {
            "TELEGRAM_BOT_TOKEN": "1234567890:test_token",
            "TELEGRAM_MESSAGE_MODE": "echo",
            "TELEGRAM_BUFFER_DELAY": "5",
        },
        clear=True,
    ):
        with pytest.raises(ValueError):
            TelegramBotSettings.from_env()


def test_settings_from_env_require_owner_false():
    """Test settings with require_owner=False allows missing owner."""
    with patch.dict(
        os.environ,
        {
            "TELEGRAM_BOT_TOKEN": "1234567890:test_token",
            "TELEGRAM_REQUIRE_OWNER": "false",
            "TELEGRAM_MESSAGE_MODE": "echo",
            "TELEGRAM_BUFFER_DELAY": "5",
        },
        clear=True,
    ):
        settings = TelegramBotSettings.from_env()
        assert settings.bot_token == "1234567890:test_token"
        assert settings.require_owner is False
        assert settings.owner_id is None
        assert settings.owner_username is None


def test_settings_from_env_require_owner_true():
    """Test settings with require_owner=True (default) requires owner."""
    with patch.dict(
        os.environ,
        {
            "TELEGRAM_BOT_TOKEN": "1234567890:test_token",
            "TELEGRAM_REQUIRE_OWNER": "true",
            "TELEGRAM_MESSAGE_MODE": "echo",
            "TELEGRAM_BUFFER_DELAY": "5",
        },
        clear=True,
    ):
        with pytest.raises(ValueError):
            TelegramBotSettings.from_env()


def test_settings_to_dict():
    settings = TelegramBotSettings(
        bot_token="test_token",
        owner_id=123456789,
        message_mode=MessageMode.ECHO,
        buffer_delay=5,
    )
    settings_dict = settings.to_dict()
    assert settings_dict["bot_token"] == "test_token"
    assert settings_dict["owner_id"] == 123456789
    assert settings_dict["owner_username"] is None
    assert settings_dict["message_mode"] == "echo"
    assert settings_dict["buffer_delay"] == 5
    assert settings_dict["require_owner"] is True


def test_settings_from_dict():
    settings_dict = {
        "bot_token": "test_token",
        "owner_id": 123456789,
        "owner_username": None,
        "message_mode": "echo",
        "buffer_delay": 5,
    }
    settings = TelegramBotSettings.from_dict(settings_dict)
    assert settings.bot_token == "test_token"
    assert settings.owner_id == 123456789
    assert settings.owner_username is None
    assert settings.message_mode == MessageMode.ECHO
    assert settings.buffer_delay == 5
    assert settings.require_owner is True  # Default value


def test_settings_from_dict_require_owner_false():
    """Test settings from dict with require_owner=False."""
    settings_dict = {
        "bot_token": "test_token",
        "require_owner": False,
        "message_mode": "echo",
        "buffer_delay": 5,
    }
    settings = TelegramBotSettings.from_dict(settings_dict)
    assert settings.bot_token == "test_token"
    assert settings.require_owner is False
    assert settings.owner_id is None
    assert settings.owner_username is None


def test_settings_from_dict_with_username():
    settings_dict = {
        "bot_token": "test_token",
        "owner_id": None,
        "owner_username": "testuser",
        "message_mode": "echo",
        "buffer_delay": 5,
    }
    settings = TelegramBotSettings.from_dict(settings_dict)
    assert settings.bot_token == "test_token"
    assert settings.owner_id is None
    assert settings.owner_username == "testuser"
    assert settings.message_mode == MessageMode.ECHO
    assert settings.buffer_delay == 5


def test_settings_from_dict_missing_required():
    settings_dict = {"owner_id": 123456789, "message_mode": "echo", "buffer_delay": 5}
    with pytest.raises(ValueError):
        TelegramBotSettings.from_dict(settings_dict)


def test_settings_from_dict_invalid_mode():
    settings_dict = {
        "bot_token": "test_token",
        "owner_id": 123456789,
        "owner_username": None,
        "message_mode": "invalid",
        "buffer_delay": 5,
    }
    with pytest.raises(ValueError):
        TelegramBotSettings.from_dict(settings_dict)
