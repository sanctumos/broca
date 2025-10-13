"""Centralized logging configuration for the application."""

import logging
import re
from typing import Any

from .config import get_env_var


class SensitiveDataFilter(logging.Filter):
    """Filter to remove sensitive data from log messages."""

    # Patterns for sensitive data
    SENSITIVE_PATTERNS = [
        # API keys and tokens
        (r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([^"\'\s,}]+)', r"\1***REDACTED***"),
        (r'(token["\']?\s*[:=]\s*["\']?)([^"\'\s,}]+)', r"\1***REDACTED***"),
        (r'(bot[_-]?token["\']?\s*[:=]\s*["\']?)([^"\'\s,}]+)', r"\1***REDACTED***"),
        (r'(password["\']?\s*[:=]\s*["\']?)([^"\'\s,}]+)', r"\1***REDACTED***"),
        (r'(secret["\']?\s*[:=]\s*["\']?)([^"\'\s,}]+)', r"\1***REDACTED***"),
        # Authorization headers
        (
            r'(Authorization["\']?\s*[:=]\s*["\']?Bearer\s+)([^"\'\s,}]+)',
            r"\1***REDACTED***",
        ),
        (r'(Authorization["\']?\s*[:=]\s*["\']?)([^"\'\s,}]+)', r"\1***REDACTED***"),
        # Database credentials
        (r'(db[_-]?password["\']?\s*[:=]\s*["\']?)([^"\'\s,}]+)', r"\1***REDACTED***"),
        (
            r'(database[_-]?password["\']?\s*[:=]\s*["\']?)([^"\'\s,}]+)',
            r"\1***REDACTED***",
        ),
        # Phone numbers
        (r"(\+?[1-9]\d{1,14})", r"***REDACTED***"),
        # Email addresses (partial redaction)
        (r"([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", r"***@\2"),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record to remove sensitive data."""
        if hasattr(record, "msg") and isinstance(record.msg, str):
            # Apply all sensitive data patterns
            for pattern, replacement in self.SENSITIVE_PATTERNS:
                record.msg = re.sub(
                    pattern, replacement, record.msg, flags=re.IGNORECASE
                )

        # Also filter args if they contain strings
        if hasattr(record, "args") and record.args:
            filtered_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    filtered_arg = arg
                    for pattern, replacement in self.SENSITIVE_PATTERNS:
                        filtered_arg = re.sub(
                            pattern, replacement, filtered_arg, flags=re.IGNORECASE
                        )
                    filtered_args.append(filtered_arg)
                else:
                    filtered_args.append(arg)
            record.args = tuple(filtered_args)

        return True


class EmojiFormatter(logging.Formatter):
    """Custom formatter that adds emojis to log levels."""

    EMOJI_MAP = {
        logging.DEBUG: "🔍",
        logging.INFO: "🔵",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.CRITICAL: "🚨",
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with emoji prefix."""
        emoji = self.EMOJI_MAP.get(record.levelno, "")
        if emoji:
            record.levelname = f"{emoji} {record.levelname}"
        return super().format(record)


def setup_logging(level: int | None = None, use_emojis: bool = True) -> None:
    """Configure the root logger with standard formatting and security filters.

    Args:
        level: Optional logging level. If None, will try to get from LOG_LEVEL env var.
               Defaults to INFO if not specified.
        use_emojis: Whether to add emojis to log levels. Defaults to True.
    """
    if level is None:
        # Try to get log level from environment variable
        log_level_str = get_env_var("LOG_LEVEL", default="INFO").upper()
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        level = level_map.get(log_level_str, logging.INFO)

    # Get root logger
    root_logger = logging.getLogger()

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler()

    # Set up formatter
    if use_emojis:
        formatter = EmojiFormatter(
            fmt="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)

    # Add sensitive data filter
    console_handler.addFilter(SensitiveDataFilter())

    # Add handler to root logger
    root_logger.addHandler(console_handler)
    root_logger.setLevel(level)

    # Disable propagation for third-party loggers to avoid duplicate messages
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("telethon").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_safe_value(value: Any, max_length: int = 8) -> str:
    """Create a safe representation of a value for logging.

    Args:
        value: The value to log safely
        max_length: Maximum length to show before truncating

    Returns:
        Safe string representation
    """
    if value is None:
        return "None"

    str_value = str(value)
    if len(str_value) <= max_length:
        return str_value

    return f"{str_value[:max_length]}..."


def log_safe_dict(
    data: dict[str, Any], sensitive_keys: set[str] | None = None
) -> dict[str, str]:
    """Create a safe representation of a dictionary for logging.

    Args:
        data: Dictionary to log safely
        sensitive_keys: Set of keys that should be redacted

    Returns:
        Dictionary with safe string representations
    """
    if sensitive_keys is None:
        sensitive_keys = {
            "api_key",
            "token",
            "bot_token",
            "password",
            "secret",
            "authorization",
            "auth",
            "key",
            "credential",
        }

    safe_data = {}
    for key, value in data.items():
        key_lower = key.lower()
        if any(sensitive in key_lower for sensitive in sensitive_keys):
            safe_data[key] = "***REDACTED***"
        else:
            safe_data[key] = log_safe_value(value)

    return safe_data
