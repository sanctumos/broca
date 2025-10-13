"""Unit tests for common utilities."""

from unittest.mock import patch

import pytest

from common.config import get_env_var, get_settings
from common.logging import get_logger, setup_logging
from common.retry import RetryConfig, exponential_backoff, is_retryable_exception


@pytest.mark.unit
def test_get_env_var():
    """Test get_env_var function."""
    with patch("common.config.os.getenv") as mock_getenv:
        mock_getenv.return_value = "test_value"
        result = get_env_var("TEST_VAR")
        assert result == "test_value"


@pytest.mark.unit
def test_get_env_var_default():
    """Test get_env_var with default."""
    with patch("common.config.os.getenv") as mock_getenv:
        mock_getenv.return_value = None
        result = get_env_var("TEST_VAR", "default")
        assert result == "default"


@pytest.mark.unit
def test_get_settings():
    """Test get_settings function."""
    with patch("common.config.os.getenv") as mock_getenv:
        mock_getenv.side_effect = lambda key, default=None: {
            "AGENT_ENDPOINT": "http://test.endpoint",
            "AGENT_API_KEY": "test_key",
            "QUEUE_REFRESH": "5",
            "MAX_RETRIES": "3",
        }.get(key, default)

        settings = get_settings()
        assert settings is not None


@pytest.mark.unit
def test_setup_logging():
    """Test setup_logging function."""
    with patch("common.logging.logging.basicConfig") as mock_config:
        setup_logging()
        mock_config.assert_called_once()


@pytest.mark.unit
def test_get_logger():
    """Test get_logger function."""
    logger = get_logger("test_module")
    assert logger is not None
    assert logger.name == "test_module"


@pytest.mark.unit
def test_retry_config():
    """Test RetryConfig class."""
    config = RetryConfig(max_retries=3, base_delay=1.0)
    assert config.max_retries == 3
    assert config.base_delay == 1.0


@pytest.mark.unit
def test_exponential_backoff():
    """Test exponential_backoff function."""
    delay = exponential_backoff(0, 1.0)
    assert delay == 1.0

    delay = exponential_backoff(1, 1.0)
    assert delay == 2.0


@pytest.mark.unit
def test_is_retryable_exception():
    """Test is_retryable_exception function."""

    # Test retryable exception
    class RetryableError(Exception):
        pass

    assert is_retryable_exception(RetryableError()) is True

    # Test non-retryable exception
    class NonRetryableError(Exception):
        pass

    assert is_retryable_exception(NonRetryableError()) is False


@pytest.mark.unit
def test_retry_config_validation():
    """Test RetryConfig validation."""
    config = RetryConfig()
    assert config.max_retries >= 0
    assert config.base_delay > 0


@pytest.mark.unit
def test_logging_levels():
    """Test different logging levels."""
    logger = get_logger("test")

    # Test that logger has expected methods
    assert hasattr(logger, "debug")
    assert hasattr(logger, "info")
    assert hasattr(logger, "warning")
    assert hasattr(logger, "error")
    assert hasattr(logger, "critical")
