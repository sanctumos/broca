"""Centralized logging configuration for the application."""

import logging


def setup_logging(level: int | None = logging.INFO) -> None:
    """Configure the root logger with standard formatting.

    Args:
        level: Optional logging level. Defaults to INFO.
    """
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
