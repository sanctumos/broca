"""Extended unit tests for common logging utilities."""

from unittest.mock import MagicMock, patch

import pytest

from common.logging import get_logger, setup_logging


@pytest.mark.unit
def test_setup_logging_with_level():
    """Test setup_logging with specific level."""
    with patch("common.logging.logging.basicConfig") as mock_basicConfig:
        setup_logging(level="DEBUG")
        mock_basicConfig.assert_called_once()


@pytest.mark.unit
def test_setup_logging_with_format():
    """Test setup_logging with custom format."""
    with patch("common.logging.logging.basicConfig") as mock_basicConfig:
        custom_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        setup_logging(format_string=custom_format)
        mock_basicConfig.assert_called_once()


@pytest.mark.unit
def test_setup_logging_with_file():
    """Test setup_logging with file output."""
    with patch("common.logging.logging.basicConfig") as mock_basicConfig:
        setup_logging(log_file="test.log")
        mock_basicConfig.assert_called_once()


@pytest.mark.unit
def test_setup_logging_with_all_options():
    """Test setup_logging with all options."""
    with patch("common.logging.logging.basicConfig") as mock_basicConfig:
        setup_logging(
            level="INFO",
            format_string="%(levelname)s: %(message)s",
            log_file="test.log",
        )
        mock_basicConfig.assert_called_once()


@pytest.mark.unit
def test_get_logger_with_name():
    """Test get_logger with specific name."""
    with patch("common.logging.logging.getLogger") as mock_getLogger:
        logger = get_logger("test_logger")
        mock_getLogger.assert_called_once_with("test_logger")
        assert logger is mock_getLogger.return_value


@pytest.mark.unit
def test_get_logger_without_name():
    """Test get_logger without name."""
    with patch("common.logging.logging.getLogger") as mock_getLogger:
        logger = get_logger()
        mock_getLogger.assert_called_once_with(None)
        assert logger is mock_getLogger.return_value


@pytest.mark.unit
def test_get_logger_multiple_calls():
    """Test get_logger with multiple calls."""
    with patch("common.logging.logging.getLogger") as mock_getLogger:
        logger1 = get_logger("test_logger")
        logger2 = get_logger("test_logger")
        assert logger1 is logger2
        assert mock_getLogger.call_count == 2


@pytest.mark.unit
def test_setup_logging_default_values():
    """Test setup_logging with default values."""
    with patch("common.logging.logging.basicConfig") as mock_basicConfig:
        setup_logging()
        mock_basicConfig.assert_called_once()


@pytest.mark.unit
def test_get_logger_caching():
    """Test get_logger caching behavior."""
    with patch("common.logging.logging.getLogger") as mock_getLogger:
        mock_logger = MagicMock()
        mock_getLogger.return_value = mock_logger

        get_logger("test_logger")
        get_logger("test_logger")

        # Should call getLogger twice (no caching in this implementation)
        assert mock_getLogger.call_count == 2


@pytest.mark.unit
def test_setup_logging_exception_handling():
    """Test setup_logging exception handling."""
    with patch(
        "common.logging.logging.basicConfig", side_effect=Exception("Config error")
    ):
        # Should not raise exception
        setup_logging()


@pytest.mark.unit
def test_get_logger_exception_handling():
    """Test get_logger exception handling."""
    with patch(
        "common.logging.logging.getLogger", side_effect=Exception("Logger error")
    ):
        # Should not raise exception
        logger = get_logger("test_logger")
        assert logger is None


@pytest.mark.unit
def test_setup_logging_with_invalid_level():
    """Test setup_logging with invalid level."""
    with patch("common.logging.logging.basicConfig") as mock_basicConfig:
        setup_logging(level="INVALID")
        mock_basicConfig.assert_called_once()


@pytest.mark.unit
def test_get_logger_with_special_characters():
    """Test get_logger with special characters in name."""
    with patch("common.logging.logging.getLogger") as mock_getLogger:
        get_logger("test-logger_123")
        mock_getLogger.assert_called_once_with("test-logger_123")


@pytest.mark.unit
def test_setup_logging_with_empty_format():
    """Test setup_logging with empty format string."""
    with patch("common.logging.logging.basicConfig") as mock_basicConfig:
        setup_logging(format_string="")
        mock_basicConfig.assert_called_once()


@pytest.mark.unit
def test_setup_logging_with_none_values():
    """Test setup_logging with None values."""
    with patch("common.logging.logging.basicConfig") as mock_basicConfig:
        setup_logging(level=None, format_string=None, log_file=None)
        mock_basicConfig.assert_called_once()
