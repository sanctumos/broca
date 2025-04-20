"""Tests for common.config module."""

import os
import json
import pytest
from unittest.mock import patch, mock_open, Mock
from common.config import get_env_var, get_settings, _reset_settings_cache

@pytest.fixture(autouse=True)
def reset_settings_cache():
    """Reset the settings cache before each test."""
    _reset_settings_cache()
    yield
    _reset_settings_cache()

def test_get_env_var_with_default():
    """Test getting an environment variable with a default value."""
    with patch.dict(os.environ, {}, clear=True):
        assert get_env_var("TEST_VAR", default="default") == "default"

def test_get_env_var_required_missing():
    """Test that required environment variables raise an error when missing."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(EnvironmentError):
            get_env_var("TEST_VAR", required=True)

def test_get_env_var_type_casting():
    """Test type casting of environment variables."""
    with patch.dict(os.environ, {"TEST_INT": "42", "TEST_BOOL": "true"}, clear=True):
        assert get_env_var("TEST_INT", cast_type=int) == 42
        assert get_env_var("TEST_BOOL", cast_type=lambda x: x.lower() == "true") is True

def test_get_settings_caching():
    """Test that settings are cached after first load."""
    test_settings = {"key": "value"}
    mock_file = mock_open(read_data=json.dumps(test_settings))
    
    with patch("builtins.open", mock_file), \
         patch("os.path.exists", return_value=True):
        # First call should read from file
        settings1 = get_settings()
        # Second call should use cache
        settings2 = get_settings()
        
        assert settings1 == settings2 == test_settings
        # Verify file was only opened once
        mock_file.assert_called_once()

def test_get_settings_invalid_json():
    """Test handling of invalid JSON in settings file."""
    mock = mock_open()
    mock.return_value.read.return_value = "invalid json"
    
    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock):
        with pytest.raises(ValueError, match="Failed to parse settings file"):
            get_settings()

def test_get_settings_file_not_found():
    """Test handling of missing settings file."""
    with patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError, match="Settings file not found"):
            get_settings()

def test_get_settings_file_open_error():
    """Test handling of file open errors."""
    def raise_permission_error(*args, **kwargs):
        raise PermissionError("Permission denied")
    
    mock = Mock(side_effect=raise_permission_error)
    
    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock):
        with pytest.raises(ValueError, match="Permission denied"):
            get_settings() 