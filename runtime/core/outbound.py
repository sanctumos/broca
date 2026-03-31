"""Headless outbound messaging (CLI / SMCP), per broca-3.1-outbound-mcp-planning.md."""

from __future__ import annotations

import logging
from typing import Any

from common.config import get_env_var
from database.operations.messages import insert_message
from database.operations.users import get_platform_profile_for_user_platform
from database.models import PlatformProfile
from runtime.platforms.telegram_delivery import deliver_telegram_markdown

logger = logging.getLogger(__name__)


def _outbound_enabled() -> bool:
    raw = get_env_var("ENABLE_OUTBOUND_TOOL", default="false")
    return str(raw).lower() in ("true", "1", "yes")


async def send_outbound_message(
    *,
    letta_user_id: int,
    platform: str,
    message: str,
    dry_run: bool = False,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    """Validate, optionally audit in DB, deliver via the platform path.

    v1 supports ``platform=telegram`` only (ephemeral aiogram session from CLI).
    """
    if not _outbound_enabled() and not dry_run:
        return {
            "success": False,
            "message_id": None,
            "routed_to_platform": None,
            "platform_user_id": None,
            "delivery_status": None,
            "error": "outbound_disabled",
            "hint": "Set ENABLE_OUTBOUND_TOOL=true for this Broca instance.",
            "idempotency_key": idempotency_key,
        }

    platform_norm = (platform or "").strip().lower()
    if not platform_norm:
        return {
            "success": False,
            "message_id": None,
            "routed_to_platform": None,
            "platform_user_id": None,
            "delivery_status": None,
            "error": "invalid_platform",
            "idempotency_key": idempotency_key,
        }

    profile = await get_platform_profile_for_user_platform(
        letta_user_id, platform_norm
    )
    if not profile:
        return {
            "success": False,
            "message_id": None,
            "routed_to_platform": platform_norm,
            "platform_user_id": None,
            "delivery_status": None,
            "error": "profile_not_found",
            "idempotency_key": idempotency_key,
        }

    if dry_run:
        return {
            "success": True,
            "message_id": None,
            "routed_to_platform": platform_norm,
            "platform_user_id": profile.platform_user_id,
            "delivery_status": "dry_run",
            "error": None,
            "idempotency_key": idempotency_key,
        }

    profile = _ensure_profile_id(profile)
    msg_row_id = await insert_message(
        letta_user_id=letta_user_id,
        platform_profile_id=profile.id,
        role="assistant",
        message=message,
    )

    if platform_norm != "telegram":
        return {
            "success": False,
            "message_id": msg_row_id,
            "routed_to_platform": platform_norm,
            "platform_user_id": profile.platform_user_id,
            "delivery_status": None,
            "error": "platform_not_supported",
            "idempotency_key": idempotency_key,
        }

    try:
        delivery = await deliver_telegram_markdown(
            profile, message, bot=None, message_id=msg_row_id
        )
    except Exception as e:
        logger.exception("Outbound Telegram delivery failed")
        return {
            "success": False,
            "message_id": msg_row_id,
            "routed_to_platform": platform_norm,
            "platform_user_id": profile.platform_user_id,
            "delivery_status": "handler_failed",
            "error": str(e),
            "idempotency_key": idempotency_key,
        }

    return {
        "success": True,
        "message_id": msg_row_id,
        "routed_to_platform": platform_norm,
        "platform_user_id": profile.platform_user_id,
        "delivery_status": "sent",
        "error": None,
        "delivery_detail": delivery,
        "idempotency_key": idempotency_key,
    }


def _ensure_profile_id(profile: PlatformProfile) -> PlatformProfile:
    if profile.id is None:
        raise ValueError("platform profile missing id")
    return profile
