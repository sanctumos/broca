"""Tests for common.logging module."""

import logging
from unittest.mock import patch
from common.logging import setup_logging

def test_setup_logging_default_level():
    """Test that setup_logging uses INFO level by default."""
    with patch("logging.basicConfig") as mock_basic_config:
        setup_logging()
        mock_basic_config.assert_called_once()
        call_args = mock_basic_config.call_args[1]
        assert call_args["level"] == logging.INFO
        assert "[%(asctime)s] [%(levelname)s] %(message)s" in call_args["format"]
        assert "%Y-%m-%d %H:%M:%S" in call_args["datefmt"]

def test_setup_logging_custom_level():
    """Test that setup_logging accepts custom logging levels."""
    with patch("logging.basicConfig") as mock_basic_config:
        setup_logging(level=logging.DEBUG)
        mock_basic_config.assert_called_once()
        call_args = mock_basic_config.call_args[1]
        assert call_args["level"] == logging.DEBUG 