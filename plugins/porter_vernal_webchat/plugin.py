"""Porter Vernal Web Chat Plugin for Broca2 — polls Kitchen POS partner-bridge."""

import asyncio
import json
import logging
from typing import Any, Dict, Optional

from plugins import Plugin
from plugins.porter_vernal_webchat.api_client import PorterWebChatAPIClient
from plugins.porter_vernal_webchat.message_handler import PorterWebChatMessageHandler
from plugins.porter_vernal_webchat.settings import PorterWebChatSettings

logger = logging.getLogger(__name__)


class PorterVernalWebChatPlugin(Plugin):
    def __init__(self, settings: Optional[PorterWebChatSettings] = None):
        self.settings = settings
        self.api_client: Optional[PorterWebChatAPIClient] = None
        self.message_handler: Optional[PorterWebChatMessageHandler] = None
        self.polling_task: Optional[asyncio.Task] = None
        self.is_running = False
        self.logger = logging.getLogger(__name__)
        self.processed_messages: set[str] = set()

    def get_name(self) -> str:
        if self.settings is None:
            return "porter_vernal_webchat"
        return self.settings.plugin_name

    def get_platform(self) -> str:
        if self.settings is None:
            return "porter_vernal_webchat"
        return self.settings.platform_name

    def get_message_handler(self):
        return self._handle_response

    async def start(self):
        if self.is_running:
            return
        if self.settings is None:
            self.settings = PorterWebChatSettings.from_env()
        self.api_client = PorterWebChatAPIClient(self.settings)
        self.message_handler = PorterWebChatMessageHandler(self.settings.platform_name)
        if not await self.api_client.test_connection():
            self.logger.error("Failed to connect to partner-bridge API")
            return
        self.is_running = True
        self.polling_task = asyncio.create_task(self._poll_messages())
        self.logger.info("Porter Vernal Web Chat Plugin started")

    async def stop(self):
        if not self.is_running:
            return
        self.is_running = False
        if self.polling_task:
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass
        if self.api_client and self.api_client.session:
            await self.api_client.session.close()
        self.logger.info("Porter Vernal Web Chat Plugin stopped")

    def get_settings(self) -> Dict[str, Any]:
        if self.settings is None:
            try:
                self.settings = PorterWebChatSettings.from_env()
            except Exception:
                return {}
        return self.settings.to_dict()

    def validate_settings(self) -> bool:
        return self.settings.validate_settings() if self.settings else False

    def apply_settings(self, settings: Dict[str, Any]) -> None:
        if settings:
            self.settings = PorterWebChatSettings.from_dict(settings)

    async def _poll_messages(self):
        while self.is_running:
            try:
                messages = await self.api_client.get_messages(limit=50)
                for message_data in messages:
                    if not self.is_running:
                        break
                    await self._process_message(message_data)
                await asyncio.sleep(self.settings.poll_interval)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                self.logger.error("Porter poll error: %s", exc)
                await asyncio.sleep(self.settings.retry_delay)

    async def _process_message(self, message_data: Dict[str, Any]):
        message_id = (
            f"{message_data.get('session_id')}_{message_data.get('id')}_{message_data.get('timestamp')}"
        )
        if message_id in self.processed_messages:
            return
        message = await self.message_handler.process_incoming_message(message_data)
        if message:
            self.processed_messages.add(message_id)

    async def send_response(self, session_id: str, response_text: str, original_message=None) -> bool:
        if not self.api_client:
            return False
        if original_message:
            await self.message_handler.process_outgoing_message(session_id, response_text, original_message)
        mid = 0
        if original_message and getattr(original_message, "metadata", None):
            meta = original_message.metadata
            if isinstance(meta, str):
                meta = json.loads(meta)
            if isinstance(meta, dict):
                mid = int(meta.get("broca_message_id") or 0)
        return await self.api_client.post_response(session_id, response_text, message_id=mid)

    async def _handle_response(self, response: str, profile, message_id: int) -> None:
        try:
            metadata = profile.metadata
            if isinstance(metadata, str):
                metadata = json.loads(metadata)
            session_id = (metadata or {}).get("session_id")
            if not session_id:
                self.logger.error("No session_id in profile metadata for message %s", message_id)
                return
            await self.send_response(session_id, response)
        except Exception as exc:
            self.logger.error("Error handling Porter response for message %s: %s", message_id, exc)

    def register_event_handler(self, event_type, handler):
        pass

    def emit_event(self, event):
        pass
