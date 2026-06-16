"""API client for Kitchen POS partner-bridge."""

import logging
from typing import Any, Dict, List, Optional

import aiohttp

from plugins.porter_vernal_webchat.settings import PorterWebChatSettings

logger = logging.getLogger(__name__)


class PorterWebChatAPIClient:
    def __init__(self, settings: PorterWebChatSettings):
        self.settings = settings
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Broca2-Porter-WebChat-Plugin/1.0",
        }

    async def get_messages(
        self, limit: int = 50, offset: int = 0, since: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if not self.session:
            self.session = aiohttp.ClientSession()

        params: Dict[str, Any] = {
            "action": "inbox",
            "limit": min(limit, 100),
            "offset": offset,
        }
        if since:
            params["since"] = since

        url = f"{self.settings.api_url.rstrip('/')}/api/v1/index.php"
        try:
            async with self.session.get(url, headers=self._get_headers(), params=params) as response:
                if response.status != 200:
                    self.logger.error("inbox HTTP %s", response.status)
                    return []
                data = await response.json()
                if data.get("success"):
                    messages = data.get("data", {}).get("messages", [])
                    self.logger.info("Retrieved %s partner-bridge messages", len(messages))
                    return messages
                self.logger.error("inbox error: %s", data.get("error", data.get("message")))
                return []
        except Exception as exc:
            self.logger.error("Error polling partner-bridge inbox: %s", exc)
            return []

    async def post_response(self, session_id: str, response: str, message_id: int = 0) -> bool:
        if not self.session:
            self.session = aiohttp.ClientSession()

        payload: Dict[str, Any] = {"session_id": session_id, "response": response}
        if message_id:
            payload["message_id"] = message_id

        url = f"{self.settings.api_url.rstrip('/')}/api/v1/index.php"
        try:
            async with self.session.post(
                url,
                headers=self._get_headers(),
                params={"action": "outbox"},
                json=payload,
            ) as resp:
                if resp.status != 200:
                    self.logger.error("outbox HTTP %s", resp.status)
                    return False
                body = await resp.json()
                if body.get("success"):
                    return True
                self.logger.error("outbox error: %s", body.get("error", body.get("message")))
                return False
        except Exception as exc:
            self.logger.error("Error posting partner-bridge outbox: %s", exc)
            return False

    async def test_connection(self) -> bool:
        try:
            await self.get_messages(limit=1)
            return True
        except Exception as exc:
            self.logger.error("Connection test failed: %s", exc)
            return False
