"""Resolve per-user Tasks API keys via Q bridge (poll-auth only)."""

from __future__ import annotations

import logging
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)


async def resolve_tasks_api_key(
    tasks_user_id: int,
    *,
    bridge_api_base: str,
    poll_api_key: str,
    timeout: int = 30,
) -> Optional[str]:
    """POST resolve_user_key — server returns hidden key for SMCP injection."""
    if tasks_user_id <= 0:
        return None
    base = bridge_api_base.rstrip("/") + "/"
    url = base + "?action=resolve_user_key"
    headers = {
        "Authorization": f"Bearer {poll_api_key}",
        "Content-Type": "application/json",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json={"tasks_user_id": tasks_user_id},
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as resp:
                if resp.status != 200:
                    logger.warning("resolve_user_key HTTP %s", resp.status)
                    return None
                body = await resp.json()
                if not body.get("success"):
                    return None
                data = body.get("data") or {}
                key = data.get("api_key")
                return str(key) if key else None
    except Exception as exc:
        logger.error("resolve_tasks_api_key failed: %s", exc)
        return None
