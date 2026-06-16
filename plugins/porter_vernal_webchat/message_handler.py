"""Message handler for Porter Vernal partner-bridge webchat."""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from database.operations.messages import insert_message
from database.operations.queue import add_to_queue
from database.operations.users import get_letta_user_block_id, get_or_create_platform_profile
from runtime.core.letta_client import get_letta_client
from runtime.core.message import Message

logger = logging.getLogger(__name__)


class PorterWebChatMessageHandler:
    def __init__(self, platform_name: str = "porter_vernal_webchat"):
        self.platform_name = platform_name
        self.logger = logging.getLogger(__name__)

    def _publish_chatter_context(self, partner_user_id: int) -> None:
        if partner_user_id <= 0:
            return
        run_dir = Path(os.getenv("BROCA_RUN_DIR", "/opt/broca-porter/run"))
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / "current_partner_user_id.txt"
        path.write_text(str(partner_user_id), encoding="utf-8")

    @staticmethod
    def _parse_partner_user_id(raw: Any) -> Optional[int]:
        try:
            uid = int(raw)
        except (TypeError, ValueError):
            return None
        return uid if uid > 0 else None

    @staticmethod
    def _partner_platform_user_id(partner_user_id: int) -> str:
        return f"partner:{partner_user_id}"

    @staticmethod
    def _chat_context_prefix(message_data: Dict[str, Any]) -> str:
        block = (message_data.get("chat_context_block") or "").strip()
        if not block:
            return ""
        return block + "\n\n---\n\n"

    @staticmethod
    def _first_contact_prefix(partner_slug: str, partner_user_id: int, display_name: str) -> str:
        who = partner_slug or display_name or f"partner {partner_user_id}"
        return (
            "[System — first conversation with this partner user]\n"
            f"This is the first time you are speaking with **{who}** "
            f"(partner user id {partner_user_id}). Greet them warmly. "
            "You help with their Kitchen POS partner portal only — never operator admin.\n\n"
            "---\n\n"
        )

    async def _resolve_partner_profile(
        self,
        partner_user_id: int,
        partner_slug: str,
        partner_display_name: str,
        session_id: str,
        uid: Optional[str],
    ) -> Tuple[Any, Any, str]:
        platform_user_id = self._partner_platform_user_id(partner_user_id)
        username = partner_slug or f"partner_{partner_user_id}"
        display_name = partner_display_name or username
        profile, letta_user = await get_or_create_platform_profile(
            platform=self.platform_name,
            platform_user_id=platform_user_id,
            username=username,
            display_name=display_name,
            metadata={
                "session_id": session_id,
                "uid": uid,
                "source": "porter_vernal_webchat",
                "partner_user_id": partner_user_id,
                "partner_slug": partner_slug,
                "identity_scope": "partner_user",
            },
        )
        return profile, letta_user, platform_user_id

    async def process_incoming_message(self, message_data: Dict[str, Any]) -> Optional[int]:
        try:
            session_id = message_data.get("session_id")
            message_text = message_data.get("message", "")
            timestamp = message_data.get("timestamp")
            uid = message_data.get("uid")
            partner_user_id = self._parse_partner_user_id(message_data.get("partner_user_id"))
            partner_slug = (message_data.get("partner_slug") or "").strip()
            partner_display_name = (message_data.get("partner_display_name") or partner_slug or "").strip()
            is_first_contact = bool(message_data.get("is_first_contact"))

            if not session_id or not message_text:
                self.logger.warning("Invalid partner message data: %s", message_data)
                return None
            if not partner_user_id:
                self.logger.error("Rejecting message without partner_user_id: %s", message_data)
                return None
            if not partner_slug:
                partner_slug = f"partner_{partner_user_id}"

            self._publish_chatter_context(partner_user_id)
            platform_profile, letta_user, platform_user_id = await self._resolve_partner_profile(
                partner_user_id,
                partner_slug,
                partner_display_name,
                session_id,
                uid,
            )

            agent_message = message_text
            prefix_parts = []
            if is_first_contact:
                prefix_parts.append(
                    self._first_contact_prefix(partner_slug, partner_user_id, partner_display_name)
                )
            ctx_prefix = self._chat_context_prefix(message_data)
            if ctx_prefix:
                prefix_parts.append(ctx_prefix)
            if prefix_parts:
                agent_message = "".join(prefix_parts) + message_text

            message_id = await insert_message(
                letta_user_id=letta_user.id,
                platform_profile_id=platform_profile.id,
                role="user",
                message=agent_message,
                timestamp=timestamp,
            )
            await add_to_queue(letta_user_id=letta_user.id, message_id=message_id)

            self.logger.info(
                "Processed Porter message session=%s partner_user=%s slug=%s",
                session_id,
                partner_user_id,
                partner_slug,
            )
            return message_id
        except Exception as exc:
            self.logger.error("Error processing Porter incoming message: %s", exc)
            return None

    async def process_outgoing_message(
        self,
        session_id: str,
        response_text: str,
        original_message: Optional[Message] = None,
    ) -> bool:
        try:
            if not original_message:
                return False
            outgoing = Message(
                id=None,
                letta_user_id=original_message.letta_user_id,
                platform_profile_id=original_message.platform_profile_id,
                content=response_text,
                message_type="outgoing",
                timestamp=datetime.utcnow(),
                metadata={
                    "session_id": session_id,
                    "platform": self.platform_name,
                    "source": "broca2_agent",
                    "in_response_to": original_message.id,
                },
            )
            await insert_message(outgoing)
            return True
        except Exception as exc:
            self.logger.error("Error processing Porter outgoing message: %s", exc)
            return False
