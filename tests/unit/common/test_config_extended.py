"""Extended unit tests for common config utilities."""

from unittest.mock import mock_open, patch

import pytest

from common.config import Settings, get_env_var, get_settings


@pytest.mark.unit
def test_get_env_var_with_cast():
    """Test get_env_var with type casting."""
    with patch("common.config.os.environ") as mock_environ:
        mock_environ.get.return_value = "123"
        result = get_env_var("TEST_VAR", cast_type=int)
        assert result == 123


@pytest.mark.unit
def test_get_env_var_with_cast_error():
    """Test get_env_var with invalid type casting."""
    with patch("common.config.os.environ") as mock_environ:
        mock_environ.get.return_value = "not_a_number"
        with pytest.raises(ValueError):
            get_env_var("TEST_VAR", cast_type=int)


@pytest.mark.unit
def test_get_env_var_required_missing():
    """Test get_env_var with required=True when variable is missing."""
    with patch("common.config.os.environ") as mock_environ:
        mock_environ.get.return_value = None
        with pytest.raises(
            OSError, match="Required environment variable TEST_VAR is not set"
        ):
            get_env_var("TEST_VAR", required=True)


@pytest.mark.unit
def test_get_env_var_required_present():
    """Test get_env_var with required=True when variable is present."""
    with patch("common.config.os.environ") as mock_environ:
        mock_environ.get.return_value = "test_value"
        result = get_env_var("TEST_VAR", required=True)
        assert result == "test_value"


@pytest.mark.unit
def test_get_env_var_with_default():
    """Test get_env_var with default value."""
    with patch("common.config.os.environ") as mock_environ:
        mock_environ.get.return_value = None
        result = get_env_var("TEST_VAR", default="default_value")
        assert result == "default_value"


@pytest.mark.unit
def test_get_env_var_empty_string():
    """Test get_env_var with empty string value."""
    with patch("common.config.os.environ") as mock_environ:
        mock_environ.get.return_value = ""
        result = get_env_var("TEST_VAR")
        assert result == ""


@pytest.mark.unit
def test_get_settings_caching():
    """Test get_settings caching behavior."""
    with patch("common.config.os.path.exists", return_value=True), patch(
        "builtins.open", mock_open(read_data='{"debug_mode": false}')
    ), patch("common.config.json.loads", return_value={"debug_mode": False}):
        # First call
        settings1 = get_settings()
        # Second call should return cached instance
        settings2 = get_settings()

        assert settings1 is settings2


@pytest.mark.unit
def test_get_settings_multiple_calls():
    """Test get_settings with multiple calls."""
    with patch("common.config.os.path.exists", return_value=True), patch(
        "builtins.open", mock_open(read_data='{"debug_mode": false}')
    ), patch("common.config.json.loads", return_value={"debug_mode": False}):
        settings1 = get_settings()
        settings2 = get_settings()
        settings3 = get_settings()

        assert settings1 is settings2 is settings3


@pytest.mark.unit
def test_settings_model_validation():
    """Test Settings model validation."""
    # Test valid settings
    settings = Settings(
        debug_mode=True, queue_refresh=10, max_retries=5, message_mode="echo"
    )
    assert settings.debug_mode is True
    assert settings.queue_refresh == 10
    assert settings.max_retries == 5
    assert settings.message_mode == "echo"


@pytest.mark.unit
def test_settings_model_defaults():
    """Test Settings model default values."""
    settings = Settings()
    assert settings.debug_mode is False
    assert settings.queue_refresh == 5
    assert settings.max_retries == 3
    assert settings.message_mode == "live"


@pytest.mark.unit
def test_settings_model_validation_error():
    """Test Settings model validation errors."""
    with pytest.raises(ValueError):
        Settings(queue_refresh=0)  # Below minimum


@pytest.mark.unit
def test_settings_model_validation_error_max():
    """Test Settings model validation errors for max values."""
    with pytest.raises(ValueError):
        Settings(queue_refresh=301)  # Above maximum


@pytest.mark.unit
def test_settings_model_validation_error_retries():
    """Test Settings model validation errors for retries."""
    with pytest.raises(ValueError):
        Settings(max_retries=11)  # Above maximum


@pytest.mark.unit
def test_settings_model_validation_error_message_mode():
    """Test Settings model validation errors for message mode."""
    with pytest.raises(ValueError):
        Settings(message_mode="invalid")  # Invalid mode


@pytest.mark.unit
def test_get_env_var_with_boolean_cast():
    """Test get_env_var with boolean casting."""
    with patch("common.config.os.environ") as mock_environ:
        # Test "true" string
        mock_environ.get.return_value = "true"
        result = get_env_var("TEST_VAR", cast_type=lambda x: x.lower() == "true")
        assert result is True

        # Test "false" string
        mock_environ.get.return_value = "false"
        result = get_env_var("TEST_VAR", cast_type=lambda x: x.lower() == "true")
        assert result is False


@pytest.mark.unit
def test_get_env_var_with_list_cast():
    """Test get_env_var with list casting."""
    with patch("common.config.os.environ") as mock_environ:
        mock_environ.get.return_value = "a,b,c"
        result = get_env_var("TEST_VAR", cast_type=lambda x: x.split(","))
        assert result == ["a", "b", "c"]


@pytest.mark.unit
def test_get_env_var_with_json_cast():
    """Test get_env_var with JSON casting."""
    with patch("common.config.os.environ") as mock_environ:
        mock_environ.get.return_value = '{"key": "value"}'
        result = get_env_var("TEST_VAR", cast_type=lambda x: {"key": "value"})
        assert result == {"key": "value"}


@pytest.mark.unit
def test_get_env_var_none_value():
    """Test get_env_var with None value."""
    with patch("common.config.os.environ") as mock_environ:
        mock_environ.get.return_value = None
        result = get_env_var("TEST_VAR")
        assert result is None


@pytest.mark.unit
def test_get_env_var_none_value_with_default():
    """Test get_env_var with None value and default."""
    with patch("common.config.os.environ") as mock_environ:
        mock_environ.get.return_value = None
        result = get_env_var("TEST_VAR", default="default")
        assert result == "default"


@pytest.mark.unit
def test_get_env_var_none_value_with_cast():
    """Test get_env_var with None value and cast."""
    with patch("common.config.os.environ") as mock_environ:
        mock_environ.get.return_value = None
        result = get_env_var("TEST_VAR", cast_type=str)
        assert result is None


@pytest.mark.unit
def test_get_env_var_none_value_with_cast_and_default():
    """Test get_env_var with None value, cast, and default."""
    with patch("common.config.os.environ") as mock_environ:
        mock_environ.get.return_value = None
        result = get_env_var("TEST_VAR", default="default", cast_type=str)
        assert result == "default"
