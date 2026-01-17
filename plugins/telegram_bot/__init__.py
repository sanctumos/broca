"""Telegram bot plugin using aiogram."""

from importlib import import_module
from typing import Any

__all__ = ["TelegramBotPlugin"]


def __getattr__(name: str) -> Any:
    if name == "TelegramBotPlugin":
        return getattr(import_module("plugins.telegram_bot.plugin"), name)
    raise AttributeError(f"module {__name__} has no attribute {name}")
