"""Telegram delivery: send markdown text using aiogram (polling bot or ephemeral session)."""

from __future__ import annotations

import logging
from typing import Any

from common.config import get_env_var
from common.telegram_markdown import preserve_telegram_markdown
from database.models import PlatformProfile

logger = logging.getLogger(__name__)


async def deliver_telegram_markdown(
    profile: PlatformProfile,
    markdown_text: str,
    *,
    bot: Any | None = None,
    message_id: int | None = None,
) -> dict[str, Any]:
    """Send formatted text to the Telegram user for this profile.

    When ``bot`` is the running aiogram Bot (broca process), reuses its session.
    When ``bot`` is None (CLI outbound), opens a short-lived Bot session.
    """
    try:
        chat_id = int(profile.platform_user_id)
    except (TypeError, ValueError) as e:
        raise ValueError(
            f"Invalid Telegram platform_user_id: {profile.platform_user_id!r}"
        ) from e

    formatted = preserve_telegram_markdown(markdown_text)
    ctx = f"message_id={message_id}" if message_id is not None else "outbound"

    async def _send(client: Any) -> dict[str, Any]:
        try:
            msg = await client.send_message(
                chat_id=chat_id, text=formatted, parse_mode="Markdown"
            )
        except Exception as e:
            if "can't parse entities" in str(e).lower():
                msg = await client.send_message(chat_id=chat_id, text=formatted)
            else:
                logger.error("Telegram send failed (%s): %s", ctx, e)
                raise
        return {"telegram_message_id": msg.message_id, "chat_id": msg.chat.id}

    if bot is not None:
        return await _send(bot)

    from aiogram import Bot

    token = get_env_var("TELEGRAM_BOT_TOKEN", required=True)
    async with Bot(token=token) as ephemeral:
        return await _send(ephemeral)
