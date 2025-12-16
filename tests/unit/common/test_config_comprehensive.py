"""Comprehensive unit tests for common.config to achieve 100% coverage."""

import json
import os
from unittest.mock import patch

import pytest

from common.config import (
    Settings,
    get_env_var,
    get_settings,
    get_typed_settings,
    save_settings,
    validate_environment_variables,
    validate_settings,
)


@pytest.mark.unit
def test_get_env_var_exists():
    """Test get_env_var when variable exists."""
    with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
        value = get_env_var("TEST_VAR")
        assert value == "test_value"


@pytest.mark.unit
def test_get_env_var_not_exists_default():
    """Test get_env_var when variable doesn't exist with default."""
    with patch.dict(os.environ, {}, clear=True):
        value = get_env_var("NONEXISTENT", default="default_value")
        assert value == "default_value"


@pytest.mark.unit
def test_get_env_var_not_exists_required():
    """Test get_env_var when variable doesn't exist and required."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(OSError, match="Required environment variable"):
            get_env_var("REQUIRED_VAR", required=True)


@pytest.mark.unit
def test_get_env_var_with_cast_type():
    """Test get_env_var with type casting."""
    with patch.dict(os.environ, {"INT_VAR": "42"}):
        value = get_env_var("INT_VAR", cast_type=int)
        assert value == 42
        assert isinstance(value, int)


@pytest.mark.unit
def test_get_env_var_cast_type_error():
    """Test get_env_var with invalid cast type."""
    with patch.dict(os.environ, {"INT_VAR": "not_an_int"}):
        with pytest.raises(ValueError, match="Failed to cast"):
            get_env_var("INT_VAR", cast_type=int)


@pytest.mark.unit
def test_validate_environment_variables_production_valid():
    """Test validate_environment_variables with valid production values."""
    env_vars = {
        "AGENT_API_KEY": "prod-key-12345",
        "AGENT_ENDPOINT": "https://api.production.com",
        "TELEGRAM_API_HASH": "prod-hash-12345",
        "TELEGRAM_BOT_TOKEN": "prod-token-12345",
    }
    
    with patch.dict(os.environ, env_vars):
        # Should not raise
        validate_environment_variables(production_mode=True)


@pytest.mark.unit
def test_validate_environment_variables_production_placeholder():
    """Test validate_environment_variables with placeholder values in production."""
    env_vars = {
        "AGENT_API_KEY": "your_letta_api_key_here",
    }
    
    with patch.dict(os.environ, env_vars):
        with pytest.raises(ValueError, match="Invalid environment variables"):
            validate_environment_variables(production_mode=True)


@pytest.mark.unit
def test_validate_environment_variables_dev_mode():
    """Test validate_environment_variables in dev mode (warnings only)."""
    env_vars = {
        "AGENT_API_KEY": "your_letta_api_key_here",
    }
    
    with patch.dict(os.environ, env_vars):
        # Should not raise in dev mode, only warn
        validate_environment_variables(production_mode=False)


@pytest.mark.unit
def test_validate_environment_variables_missing():
    """Test validate_environment_variables with missing variables."""
    with patch.dict(os.environ, {}, clear=True):
        # Should not raise, only warn
        validate_environment_variables(production_mode=True)


@pytest.mark.unit
def test_get_settings_file_exists(tmp_path, monkeypatch):
    """Test get_settings when file exists."""
    monkeypatch.chdir(tmp_path)
    
    settings_file = tmp_path / "settings.json"
    settings_data = {"debug_mode": True, "queue_refresh": 5}
    settings_file.write_text(json.dumps(settings_data))
    
    result = get_settings()
    
    assert result == settings_data


@pytest.mark.unit
def test_get_settings_file_not_exists(tmp_path, monkeypatch):
    """Test get_settings when file doesn't exist."""
    monkeypatch.chdir(tmp_path)
    
    with pytest.raises(FileNotFoundError):
        get_settings()


@pytest.mark.unit
def test_get_settings_invalid_json(tmp_path, monkeypatch):
    """Test get_settings with invalid JSON."""
    monkeypatch.chdir(tmp_path)
    
    settings_file = tmp_path / "settings.json"
    settings_file.write_text("invalid json{")
    
    with pytest.raises(ValueError, match="Failed to parse"):
        get_settings()


@pytest.mark.unit
def test_get_settings_permission_error(tmp_path, monkeypatch):
    """Test get_settings with permission error."""
    monkeypatch.chdir(tmp_path)
    
    with patch("builtins.open", side_effect=PermissionError("Permission denied")):
        with pytest.raises(ValueError, match="Permission denied"):
            get_settings()


@pytest.mark.unit
def test_get_settings_force_reload(tmp_path, monkeypatch):
    """Test get_settings with force_reload."""
    monkeypatch.chdir(tmp_path)
    
    settings_file = tmp_path / "settings.json"
    settings_file.write_text(json.dumps({"debug_mode": True}))
    
    # First call
    result1 = get_settings()
    
    # Modify file
    settings_file.write_text(json.dumps({"debug_mode": False}))
    
    # Second call without force_reload (should use cache)
    result2 = get_settings()
    assert result2 == result1  # Cached
    
    # Third call with force_reload
    result3 = get_settings(force_reload=True)
    assert result3["debug_mode"] is False  # Fresh load


@pytest.mark.unit
def test_get_typed_settings_valid(tmp_path, monkeypatch):
    """Test get_typed_settings with valid settings."""
    monkeypatch.chdir(tmp_path)
    
    settings_file = tmp_path / "settings.json"
    settings_data = {
        "debug_mode": False,
        "queue_refresh": 5,
        "max_retries": 3,
        "message_mode": "live",
    }
    settings_file.write_text(json.dumps(settings_data))
    
    result = get_typed_settings()
    
    assert isinstance(result, Settings)
    assert result.debug_mode is False
    assert result.queue_refresh == 5


@pytest.mark.unit
def test_get_typed_settings_invalid(tmp_path, monkeypatch):
    """Test get_typed_settings with invalid settings."""
    monkeypatch.chdir(tmp_path)
    
    settings_file = tmp_path / "settings.json"
    settings_data = {
        "queue_refresh": 500,  # Invalid: exceeds max
    }
    settings_file.write_text(json.dumps(settings_data))
    
    with pytest.raises(ValueError, match="Settings validation failed"):
        get_typed_settings()


@pytest.mark.unit
def test_validate_settings_valid():
    """Test validate_settings with valid settings."""
    settings = {
        "debug_mode": True,
        "queue_refresh": 5,
        "max_retries": 3,
        "message_mode": "echo",
    }
    
    result = validate_settings(settings)
    
    assert result == settings


@pytest.mark.unit
def test_validate_settings_missing_field():
    """Test validate_settings with missing required field."""
    settings = {
        "debug_mode": True,
        # Missing queue_refresh
        "max_retries": 3,
        "message_mode": "echo",
    }
    
    with pytest.raises(ValueError, match="Missing required setting"):
        validate_settings(settings)


@pytest.mark.unit
def test_validate_settings_invalid_message_mode():
    """Test validate_settings with invalid message_mode."""
    settings = {
        "debug_mode": True,
        "queue_refresh": 5,
        "max_retries": 3,
        "message_mode": "invalid_mode",
    }
    
    with pytest.raises(ValueError, match="Invalid message_mode"):
        validate_settings(settings)


@pytest.mark.unit
def test_validate_settings_invalid_queue_refresh():
    """Test validate_settings with invalid queue_refresh."""
    settings = {
        "debug_mode": True,
        "queue_refresh": 0,  # Invalid: less than 1
        "max_retries": 3,
        "message_mode": "echo",
    }
    
    with pytest.raises(ValueError, match="queue_refresh must be at least 1"):
        validate_settings(settings)


@pytest.mark.unit
def test_validate_settings_invalid_max_retries():
    """Test validate_settings with invalid max_retries."""
    settings = {
        "debug_mode": True,
        "queue_refresh": 5,
        "max_retries": -1,  # Invalid: negative
        "message_mode": "echo",
    }
    
    with pytest.raises(ValueError, match="max_retries must be non-negative"):
        validate_settings(settings)


@pytest.mark.unit
def test_validate_settings_bool_conversion_string():
    """Test validate_settings converts string bool values."""
    settings = {
        "debug_mode": "true",  # String
        "queue_refresh": 5,
        "max_retries": 3,
        "message_mode": "echo",
    }
    
    result = validate_settings(settings)
    
    assert result["debug_mode"] is True


@pytest.mark.unit
def test_validate_settings_bool_conversion_on():
    """Test validate_settings converts 'on' to True."""
    settings = {
        "debug_mode": "on",
        "queue_refresh": 5,
        "max_retries": 3,
        "message_mode": "echo",
    }
    
    result = validate_settings(settings)
    
    assert result["debug_mode"] is True


@pytest.mark.unit
def test_save_settings_success(tmp_path, monkeypatch):
    """Test save_settings successfully saves settings."""
    monkeypatch.chdir(tmp_path)
    
    settings = {
        "debug_mode": True,
        "queue_refresh": 5,
        "max_retries": 3,
        "message_mode": "echo",
    }
    
    save_settings(settings)
    
    # Verify file was created
    settings_file = tmp_path / "settings.json"
    assert settings_file.exists()
    
    # Verify content
    loaded = json.loads(settings_file.read_text())
    assert loaded == settings


@pytest.mark.unit
def test_save_settings_permission_error(tmp_path, monkeypatch):
    """Test save_settings with permission error."""
    monkeypatch.chdir(tmp_path)
    
    settings = {"debug_mode": True}
    
    with patch("builtins.open", side_effect=PermissionError("Permission denied")):
        with pytest.raises(ValueError, match="Failed to save settings"):
            save_settings(settings)


@pytest.mark.unit
def test_settings_model_valid():
    """Test Settings model with valid data."""
    settings = Settings(
        debug_mode=True,
        queue_refresh=5,
        max_retries=3,
        message_mode="live"
    )
    
    assert settings.debug_mode is True
    assert settings.queue_refresh == 5
    assert settings.max_retries == 3
    assert settings.message_mode == "live"


@pytest.mark.unit
def test_settings_model_invalid_queue_refresh():
    """Test Settings model with invalid queue_refresh."""
    with pytest.raises(Exception):  # Pydantic validation error
        Settings(
            debug_mode=True,
            queue_refresh=500,  # Exceeds max
            max_retries=3,
            message_mode="live"
        )


@pytest.mark.unit
def test_settings_model_invalid_max_retries():
    """Test Settings model with invalid max_retries."""
    with pytest.raises(Exception):  # Pydantic validation error
        Settings(
            debug_mode=True,
            queue_refresh=5,
            max_retries=15,  # Exceeds max
            message_mode="live"
        )


@pytest.mark.unit
def test_settings_model_invalid_message_mode():
    """Test Settings model with invalid message_mode."""
    with pytest.raises(Exception):  # Pydantic validation error
        Settings(
            debug_mode=True,
            queue_refresh=5,
            max_retries=3,
            message_mode="invalid"
        )


@pytest.mark.unit
def test_settings_model_defaults():
    """Test Settings model with defaults."""
    settings = Settings()
    
    assert settings.debug_mode is False
    assert settings.queue_refresh == 5
    assert settings.max_retries == 3
    assert settings.message_mode == "live"
