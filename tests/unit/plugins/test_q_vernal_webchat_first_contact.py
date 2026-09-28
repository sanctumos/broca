"""Q webchat: first-contact / human-block novelty guards."""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from plugins.q_vernal_webchat.message_handler import WebChatMessageHandler


def test_parse_existing_human_block_preserves_created_at():
    raw = json.dumps(
        {
            "type": "human_core",
            "data": {
                "name": "chuck",
                "created_at": "2026-05-24T23:32:43.208062",
                "content": "About Me (chuck)\nTasks username: chuck\nAgent note: regular",
            },
        }
    )
    created, content = WebChatMessageHandler._parse_existing_human_block(raw)
    assert created == "2026-05-24T23:32:43.208062"
    assert "Agent note: regular" in content


def test_preserve_agent_notes_strips_owned_headers():
    existing = (
        "About Me (chuck)\n"
        "Tasks username: chuck\n"
        "Tasks user id: 11\n"
        "Broca platform_user_id: tasks:11\n"
        "Channel: Sanctum Tasks — Ask Q webchat\n"
        "Prefers plain language briefings"
    )
    notes = WebChatMessageHandler._preserve_agent_notes(existing)
    assert notes == "Prefers plain language briefings"


@pytest.mark.asyncio
async def test_false_first_contact_overridden_when_prior_messages_exist():
    handler = WebChatMessageHandler(platform_name="q_vernal_webchat")
    profile = SimpleNamespace(id=5, created_at="2026-05-24T23:32:43.208062")
    letta_user = SimpleNamespace(id=30)

    with (
        patch.object(handler, "_publish_chatter_context"),
        patch.object(
            handler,
            "_resolve_tasks_chatter_profile",
            new=AsyncMock(return_value=(profile, letta_user, "tasks:11")),
        ),
        patch(
            "plugins.q_vernal_webchat.message_handler.count_messages_for_letta_user",
            new=AsyncMock(return_value=7),
        ),
        patch.object(handler, "_sync_human_block", new=AsyncMock()) as sync_block,
        patch(
            "plugins.q_vernal_webchat.message_handler.insert_message",
            new=AsyncMock(return_value=999),
        ),
        patch(
            "plugins.q_vernal_webchat.message_handler.add_to_queue",
            new=AsyncMock(),
        ),
    ):
        mid = await handler.process_incoming_message(
            {
                "session_id": "session_tasks_11",
                "message": "explain benchlab",
                "timestamp": "2026-09-28T20:05:26.531Z",
                "uid": "7f929bf2bda91a7a",
                "tasks_user_id": 11,
                "tasks_username": "chuck",
                "tasks_display_name": "chuck",
                "is_first_contact": True,  # lying client flag
            }
        )

    assert mid == 999
    sync_block.assert_awaited_once()
    assert sync_block.await_args.kwargs["is_first_contact"] is False
    assert sync_block.await_args.kwargs["profile_created_at"] == profile.created_at


@pytest.mark.asyncio
async def test_sync_human_block_does_not_reset_created_at():
    handler = WebChatMessageHandler(platform_name="q_vernal_webchat")
    existing = json.dumps(
        {
            "type": "human_core",
            "data": {
                "name": "chuck",
                "created_at": "2026-05-24T23:32:43.208062",
                "content": "About Me (chuck)\nTasks username: chuck\nKeeps receipts",
            },
        }
    )
    fake_block = SimpleNamespace(value=existing)
    client = MagicMock()
    client.blocks.retrieve = MagicMock(return_value=fake_block)
    client.blocks.update = MagicMock()

    with (
        patch(
            "plugins.q_vernal_webchat.message_handler.get_letta_user_block_id",
            new=AsyncMock(return_value="block-chuck"),
        ),
        patch(
            "plugins.q_vernal_webchat.message_handler.get_letta_client",
            return_value=client,
        ),
    ):
        await handler._sync_human_block(
            30,
            "chuck",
            11,
            is_first_contact=False,
            profile_created_at="2026-05-24T23:32:43.208062",
        )

    client.blocks.update.assert_called_once()
    payload = json.loads(client.blocks.update.call_args.kwargs["value"])
    assert payload["data"]["created_at"] == "2026-05-24T23:32:43.208062"
    assert "Keeps receipts" in payload["data"]["content"]
    assert "First conversation" not in payload["data"]["content"]
