"""
Message Handler for Web Chat Plugin

This module handles processing of incoming web chat messages and
integration with Broca2's database and queue systems.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from database.operations.messages import count_messages_for_letta_user, insert_message
from database.operations.queue import add_to_queue
from database.operations.users import (
    get_letta_user_block_id,
    get_or_create_platform_profile,
)
from runtime.core.letta_client import get_letta_client
from runtime.core.message import Message

logger = logging.getLogger(__name__)

# Stable identity lines Broca owns; anything after these is preserved (agent notes).
_HUMAN_BLOCK_OWNED_PREFIXES = (
    "About Me (",
    "Tasks username:",
    "Tasks user id:",
    "Broca platform_user_id:",
    "Channel: Sanctum Tasks",
    "First conversation with Q Vernal:",
)


class WebChatMessageHandler:
    """Handles processing of web chat messages and integration with Broca2."""

    def __init__(self, platform_name: str = "web_chat"):
        self.platform_name = platform_name
        self.logger = logging.getLogger(__name__)

    def _publish_chatter_context(self, tasks_user_id: int) -> None:
        """Write active chatter id for Q Vernal SMCP (plugin-only; not Broca core)."""
        if tasks_user_id <= 0:
            return
        run_dir = Path(os.getenv("BROCA_RUN_DIR", "/opt/broca-q/run"))
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / "current_tasks_user_id.txt"
        path.write_text(str(tasks_user_id), encoding="utf-8")
        self.logger.debug("Published chatter context for SMCP: user_id=%s", tasks_user_id)
        # Best-effort: if queue already wrote an active-turn sidecar, fill tasks_user_id.
        # Primary ownership is dequeue-time write in runtime.core.queue.
        try:
            from runtime.core.active_turn import maybe_set_tasks_user_id

            maybe_set_tasks_user_id(tasks_user_id)
        except Exception as exc:
            self.logger.debug("active-turn tasks_user_id assist skipped: %s", exc)

    @staticmethod
    def _parse_tasks_user_id(raw: Any) -> Optional[int]:
        try:
            uid = int(raw)
        except (TypeError, ValueError):
            return None
        return uid if uid > 0 else None

    @staticmethod
    def _tasks_platform_user_id(tasks_user_id: int) -> str:
        return f"tasks:{tasks_user_id}"

    @staticmethod
    def _first_contact_prefix(
        tasks_username: str, tasks_user_id: int, display_name: str
    ) -> str:
        who = tasks_username or display_name or f"user {tasks_user_id}"
        return (
            "[System — first conversation with this Tasks user]\n"
            f"This is the first time you are speaking with **{who}** "
            f"(Tasks user id {tasks_user_id}). Greet them by username. "
            "Their Letta human block is tied to this Tasks user — "
            "you may add notes there as you learn about them.\n\n"
            "---\n\n"
        )

    @staticmethod
    def _parse_existing_human_block(raw: Optional[str]) -> Tuple[Optional[str], str]:
        """Return (created_at, content) from an existing human block value."""
        if not raw:
            return None, ""
        try:
            parsed = json.loads(raw)
        except (TypeError, ValueError, json.JSONDecodeError):
            return None, str(raw)
        if not isinstance(parsed, dict):
            return None, str(raw)
        data = parsed.get("data") if parsed.get("type") == "human_core" else parsed
        if not isinstance(data, dict):
            return None, str(raw)
        created = data.get("created_at")
        content = data.get("content") or ""
        return (str(created) if created else None), str(content)

    @staticmethod
    def _preserve_agent_notes(existing_content: str) -> str:
        """Keep freeform lines after Broca-owned identity headers."""
        if not existing_content:
            return ""
        extras: list[str] = []
        for line in existing_content.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if any(stripped.startswith(p) for p in _HUMAN_BLOCK_OWNED_PREFIXES):
                continue
            extras.append(line)
        return "\n".join(extras).strip()

    async def _sync_human_block(
        self,
        letta_user_id: int,
        tasks_username: str,
        tasks_user_id: int,
        *,
        is_first_contact: bool,
        profile_created_at: Optional[str] = None,
    ) -> None:
        block_id = await get_letta_user_block_id(letta_user_id)
        if not block_id:
            return

        client = get_letta_client()
        existing_created_at: Optional[str] = None
        existing_content = ""
        try:
            block = await asyncio.to_thread(client.blocks.retrieve, block_id=block_id)
            raw_value = getattr(block, "value", None) or (
                block.get("value") if isinstance(block, dict) else None
            )
            existing_created_at, existing_content = self._parse_existing_human_block(
                raw_value
            )
        except Exception as exc:
            self.logger.debug("Could not read existing human block %s: %s", block_id, exc)

        # Never mint a fresh created_at for returning users — that reads as "new user".
        created_at = (
            existing_created_at
            or profile_created_at
            or datetime.utcnow().isoformat()
        )

        lines = [
            f"About Me ({tasks_username})",
            f"Tasks username: {tasks_username}",
            f"Tasks user id: {tasks_user_id}",
            f"Broca platform_user_id: {self._tasks_platform_user_id(tasks_user_id)}",
            "Channel: Sanctum Tasks — Ask Q webchat",
        ]
        if is_first_contact and "First conversation with Q Vernal:" not in existing_content:
            lines.append(
                f"First conversation with Q Vernal: {datetime.utcnow().isoformat()}Z"
            )
        elif "First conversation with Q Vernal:" in existing_content:
            for line in existing_content.splitlines():
                if line.strip().startswith("First conversation with Q Vernal:"):
                    lines.append(line.strip())
                    break

        notes = self._preserve_agent_notes(existing_content)
        if notes:
            lines.append(notes)

        block_value = json.dumps(
            {
                "type": "human_core",
                "data": {
                    "name": tasks_username,
                    "created_at": created_at,
                    "content": "\n".join(lines),
                },
            }
        )
        try:
            await asyncio.to_thread(
                client.blocks.update,
                block_id=block_id,
                value=block_value,
            )
            self.logger.info(
                "Updated human block for Tasks user %s (%s) created_at=%s first=%s",
                tasks_user_id,
                tasks_username,
                created_at,
                is_first_contact,
            )
        except Exception as exc:
            self.logger.warning("Human block update failed: %s", exc)

    async def _resolve_tasks_chatter_profile(
        self,
        tasks_user_id: int,
        tasks_username: str,
        tasks_display_name: str,
        session_id: str,
        uid: Optional[str],
    ) -> Tuple[Any, Any, str]:
        """
        One Letta identity per Tasks user (platform_user_id tasks:{id}), not per session/uid.
        """
        platform_user_id = self._tasks_platform_user_id(tasks_user_id)
        username = tasks_username
        display_name = tasks_display_name or tasks_username

        profile, letta_user = await get_or_create_platform_profile(
            platform=self.platform_name,
            platform_user_id=platform_user_id,
            username=username,
            display_name=display_name,
            metadata={
                "session_id": session_id,
                "uid": uid,
                "source": "q_vernal_webchat",
                "tasks_user_id": tasks_user_id,
                "tasks_username": tasks_username,
                "identity_scope": "tasks_user",
            },
        )
        return profile, letta_user, platform_user_id

    async def process_incoming_message(self, message_data: Dict[str, Any]) -> Optional[int]:
        """
        Process an incoming message from the web chat API.

        Returns:
            message_id if successfully processed, None otherwise
        """
        try:
            session_id = message_data.get("session_id")
            message_text = message_data.get("message", "")
            timestamp = message_data.get("timestamp")
            uid = message_data.get("uid")
            tasks_user_id = self._parse_tasks_user_id(message_data.get("tasks_user_id"))
            tasks_username = (message_data.get("tasks_username") or "").strip()
            tasks_display_name = (
                message_data.get("tasks_display_name") or tasks_username or ""
            ).strip()
            is_first_contact = bool(message_data.get("is_first_contact"))

            if not session_id or not message_text:
                self.logger.warning("Invalid message data: %s", message_data)
                return None

            if not tasks_user_id:
                self.logger.error(
                    "Rejecting webchat message without tasks_user_id (identity is per Tasks user, not session): %s",
                    message_data,
                )
                return None

            if not tasks_username:
                tasks_username = f"tasks_user_{tasks_user_id}"
                tasks_display_name = tasks_username

            self._publish_chatter_context(tasks_user_id)

            platform_profile, letta_user, platform_user_id = (
                await self._resolve_tasks_chatter_profile(
                    tasks_user_id,
                    tasks_username,
                    tasks_display_name,
                    session_id,
                    uid,
                )
            )

            # Client is_first_contact can lie (session uid churn). Broca history wins.
            prior_msgs = await count_messages_for_letta_user(letta_user.id)
            if prior_msgs > 0 and is_first_contact:
                self.logger.warning(
                    "Ignoring false is_first_contact for tasks_user=%s (%s) "
                    "— Broca already has %s message(s) for letta_user=%s",
                    tasks_user_id,
                    tasks_username,
                    prior_msgs,
                    letta_user.id,
                )
                is_first_contact = False

            await self._sync_human_block(
                letta_user.id,
                tasks_username,
                tasks_user_id,
                is_first_contact=is_first_contact,
                profile_created_at=getattr(platform_profile, "created_at", None),
            )

            # Porter precedent: Layer B chat_context_block before user text.
            prefix_parts = []
            if is_first_contact:
                prefix_parts.append(
                    self._first_contact_prefix(
                        tasks_username, tasks_user_id, tasks_display_name
                    )
                )
            ctx_block = (message_data.get("chat_context_block") or "").strip()
            if ctx_block:
                prefix_parts.append(ctx_block + "\n\n---\n\n")
            agent_message = "".join(prefix_parts) + message_text

            message = Message(
                content=agent_message,
                user_id=platform_user_id,
                username=tasks_username,
                platform=self.platform_name,
                timestamp=datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                if timestamp
                else datetime.utcnow(),
                metadata={
                    "session_id": session_id,
                    "uid": uid,
                    "platform": self.platform_name,
                    "source": "q_vernal_webchat",
                    "tasks_user_id": tasks_user_id,
                    "tasks_username": tasks_username,
                    "is_first_contact": is_first_contact,
                    "letta_user_id": letta_user.id,
                    "platform_profile_id": platform_profile.id,
                    "identity_scope": "tasks_user",
                },
            )

            message_id = await insert_message(
                letta_user_id=letta_user.id,
                platform_profile_id=platform_profile.id,
                role="user",
                message=agent_message,
                timestamp=timestamp,
            )

            await add_to_queue(letta_user_id=letta_user.id, message_id=message_id)

            self.logger.info(
                "Processed message session=%s tasks_user=%s (%s) letta_user=%s first=%s",
                session_id,
                tasks_user_id,
                tasks_username,
                letta_user.id,
                is_first_contact,
            )
            return message_id

        except Exception as e:
            self.logger.error("Error processing incoming message: %s", e)
            return None

    async def process_outgoing_message(
        self,
        session_id: str,
        response_text: str,
        original_message: Optional[Message] = None,
    ) -> bool:
        """Process an outgoing message to be sent back to the web chat."""
        try:
            if not original_message:
                self.logger.warning(
                    "No original message provided for response to session %s",
                    session_id,
                )
                return False

            outgoing_message = Message(
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

            await insert_message(outgoing_message)

            self.logger.info("Processed outgoing message for session %s", session_id)
            return True

        except Exception as e:
            self.logger.error("Error processing outgoing message: %s", e)
            return False

    def sanitize_message(self, message_text: str) -> str:
        """Sanitize message text for safe processing."""
        if not message_text:
            return ""
        sanitized = message_text.replace("\x00", "").strip()
        if len(sanitized) > 4000:
            sanitized = sanitized[:4000] + "..."
        return sanitized
