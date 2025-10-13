"""Tests for typed configuration with pydantic Settings model."""

import json
import tempfile
from pathlib import Path

from common.config import Settings, get_typed_settings, validate_settings


def test_settings_model_validation():
    """Test Settings model validation."""
    # Test valid settings
    valid_settings = Settings(
        debug_mode=True, queue_refresh=10, max_retries=5, message_mode="live"
    )
    assert valid_settings.debug_mode is True
    assert valid_settings.queue_refresh == 10
    assert valid_settings.max_retries == 5
    assert valid_settings.message_mode == "live"

    # Test defaults
    default_settings = Settings()
    assert default_settings.debug_mode is False
    assert default_settings.queue_refresh == 5
    assert default_settings.max_retries == 3
    assert default_settings.message_mode == "live"


def test_settings_validation_errors():
    """Test Settings model validation errors."""
    # Test invalid message_mode
    try:
        Settings(message_mode="invalid")
        raise AssertionError("Should have raised validation error")
    except ValueError as e:
        assert "message_mode" in str(e)

    # Test invalid queue_refresh
    try:
        Settings(queue_refresh=0)
        raise AssertionError("Should have raised validation error")
    except ValueError as e:
        assert "queue_refresh" in str(e)

    # Test invalid max_retries
    try:
        Settings(max_retries=-1)
        raise AssertionError("Should have raised validation error")
    except ValueError as e:
        assert "max_retries" in str(e)


def test_typed_settings_loading():
    """Test typed settings loading from file."""
    # Create temporary settings file
    settings_data = {
        "debug_mode": True,
        "queue_refresh": 15,
        "max_retries": 7,
        "message_mode": "echo",
        "plugins": {"test_plugin": {"enabled": True}},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(settings_data, f)
        temp_file = f.name

    try:
        # Load typed settings
        settings = get_typed_settings(temp_file)

        assert settings.debug_mode is True
        assert settings.queue_refresh == 15
        assert settings.max_retries == 7
        assert settings.message_mode == "echo"
        assert settings.plugins == {"test_plugin": {"enabled": True}}

        # Test force reload
        settings2 = get_typed_settings(temp_file, force_reload=True)
        assert settings2.debug_mode is True

    finally:
        Path(temp_file).unlink()


def test_validate_settings_non_mutating():
    """Test that validate_settings doesn't mutate input."""
    original_settings = {
        "debug_mode": "true",  # String that should be converted
        "queue_refresh": "10",  # String that should be converted
        "max_retries": 3,
        "message_mode": "live",
    }

    # Make a copy to verify original isn't mutated
    original_copy = original_settings.copy()

    validated = validate_settings(original_settings)

    # Original should be unchanged
    assert original_settings == original_copy
    assert original_settings["debug_mode"] == "true"  # Still string
    assert original_settings["queue_refresh"] == "10"  # Still string

    # Validated should have correct types
    assert validated["debug_mode"] is True  # Converted to bool
    assert validated["queue_refresh"] == 10  # Converted to int
    assert validated["max_retries"] == 3
    assert validated["message_mode"] == "live"


def test_environment_variable_override():
    """Test environment variable override with BROCA_ prefix."""
    import os

    # Set environment variables
    os.environ["BROCA_DEBUG_MODE"] = "true"
    os.environ["BROCA_QUEUE_REFRESH"] = "20"
    os.environ["BROCA_MESSAGE_MODE"] = "listen"

    try:
        settings = Settings()

        # Should use environment values
        assert settings.debug_mode is True
        assert settings.queue_refresh == 20
        assert settings.message_mode == "listen"

    finally:
        # Clean up environment
        os.environ.pop("BROCA_DEBUG_MODE", None)
        os.environ.pop("BROCA_QUEUE_REFRESH", None)
        os.environ.pop("BROCA_MESSAGE_MODE", None)


if __name__ == "__main__":
    test_settings_model_validation()
    test_settings_validation_errors()
    test_typed_settings_loading()
    test_validate_settings_non_mutating()
    test_environment_variable_override()
    print("All tests passed!")
