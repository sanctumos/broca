"""Centralized logging configuration for the application."""

import logging

from .config import get_env_var


def setup_logging(level: int | None = None) -> None:
    """Configure the root logger with standard formatting.

    Args:
        level: Optional logging level. If None, will try to get from LOG_LEVEL env var.
               Defaults to INFO if not specified.
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

    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
