"""Shared Telegram markdown/code formatting helpers.

This module lives outside `plugins/` so individual plugins can remain
self-contained and not depend on other plugins being installed.
"""

from __future__ import annotations

import re


def preserve_telegram_markdown(text: str) -> str:
    """Preserve common markdown constructs while keeping Telegram compatibility.

    Notes:
    - We intentionally keep this conservative to avoid over-escaping and
      flattening newlines (which breaks fenced code blocks).
    - The behavior here is expected to be shared by both Telegram integrations.
    """

    if not text:
        return text

    # Convert _italic_ to __italic__ (Telegram-style italics)
    text = re.sub(r"_([^_]+)_", r"__\1__", text)

    # Convert *italic* to __italic__ while preserving **bold**
    text = re.sub(r"\*\*([^*]+)\*\*", r"<BOLD>\1</BOLD>", text)
    text = re.sub(r"\*([^*]+)\*", r"__\1__", text)
    text = re.sub(r"<BOLD>([^<]+)</BOLD>", r"**\1**", text)

    # Convert non-standard ..code.. delimiter into fenced blocks
    text = re.sub(r"\.\.\n(.*?)\.\.", r"```\n\1\n```", text, flags=re.DOTALL)

    # Quote blocks: render as a subtle label (Telegram markdown support varies)
    text = re.sub(r"^>\s*(.*?)$", r"*Quote:* \1", text, flags=re.MULTILINE)

    return text.strip()

