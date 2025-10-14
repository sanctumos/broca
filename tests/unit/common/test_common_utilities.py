"""Unit tests for common utilities."""

from unittest.mock import mock_open, patch

import pytest

from common.config import get_env_var, get_settings
from common.logging import get_logger, setup_logging
from common.retry import RetryConfig, exponential_backoff, is_retryable_exception


@pytest.mark.unit
def test_get_env_var():
    """Test get_env_var function."""
    with patch("common.config.os.environ") as mock_environ:
        mock_environ.get.return_value = "test_value"
        result = get_env_var("TEST_VAR")
        assert result == "test_value"


@pytest.mark.unit
def test_get_env_var_default():
    """Test get_env_var with default."""
    with patch("common.config.os.environ") as mock_environ:
        mock_environ.get.return_value = None
        result = get_env_var("TEST_VAR", "default")
        assert result == "default"


@pytest.mark.unit
def test_get_settings():
    """Test get_settings function."""
    with patch("common.config.os.path.exists", return_value=True), patch(
        "builtins.open",
        mock_open(read_data='{"debug_mode": false, "queue_refresh": 5}'),
    ), patch(
        "common.config.json.loads",
        return_value={"debug_mode": False, "queue_refresh": 5},
    ):
        settings = get_settings()
        assert settings is not None
        assert settings["debug_mode"] is False


@pytest.mark.unit
def test_setup_logging():
    """Test setup_logging function."""
    with patch("common.logging.logging.getLogger") as mock_get_logger:
        mock_logger = mock_get_logger.return_value
        mock_handlers = []
        mock_logger.handlers = mock_handlers

        setup_logging()

        # Check that handlers were cleared and new handler added
        assert len(mock_logger.handlers) == 0  # cleared
        mock_logger.addHandler.assert_called_once()
        mock_logger.setLevel.assert_called()  # called at least once


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


@pytest.mark.asyncio
@pytest.mark.unit
async def test_exponential_backoff():
    """Test exponential_backoff function."""

    async def test_func():
        return "success"

    result = await exponential_backoff(test_func)
    assert result == "success"

    # Test with retry config
    config = RetryConfig(max_retries=2, base_delay=0.1)
    result = await exponential_backoff(test_func, config)
    assert result == "success"


@pytest.mark.unit
def test_is_retryable_exception():
    """Test is_retryable_exception function."""

    # Test retryable exception (ConnectionError is in the retryable types)
    assert is_retryable_exception(ConnectionError()) is True

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
