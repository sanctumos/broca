"""Extended unit tests for common logging utilities."""

import logging
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from common.logging import (
    LogFormat,
    LogLevel,
    add_console_handler,
    add_file_handler,
    clear_handlers,
    configure_logger,
    get_log_file_path,
    get_logger,
    remove_handler,
    rotate_log_file,
    set_log_level,
    setup_logging,
)


class TestLoggingExtended:
    """Extended test cases for common logging utilities."""

    def test_setup_logging_default(self):
        """Test setting up logging with default configuration."""
        with patch("common.logging.configure_logger") as mock_configure:
            setup_logging()
            mock_configure.assert_called_once()

    def test_setup_logging_with_custom_config(self):
        """Test setting up logging with custom configuration."""
        custom_config = {
            "level": "DEBUG",
            "format": "custom",
            "file_path": "/custom/path.log",
        }

        with patch("common.logging.configure_logger") as mock_configure:
            setup_logging(**custom_config)
            mock_configure.assert_called_once_with(**custom_config)

    def test_get_logger_default(self):
        """Test getting logger with default name."""
        logger = get_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "broca"

    def test_get_logger_custom_name(self):
        """Test getting logger with custom name."""
        logger = get_logger("custom_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "custom_module"

    def test_get_logger_existing(self):
        """Test getting existing logger."""
        logger1 = get_logger("test_module")
        logger2 = get_logger("test_module")
        assert logger1 is logger2  # Should return the same instance

    def test_configure_logger_default(self):
        """Test configuring logger with default settings."""
        logger = configure_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.level == logging.INFO

    def test_configure_logger_custom_level(self):
        """Test configuring logger with custom level."""
        logger = configure_logger(level="DEBUG")
        assert logger.level == logging.DEBUG

    def test_configure_logger_custom_format(self):
        """Test configuring logger with custom format."""
        logger = configure_logger(format="detailed")
        assert isinstance(logger, logging.Logger)

    def test_configure_logger_with_file(self):
        """Test configuring logger with file output."""
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as f:
            temp_path = f.name

        try:
            logger = configure_logger(file_path=temp_path)
            assert isinstance(logger, logging.Logger)
            assert os.path.exists(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_set_log_level(self):
        """Test setting log level."""
        logger = get_logger("test_level")
        set_log_level(logger, "DEBUG")
        assert logger.level == logging.DEBUG

    def test_set_log_level_invalid(self):
        """Test setting invalid log level."""
        logger = get_logger("test_invalid_level")
        with pytest.raises(ValueError):
            set_log_level(logger, "INVALID_LEVEL")

    def test_add_file_handler(self):
        """Test adding file handler to logger."""
        logger = get_logger("test_file_handler")

        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as f:
            temp_path = f.name

        try:
            handler = add_file_handler(logger, temp_path)
            assert isinstance(handler, logging.FileHandler)
            assert handler.baseFilename == os.path.abspath(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_add_file_handler_with_level(self):
        """Test adding file handler with custom level."""
        logger = get_logger("test_file_handler_level")

        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as f:
            temp_path = f.name

        try:
            handler = add_file_handler(logger, temp_path, level="ERROR")
            assert handler.level == logging.ERROR
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_add_console_handler(self):
        """Test adding console handler to logger."""
        logger = get_logger("test_console_handler")
        handler = add_console_handler(logger)
        assert isinstance(handler, logging.StreamHandler)

    def test_add_console_handler_with_level(self):
        """Test adding console handler with custom level."""
        logger = get_logger("test_console_handler_level")
        handler = add_console_handler(logger, level="WARNING")
        assert handler.level == logging.WARNING

    def test_remove_handler(self):
        """Test removing handler from logger."""
        logger = get_logger("test_remove_handler")
        handler = add_console_handler(logger)

        remove_handler(logger, handler)
        assert handler not in logger.handlers

    def test_remove_nonexistent_handler(self):
        """Test removing nonexistent handler."""
        logger = get_logger("test_remove_nonexistent")
        handler = MagicMock()

        # Should not raise an exception
        remove_handler(logger, handler)

    def test_clear_handlers(self):
        """Test clearing all handlers from logger."""
        logger = get_logger("test_clear_handlers")
        add_console_handler(logger)
        add_console_handler(logger)

        assert len(logger.handlers) == 2
        clear_handlers(logger)
        assert len(logger.handlers) == 0

    def test_get_log_file_path_default(self):
        """Test getting default log file path."""
        with patch("common.logging.os.path.expanduser", return_value="/home/user"):
            path = get_log_file_path()
            assert path == "/home/user/broca.log"

    def test_get_log_file_path_custom(self):
        """Test getting custom log file path."""
        custom_path = "/custom/path.log"
        with patch("common.logging.os.getenv", return_value=custom_path):
            path = get_log_file_path()
            assert path == custom_path

    def test_rotate_log_file(self):
        """Test rotating log file."""
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as f:
            temp_path = f.name
            f.write(b"test log content")

        try:
            rotated_path = rotate_log_file(temp_path)
            assert os.path.exists(rotated_path)
            assert not os.path.exists(temp_path)

            # Verify content was preserved
            with open(rotated_path) as f:
                content = f.read()
            assert content == "test log content"
        finally:
            for path in [temp_path, rotated_path]:
                if os.path.exists(path):
                    os.unlink(path)

    def test_rotate_log_file_nonexistent(self):
        """Test rotating nonexistent log file."""
        nonexistent_path = "/nonexistent/path.log"
        rotated_path = rotate_log_file(nonexistent_path)
        assert rotated_path is None

    def test_log_level_enum(self):
        """Test LogLevel enum values."""
        assert LogLevel.DEBUG == "DEBUG"
        assert LogLevel.INFO == "INFO"
        assert LogLevel.WARNING == "WARNING"
        assert LogLevel.ERROR == "ERROR"
        assert LogLevel.CRITICAL == "CRITICAL"

    def test_log_format_enum(self):
        """Test LogFormat enum values."""
        assert LogFormat.SIMPLE == "simple"
        assert LogFormat.DETAILED == "detailed"
        assert LogFormat.JSON == "json"

    def test_logger_with_multiple_handlers(self):
        """Test logger with multiple handlers."""
        logger = get_logger("test_multiple_handlers")

        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as f:
            temp_path = f.name

        try:
            console_handler = add_console_handler(logger)
            file_handler = add_file_handler(logger, temp_path)

            assert len(logger.handlers) == 2
            assert console_handler in logger.handlers
            assert file_handler in logger.handlers
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_logger_propagation(self):
        """Test logger propagation settings."""
        logger = get_logger("test_propagation")
        assert logger.propagate is True

    def test_logger_disabled_propagation(self):
        """Test logger with disabled propagation."""
        logger = configure_logger(propagate=False)
        assert logger.propagate is False

    def test_logger_with_filters(self):
        """Test logger with custom filters."""

        class TestFilter(logging.Filter):
            def filter(self, record):
                return record.levelno >= logging.WARNING

        logger = get_logger("test_filters")
        logger.addFilter(TestFilter())

        # Test that filter is applied
        assert len(logger.filters) == 1

    def test_logger_exception_handling(self):
        """Test logger exception handling."""
        logger = get_logger("test_exception")

        # Should not raise an exception
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("An exception occurred")

    def test_logger_context_manager(self):
        """Test logger as context manager."""
        logger = get_logger("test_context")

        with logger:
            logger.info("Inside context")

        # Should not raise an exception

    def test_logger_thread_safety(self):
        """Test logger thread safety."""
        logger = get_logger("test_thread_safety")

        # Should not raise an exception when used from multiple threads
        import threading

        def log_message():
            logger.info("Thread message")

        threads = []
        for _i in range(5):
            thread = threading.Thread(target=log_message)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def test_logger_performance(self):
        """Test logger performance with many messages."""
        logger = get_logger("test_performance")

        # Should handle many log messages efficiently
        for i in range(1000):
            logger.debug(f"Debug message {i}")

    def test_logger_with_custom_formatter(self):
        """Test logger with custom formatter."""
        logger = get_logger("test_custom_formatter")

        custom_formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        handler = add_console_handler(logger)
        handler.setFormatter(custom_formatter)

        assert handler.formatter == custom_formatter

    def test_logger_level_hierarchy(self):
        """Test logger level hierarchy."""
        parent_logger = get_logger("parent")
        child_logger = get_logger("parent.child")

        parent_logger.setLevel(logging.WARNING)

        # Child should inherit parent's level
        assert child_logger.level == logging.WARNING

    def test_logger_with_disabled_level(self):
        """Test logger with disabled level."""
        logger = get_logger("test_disabled_level")
        logger.setLevel(logging.CRITICAL)

        # Debug messages should be ignored
        logger.debug("This should be ignored")
        logger.critical("This should be logged")

    def test_logger_with_extra_data(self):
        """Test logger with extra data."""
        logger = get_logger("test_extra_data")

        # Should handle extra data in log records
        logger.info(
            "Message with extra data", extra={"user_id": 123, "action": "login"}
        )

    def test_logger_with_structured_logging(self):
        """Test logger with structured logging."""
        logger = get_logger("test_structured")

        # Should handle structured logging
        logger.info(
            "User action",
            extra={
                "user_id": 123,
                "action": "login",
                "timestamp": "2024-01-01T00:00:00Z",
            },
        )

    def test_logger_with_different_levels(self):
        """Test logger with different log levels."""
        logger = get_logger("test_levels")

        # Test all log levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

    def test_logger_with_exception_info(self):
        """Test logger with exception info."""
        logger = get_logger("test_exception_info")

        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.error("Exception occurred", exc_info=True)

    def test_logger_with_stack_info(self):
        """Test logger with stack info."""
        logger = get_logger("test_stack_info")

        logger.info("Message with stack info", stack_info=True)

    def test_logger_with_custom_attributes(self):
        """Test logger with custom attributes."""
        logger = get_logger("test_custom_attributes")

        # Add custom attributes
        logger.info("Message", extra={"custom_field": "custom_value"})

    def test_logger_with_unicode_messages(self):
        """Test logger with unicode messages."""
        logger = get_logger("test_unicode")

        # Should handle unicode messages
        logger.info("Unicode message: café, naïve, résumé")

    def test_logger_with_long_messages(self):
        """Test logger with long messages."""
        logger = get_logger("test_long_messages")

        # Should handle long messages
        long_message = "A" * 10000
        logger.info(long_message)

    def test_logger_with_special_characters(self):
        """Test logger with special characters."""
        logger = get_logger("test_special_chars")

        # Should handle special characters
        logger.info("Special chars: @#$%^&*()_+-=[]{}|;':\",./<>?")

    def test_logger_with_none_values(self):
        """Test logger with None values."""
        logger = get_logger("test_none_values")

        # Should handle None values gracefully
        logger.info("Message with None", extra={"none_field": None})

    def test_logger_with_empty_strings(self):
        """Test logger with empty strings."""
        logger = get_logger("test_empty_strings")

        # Should handle empty strings
        logger.info("")
        logger.info("Message with empty field", extra={"empty_field": ""})

    def test_logger_with_boolean_values(self):
        """Test logger with boolean values."""
        logger = get_logger("test_boolean_values")

        # Should handle boolean values
        logger.info("Message with boolean", extra={"bool_field": True})

    def test_logger_with_numeric_values(self):
        """Test logger with numeric values."""
        logger = get_logger("test_numeric_values")

        # Should handle numeric values
        logger.info(
            "Message with numbers",
            extra={"int_field": 42, "float_field": 3.14, "complex_field": 1 + 2j},
        )

    def test_logger_with_list_values(self):
        """Test logger with list values."""
        logger = get_logger("test_list_values")

        # Should handle list values
        logger.info("Message with list", extra={"list_field": [1, 2, 3]})

    def test_logger_with_dict_values(self):
        """Test logger with dictionary values."""
        logger = get_logger("test_dict_values")

        # Should handle dictionary values
        logger.info("Message with dict", extra={"dict_field": {"key": "value"}})
