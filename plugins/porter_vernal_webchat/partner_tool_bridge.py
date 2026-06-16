"""Resolve per-partner Kitchen POS bridge keys via partner-bridge poll auth."""

from __future__ import annotations

import logging
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)


async def resolve_partner_api_key(
    partner_user_id: int,
    *,
    bridge_api_base: str,
    poll_api_key: str,
    timeout: int = 30,
) -> Optional[str]:
    if partner_user_id <= 0:
        return None
    base = bridge_api_base.rstrip("/") + "/api/v1/index.php"
    url = base + "?action=resolve_partner_key"
    headers = {
        "Authorization": f"Bearer {poll_api_key}",
        "Content-Type": "application/json",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json={"partner_user_id": partner_user_id},
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as resp:
                if resp.status != 200:
                    logger.warning("resolve_partner_key HTTP %s", resp.status)
                    return None
                body = await resp.json()
                if not body.get("success"):
                    return None
                data = body.get("data") or {}
                key = data.get("api_key")
                return str(key) if key else None
    except Exception as exc:
        logger.error("resolve_partner_api_key failed: %s", exc)
        return None
