"""Extended unit tests for common config utilities."""

import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open

import pytest

from common.config import (
    Settings,
    get_env_var,
    get_settings,
    load_settings_from_file,
    save_settings_to_file,
    validate_settings,
)


class TestConfigExtended:
    """Extended test cases for common config utilities."""

    def test_get_env_var_string(self):
        """Test getting string environment variable."""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            result = get_env_var("TEST_VAR")
            assert result == "test_value"

    def test_get_env_var_with_default(self):
        """Test getting environment variable with default."""
        with patch.dict(os.environ, {}, clear=True):
            result = get_env_var("NONEXISTENT_VAR", default="default_value")
            assert result == "default_value"

    def test_get_env_var_required_missing(self):
        """Test getting required environment variable that's missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                ValueError,
                match="Required environment variable NONEXISTENT_VAR not set",
            ):
                get_env_var("NONEXISTENT_VAR", required=True)

    def test_get_env_var_int_cast(self):
        """Test getting environment variable with int casting."""
        with patch.dict(os.environ, {"TEST_INT": "42"}):
            result = get_env_var("TEST_INT", cast_type=int)
            assert result == 42

    def test_get_env_var_bool_cast_true(self):
        """Test getting environment variable with bool casting (true)."""
        with patch.dict(os.environ, {"TEST_BOOL": "true"}):
            result = get_env_var("TEST_BOOL", cast_type=bool)
            assert result is True

    def test_get_env_var_bool_cast_false(self):
        """Test getting environment variable with bool casting (false)."""
        with patch.dict(os.environ, {"TEST_BOOL": "false"}):
            result = get_env_var("TEST_BOOL", cast_type=bool)
            assert result is False

    def test_get_env_var_bool_cast_invalid(self):
        """Test getting environment variable with invalid bool casting."""
        with patch.dict(os.environ, {"TEST_BOOL": "invalid"}):
            with pytest.raises(ValueError):
                get_env_var("TEST_BOOL", cast_type=bool)

    def test_get_env_var_int_cast_invalid(self):
        """Test getting environment variable with invalid int casting."""
        with patch.dict(os.environ, {"TEST_INT": "not_a_number"}):
            with pytest.raises(ValueError):
                get_env_var("TEST_INT", cast_type=int)

    def test_get_env_var_float_cast(self):
        """Test getting environment variable with float casting."""
        with patch.dict(os.environ, {"TEST_FLOAT": "3.14"}):
            result = get_env_var("TEST_FLOAT", cast_type=float)
            assert result == 3.14

    def test_get_env_var_list_cast(self):
        """Test getting environment variable with list casting."""
        with patch.dict(os.environ, {"TEST_LIST": "a,b,c"}):
            result = get_env_var("TEST_LIST", cast_type=lambda x: x.split(","))
            assert result == ["a", "b", "c"]

    def test_get_settings_default(self):
        """Test getting default settings."""
        with patch("common.config.Path.exists", return_value=False):
            settings = get_settings()
            assert isinstance(settings, dict)
            assert "debug_mode" in settings
            assert "queue_refresh" in settings
            assert "max_retries" in settings
            assert "message_mode" in settings

    def test_get_settings_from_file(self):
        """Test getting settings from file."""
        test_settings = {
            "debug_mode": True,
            "queue_refresh": 10,
            "max_retries": 5,
            "message_mode": "echo",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            import json

            json.dump(test_settings, f)
            temp_path = f.name

        try:
            with patch("common.config.Path.exists", return_value=True):
                with patch(
                    "common.config.Path.open",
                    mock_open(read_data=json.dumps(test_settings)),
                ):
                    settings = get_settings()
                    assert settings == test_settings
        finally:
            os.unlink(temp_path)

    def test_validate_settings_valid(self):
        """Test validating valid settings."""
        valid_settings = {
            "debug_mode": True,
            "queue_refresh": 5,
            "max_retries": 3,
            "message_mode": "live",
        }

        # Should not raise an exception
        validate_settings(valid_settings)

    def test_validate_settings_invalid_queue_refresh(self):
        """Test validating settings with invalid queue_refresh."""
        invalid_settings = {
            "debug_mode": True,
            "queue_refresh": -1,  # Invalid: must be positive
            "max_retries": 3,
            "message_mode": "live",
        }

        with pytest.raises(
            ValueError, match="queue_refresh must be a positive integer"
        ):
            validate_settings(invalid_settings)

    def test_validate_settings_invalid_max_retries(self):
        """Test validating settings with invalid max_retries."""
        invalid_settings = {
            "debug_mode": True,
            "queue_refresh": 5,
            "max_retries": -1,  # Invalid: must be non-negative
            "message_mode": "live",
        }

        with pytest.raises(
            ValueError, match="max_retries must be a non-negative integer"
        ):
            validate_settings(invalid_settings)

    def test_validate_settings_invalid_message_mode(self):
        """Test validating settings with invalid message_mode."""
        invalid_settings = {
            "debug_mode": True,
            "queue_refresh": 5,
            "max_retries": 3,
            "message_mode": "invalid_mode",  # Invalid: must be 'live' or 'echo'
        }

        with pytest.raises(
            ValueError, match="message_mode must be either 'live' or 'echo'"
        ):
            validate_settings(invalid_settings)

    def test_validate_settings_missing_fields(self):
        """Test validating settings with missing fields."""
        incomplete_settings = {
            "debug_mode": True
            # Missing other required fields
        }

        with pytest.raises(ValueError):
            validate_settings(incomplete_settings)

    def test_settings_class_initialization(self):
        """Test Settings class initialization."""
        settings = Settings(
            debug_mode=True, queue_refresh=10, max_retries=5, message_mode="echo"
        )

        assert settings.debug_mode is True
        assert settings.queue_refresh == 10
        assert settings.max_retries == 5
        assert settings.message_mode == "echo"

    def test_settings_class_defaults(self):
        """Test Settings class with default values."""
        settings = Settings()

        assert settings.debug_mode is False
        assert settings.queue_refresh == 5
        assert settings.max_retries == 3
        assert settings.message_mode == "live"

    def test_settings_class_validation(self):
        """Test Settings class validation."""
        with pytest.raises(ValueError):
            Settings(queue_refresh=-1)

    def test_load_settings_from_file(self):
        """Test loading settings from file."""
        test_settings = {
            "debug_mode": True,
            "queue_refresh": 10,
            "max_retries": 5,
            "message_mode": "echo",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            import json

            json.dump(test_settings, f)
            temp_path = f.name

        try:
            settings = load_settings_from_file(temp_path)
            assert settings == test_settings
        finally:
            os.unlink(temp_path)

    def test_load_settings_from_nonexistent_file(self):
        """Test loading settings from nonexistent file."""
        with pytest.raises(FileNotFoundError):
            load_settings_from_file("nonexistent.json")

    def test_load_settings_from_invalid_json(self):
        """Test loading settings from invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            temp_path = f.name

        try:
            with pytest.raises(ValueError):
                load_settings_from_file(temp_path)
        finally:
            os.unlink(temp_path)

    def test_save_settings_to_file(self):
        """Test saving settings to file."""
        test_settings = {
            "debug_mode": True,
            "queue_refresh": 10,
            "max_retries": 5,
            "message_mode": "echo",
        }

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            save_settings_to_file(test_settings, temp_path)

            # Verify file was created and contains correct content
            assert os.path.exists(temp_path)

            import json

            with open(temp_path) as f:
                loaded_settings = json.load(f)
            assert loaded_settings == test_settings
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_save_settings_to_file_with_indent(self):
        """Test saving settings to file with indentation."""
        test_settings = {"debug_mode": True}

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            save_settings_to_file(test_settings, temp_path, indent=4)

            # Verify file contains indented JSON
            with open(temp_path) as f:
                content = f.read()
            assert "    " in content  # Should contain 4-space indentation
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_get_env_var_case_sensitive(self):
        """Test that environment variable names are case sensitive."""
        with patch.dict(os.environ, {"test_var": "lowercase", "TEST_VAR": "uppercase"}):
            result_lower = get_env_var("test_var")
            result_upper = get_env_var("TEST_VAR")

            assert result_lower == "lowercase"
            assert result_upper == "uppercase"

    def test_get_env_var_empty_string(self):
        """Test getting empty string environment variable."""
        with patch.dict(os.environ, {"EMPTY_VAR": ""}):
            result = get_env_var("EMPTY_VAR")
            assert result == ""

    def test_get_env_var_none_default(self):
        """Test getting environment variable with None default."""
        with patch.dict(os.environ, {}, clear=True):
            result = get_env_var("NONEXISTENT_VAR", default=None)
            assert result is None

    def test_validate_settings_extra_fields(self):
        """Test validating settings with extra fields."""
        settings_with_extra = {
            "debug_mode": True,
            "queue_refresh": 5,
            "max_retries": 3,
            "message_mode": "live",
            "extra_field": "extra_value",  # Extra field
        }

        # Should not raise an exception for extra fields
        validate_settings(settings_with_extra)

    def test_settings_class_to_dict(self):
        """Test converting Settings class to dictionary."""
        settings = Settings(debug_mode=True, queue_refresh=10)
        settings_dict = settings.to_dict()

        assert isinstance(settings_dict, dict)
        assert settings_dict["debug_mode"] is True
        assert settings_dict["queue_refresh"] == 10

    def test_settings_class_from_dict(self):
        """Test creating Settings class from dictionary."""
        settings_dict = {
            "debug_mode": True,
            "queue_refresh": 10,
            "max_retries": 5,
            "message_mode": "echo",
        }

        settings = Settings.from_dict(settings_dict)

        assert settings.debug_mode is True
        assert settings.queue_refresh == 10
        assert settings.max_retries == 5
        assert settings.message_mode == "echo"

    def test_get_env_var_with_custom_cast_function(self):
        """Test getting environment variable with custom cast function."""
        with patch.dict(os.environ, {"CUSTOM_VAR": "hello,world"}):

            def custom_cast(value):
                return value.split(",")

            result = get_env_var("CUSTOM_VAR", cast_type=custom_cast)
            assert result == ["hello", "world"]

    def test_validate_settings_edge_cases(self):
        """Test validating settings with edge case values."""
        # Test with zero values
        zero_settings = {
            "debug_mode": False,
            "queue_refresh": 1,  # Minimum valid value
            "max_retries": 0,  # Valid: non-negative
            "message_mode": "live",
        }

        # Should not raise an exception
        validate_settings(zero_settings)

    def test_get_env_var_with_whitespace(self):
        """Test getting environment variable with whitespace."""
        with patch.dict(os.environ, {"WHITESPACE_VAR": "  test value  "}):
            result = get_env_var("WHITESPACE_VAR")
            assert result == "  test value  "  # Should preserve whitespace

    def test_settings_class_equality(self):
        """Test Settings class equality comparison."""
        settings1 = Settings(debug_mode=True, queue_refresh=10)
        settings2 = Settings(debug_mode=True, queue_refresh=10)
        settings3 = Settings(debug_mode=False, queue_refresh=10)

        assert settings1 == settings2
        assert settings1 != settings3

    def test_settings_class_string_representation(self):
        """Test Settings class string representation."""
        settings = Settings(debug_mode=True, queue_refresh=10)
        settings_str = str(settings)

        assert "debug_mode=True" in settings_str
        assert "queue_refresh=10" in settings_str
