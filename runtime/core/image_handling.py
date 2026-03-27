"""
Extensible image handling for plugins.

Reads ENABLE_IMAGE_HANDLING and ENABLE_TMPFILES_IMAGE_ADDENDUM from env.
Provides build_message_for_agent(text, image_paths) so any plugin can build
the single string to store in the DB (with optional [Image Attachment: url] lines).
No plugin imports in this module.
"""

import logging
from collections.abc import Sequence
from pathlib import Path

from common.config import get_env_var
from common.tmpfiles import upload_file as tmpfiles_upload_file

from .message import MessageFormatter

logger = logging.getLogger(__name__)

_ENABLE_IMAGE_HANDLING: bool | None = None
_ENABLE_TMPFILES_IMAGE_ADDENDUM: bool | None = None


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in ("true", "1", "yes")


def _get_image_handling_enabled() -> bool:
    global _ENABLE_IMAGE_HANDLING
    if _ENABLE_IMAGE_HANDLING is None:
        raw = get_env_var("ENABLE_IMAGE_HANDLING", default="false")
        _ENABLE_IMAGE_HANDLING = _parse_bool(str(raw))
    return _ENABLE_IMAGE_HANDLING


def _get_tmpfiles_addendum_enabled() -> bool:
    global _ENABLE_TMPFILES_IMAGE_ADDENDUM
    if _ENABLE_TMPFILES_IMAGE_ADDENDUM is None:
        raw = get_env_var("ENABLE_TMPFILES_IMAGE_ADDENDUM", default="false")
        _ENABLE_TMPFILES_IMAGE_ADDENDUM = _parse_bool(str(raw))
    return _ENABLE_TMPFILES_IMAGE_ADDENDUM


def image_handling_enabled() -> bool:
    """Return True if ENABLE_IMAGE_HANDLING is set to a truthy value."""
    return _get_image_handling_enabled()


def tmpfiles_addendum_enabled() -> bool:
    """Return True if ENABLE_TMPFILES_IMAGE_ADDENDUM is set to a truthy value."""
    return _get_tmpfiles_addendum_enabled()


def build_message_for_agent(
    text: str,
    image_paths: Sequence[Path] | None = None,
) -> str:
    """
    Build the single message string for the agent (to store in DB and enqueue).

    - If image handling is off or image_paths is None/empty: return sanitized text only.
    - If image handling is on and image_paths non-empty and tmpfiles addendum on:
      for each path upload to tmpfiles.org, append \\n[Image Attachment: <direct_url>];
      on upload failure log and skip that image.
    - If image handling is on and tmpfiles addendum off: use only sanitized text.
    """
    sanitized = MessageFormatter.sanitize_text(text or "")
    if not _get_image_handling_enabled():
        return sanitized
    paths = list(image_paths) if image_paths else []
    if not paths:
        return sanitized
    if not _get_tmpfiles_addendum_enabled():
        return sanitized
    parts = [sanitized]
    for path in paths:
        if not path.exists():
            logger.warning("Image path does not exist, skipping: %s", path)
            continue
        try:
            direct_url = tmpfiles_upload_file(path)
            parts.append(f"[Image Attachment: {direct_url}]")
        except Exception as e:
            logger.warning("tmpfiles upload failed for %s: %s", path, e)
    return "\n".join(parts)
