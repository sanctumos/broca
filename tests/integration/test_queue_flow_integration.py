"""
Integration tests: database + queue processor flow with real DB and mocked agent.

Uses temp_db (real SQLite), real pool, real QueueProcessor in echo mode so
no Letta/agent calls. Verifies full path: seed data -> queue -> process -> DB updated.
"""

import asyncio
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio

from database.operations.messages import insert_message
from database.operations.queue import add_to_queue, atomic_dequeue_item
from database.pool import get_pool
from runtime.core.queue import QueueProcessor


@pytest_asyncio.fixture
async def seeded_queue_item(temp_db: str):
    """Insert one user, profile, message and queue item; yield (letta_user_id, message_id, queue_id)."""
    now = datetime.utcnow().isoformat()
    async with get_pool().connection() as db:
        await db.execute(
            """
            INSERT INTO letta_users (
                created_at, last_active, letta_identity_id, letta_block_id,
                agent_preferences, custom_instructions, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (now, now, "test-identity-1", "test-block-1", None, None, 1),
        )
        await db.commit()
        cursor = await db.execute("SELECT last_insert_rowid()")
        row = await cursor.fetchone()
        letta_user_id = row[0]

        await db.execute(
            """
            INSERT INTO platform_profiles (
                letta_user_id, platform, platform_user_id, username, display_name,
                created_at, last_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (letta_user_id, "telegram", "tg-123", "testuser", "Test User", now, now),
        )
        await db.commit()
        cursor = await db.execute("SELECT last_insert_rowid()")
        row = await cursor.fetchone()
        platform_profile_id = row[0]

    message_id = await insert_message(
        letta_user_id=letta_user_id,
        platform_profile_id=platform_profile_id,
        role="user",
        message="Hello integration test",
    )
    await add_to_queue(letta_user_id, message_id)

    async with get_pool().connection() as db:
        async with db.execute(
            "SELECT id FROM queue WHERE message_id = ?", (message_id,)
        ) as cur:
            row = await cur.fetchone()
            queue_id = row[0]

    yield letta_user_id, message_id, queue_id


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_queue_echo_mode_processes_item_and_updates_db(
    seeded_queue_item,
):
    """Queue processor in echo mode should process one item and update message + queue."""
    letta_user_id, message_id, queue_id = seeded_queue_item
    mock_client = MagicMock()
    mock_client.agents.blocks.attach.return_value = None
    mock_client.agents.blocks.detach.return_value = None

    async def noop_processor(msg: str) -> str:
        return msg

    with patch("runtime.core.queue.get_letta_client", return_value=mock_client):
        processor = QueueProcessor(
            message_processor=noop_processor,
            message_mode="echo",
            plugin_manager=None,
        )
    # Run one iteration: dequeue and process (without starting the loop)
    item = await atomic_dequeue_item()
    assert item is not None
    assert item.message_id == message_id

    await processor._process_single_message(item)

    # In echo mode response is the formatted message; queue row should be completed
    async with get_pool().connection() as db:
        async with db.execute(
            "SELECT agent_response, processed FROM messages WHERE id = ?",
            (message_id,),
        ) as cur:
            row = await cur.fetchone()
            assert row is not None
            assert row[0] is not None
            assert len(row[0]) > 0
            assert row[1] == 1
        async with db.execute(
            "SELECT status FROM queue WHERE id = ?", (queue_id,)
        ) as cur:
            row = await cur.fetchone()
            assert row is not None
            assert row[0] == "completed"


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_queue_processor_start_stops_gracefully(seeded_queue_item):
    """QueueProcessor start() processes one item then we stop it."""
    letta_user_id, message_id, queue_id = seeded_queue_item
    mock_client = MagicMock()
    mock_client.agents.blocks.attach.return_value = None
    mock_client.agents.blocks.detach.return_value = None

    async def noop_processor(msg: str) -> str:
        return msg

    with patch("runtime.core.queue.get_letta_client", return_value=mock_client):
        processor = QueueProcessor(
            message_processor=noop_processor,
            message_mode="echo",
            plugin_manager=None,
        )
    task = asyncio.create_task(processor.start())
    # Allow one item to be processed
    await asyncio.sleep(2.0)
    await processor.stop()
    await asyncio.wait_for(task, timeout=5.0)

    async with get_pool().connection() as db:
        async with db.execute(
            "SELECT status FROM queue WHERE id = ?", (queue_id,)
        ) as cur:
            row = await cur.fetchone()
            assert row is not None
            assert row[0] == "completed"


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_queue_flow_with_message_containing_image_addendum(temp_db: str):
    """Queue/agent flow accepts message text containing [Image Attachment: url] (no schema change)."""
    now = datetime.utcnow().isoformat()
    async with get_pool().connection() as db:
        await db.execute(
            """
            INSERT INTO letta_users (
                created_at, last_active, letta_identity_id, letta_block_id,
                agent_preferences, custom_instructions, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (now, now, "test-identity-addendum", "test-block-addendum", None, None, 1),
        )
        await db.commit()
        cursor = await db.execute("SELECT last_insert_rowid()")
        row = await cursor.fetchone()
        letta_user_id = row[0]
        await db.execute(
            """
            INSERT INTO platform_profiles (
                letta_user_id, platform, platform_user_id, username, display_name,
                created_at, last_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                letta_user_id,
                "telegram",
                "tg-addendum",
                "addendumuser",
                "Addendum User",
                now,
                now,
            ),
        )
        await db.commit()
        cursor = await db.execute("SELECT last_insert_rowid()")
        row = await cursor.fetchone()
        platform_profile_id = row[0]

    message_with_addendum = (
        "What is in this image?\n"
        "[Image Attachment: https://tmpfiles.org/dl/12345/test.png]"
    )
    message_id = await insert_message(
        letta_user_id=letta_user_id,
        platform_profile_id=platform_profile_id,
        role="user",
        message=message_with_addendum,
    )
    await add_to_queue(letta_user_id, message_id)

    mock_client = MagicMock()
    mock_client.agents.blocks.attach.return_value = None
    mock_client.agents.blocks.detach.return_value = None

    async def echo_processor(msg: str) -> str:
        return msg

    with patch("runtime.core.queue.get_letta_client", return_value=mock_client), patch(
        "runtime.core.queue.get_env_var",
        side_effect=lambda n, **kw: "test-agent-id"
        if n == "AGENT_ID"
        else kw.get("default"),
    ):
        processor = QueueProcessor(
            message_processor=echo_processor,
            message_mode="echo",
            plugin_manager=None,
        )
    item = await atomic_dequeue_item()
    assert item is not None
    assert item.message_id == message_id
    await processor._process_single_message(item)

    async with get_pool().connection() as db:
        async with db.execute(
            "SELECT agent_response, processed FROM messages WHERE id = ?",
            (message_id,),
        ) as cur:
            row = await cur.fetchone()
            assert row is not None
            assert row[0] is not None
            assert "[Image Attachment:" in row[0]
            assert row[1] == 1
