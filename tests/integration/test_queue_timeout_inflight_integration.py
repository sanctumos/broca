"""
Integration tests: real SQLite (temp_db) + QueueProcessor timeout / requeue semantics.

Verifies persisted ``queue.status`` and ``queue.attempts`` match production expectations
when the agent layer is mocked and ``asyncio.wait_for`` / core-block paths are controlled.
"""

from __future__ import annotations

import inspect
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from common.exceptions import AgentTurnTimeoutInFlight
from database.operations.messages import insert_message
from database.operations.queue import (
    add_to_queue,
    atomic_dequeue_item,
    requeue_stale_processing_items,
)
from database.pool import get_pool
from runtime.core.queue import QueueProcessor


def _discard_unawaited_coroutine(awaitable: object) -> None:
    if inspect.isawaitable(awaitable):
        close = getattr(awaitable, "close", None)
        if callable(close):
            try:
                close()
            except (RuntimeError, GeneratorExit):
                pass


async def _queue_row(queue_id: int) -> tuple[str, int]:
    async with get_pool().connection() as db:
        async with db.execute(
            "SELECT status, attempts FROM queue WHERE id = ?", (queue_id,)
        ) as cur:
            row = await cur.fetchone()
            assert row is not None
            return row[0], int(row[1])


@pytest_asyncio.fixture
async def seeded_queue_item(temp_db: str):  # noqa: ARG001
    """One letta user, platform profile, message, and pending queue row."""
    now = datetime.utcnow().isoformat()
    async with get_pool().connection() as db:
        await db.execute(
            """
            INSERT INTO letta_users (
                created_at, last_active, letta_identity_id, letta_block_id,
                agent_preferences, custom_instructions, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (now, now, "integ-identity-1", "integ-block-1", None, None, 1),
        )
        await db.commit()
        cursor = await db.execute("SELECT last_insert_rowid()")
        row = await cursor.fetchone()
        letta_user_id = int(row[0])

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
                "tg-integ",
                "integuser",
                "Integ User",
                now,
                now,
            ),
        )
        await db.commit()
        cursor = await db.execute("SELECT last_insert_rowid()")
        row = await cursor.fetchone()
        platform_profile_id = int(row[0])

    message_id = await insert_message(
        letta_user_id=letta_user_id,
        platform_profile_id=platform_profile_id,
        role="user",
        message="integration timeout body",
    )
    await add_to_queue(letta_user_id, message_id)

    async with get_pool().connection() as db:
        async with db.execute(
            "SELECT id FROM queue WHERE message_id = ?", (message_id,)
        ) as cur:
            row = await cur.fetchone()
            queue_id = int(row[0])

    yield letta_user_id, message_id, queue_id


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_outer_wait_for_timeout_persists_failed_without_attempt_increment(
    seeded_queue_item,
) -> None:
    """SQLite: ``failed`` and same ``attempts`` after MESSAGE_PROCESS outer timeout."""

    _letta_user_id, message_id, queue_id = seeded_queue_item
    item = await atomic_dequeue_item()
    assert item is not None
    assert item.id == queue_id
    attempts_at_dequeue = item.attempts

    async def boom_wait_for(coro, timeout=None):  # noqa: ARG002
        _discard_unawaited_coroutine(coro)
        raise TimeoutError()

    async def never_called(
        _m: str, sender_id: str | None = None
    ) -> str:  # pragma: no cover
        raise AssertionError("processor must not run")

    mock_client = MagicMock()
    with patch.dict(
        "os.environ",
        {"AGENT_ID": "integration-agent-outer-timeout"},
        clear=False,
    ):
        with patch("runtime.core.queue.get_letta_client", return_value=mock_client):
            processor = QueueProcessor(never_called, message_mode="live")

    with patch("runtime.core.queue.asyncio.wait_for", side_effect=boom_wait_for):
        await processor._process_single_message(item)

    status, attempts = await _queue_row(queue_id)
    assert status == "failed"
    assert attempts == attempts_at_dequeue


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_agent_turn_timeout_inflight_persists_failed_without_attempt_increment(
    seeded_queue_item,
) -> None:
    """SQLite: ``AgentTurnTimeoutInFlight`` path leaves ``failed`` and does not bump attempts."""

    _letta_user_id, _message_id, queue_id = seeded_queue_item
    item = await atomic_dequeue_item()
    assert item is not None
    attempts_at_dequeue = item.attempts

    async def passthrough_wait_for(coro, timeout=None):  # noqa: ARG002
        return await coro

    async def core_raises(*_a, **_k):
        raise AgentTurnTimeoutInFlight("integration simulated in-flight timeout")

    mock_client = MagicMock()
    with patch.dict(
        "os.environ",
        {"AGENT_ID": "integration-agent-inflight"},
        clear=False,
    ):
        with patch("runtime.core.queue.get_letta_client", return_value=mock_client):
            processor = QueueProcessor(AsyncMock(), message_mode="live")
    processor._process_with_core_block = core_raises  # type: ignore[method-assign]

    with patch("runtime.core.queue.asyncio.wait_for", side_effect=passthrough_wait_for):
        await processor._process_single_message(item)

    status, attempts = await _queue_row(queue_id)
    assert status == "failed"
    assert attempts == attempts_at_dequeue


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_completed_none_response_requeues_pending_and_increments_attempts(
    seeded_queue_item,
) -> None:
    """SQLite: empty agent turn uses ``requeue_failed_item`` → ``pending``, ``attempts+1``."""

    _letta_user_id, _message_id, queue_id = seeded_queue_item
    item = await atomic_dequeue_item()
    assert item is not None
    attempts_before = item.attempts

    async def passthrough_wait_for(coro, timeout=None):  # noqa: ARG002
        return await coro

    async def core_none(*_a, **_k):
        return None, "failed"

    mock_client = MagicMock()
    with patch.dict(
        "os.environ",
        {"AGENT_ID": "integration-agent-none"},
        clear=False,
    ):
        with patch("runtime.core.queue.get_letta_client", return_value=mock_client):
            processor = QueueProcessor(AsyncMock(), message_mode="live")
    processor._process_with_core_block = core_none  # type: ignore[method-assign]

    with patch("runtime.core.queue.asyncio.wait_for", side_effect=passthrough_wait_for):
        with patch("runtime.core.queue.asyncio.sleep", new_callable=AsyncMock):
            await processor._process_single_message(item)

    status, attempts = await _queue_row(queue_id)
    assert status == "pending"
    assert attempts == attempts_before + 1


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_successful_live_turn_writes_message_and_completes_queue(
    seeded_queue_item,
) -> None:
    """SQLite: happy-path ``(text, completed)`` updates ``messages`` and ``queue``."""

    _letta_user_id, message_id, queue_id = seeded_queue_item
    item = await atomic_dequeue_item()
    assert item is not None

    async def passthrough_wait_for(coro, timeout=None):  # noqa: ARG002
        return await coro

    async def core_ok(*_a, **_k):
        return "assistant integration reply", "completed"

    mock_client = MagicMock()
    with patch.dict(
        "os.environ",
        {"AGENT_ID": "integration-agent-success"},
        clear=False,
    ):
        with patch("runtime.core.queue.get_letta_client", return_value=mock_client):
            processor = QueueProcessor(AsyncMock(), message_mode="live")
    processor._process_with_core_block = core_ok  # type: ignore[method-assign]

    with patch("runtime.core.queue.asyncio.wait_for", side_effect=passthrough_wait_for):
        with patch.object(
            processor, "_route_response", new_callable=AsyncMock, return_value=True
        ):
            await processor._process_single_message(item)

    status, _attempts = await _queue_row(queue_id)
    assert status == "completed"

    async with get_pool().connection() as db:
        async with db.execute(
            "SELECT agent_response, processed FROM messages WHERE id = ?",
            (message_id,),
        ) as cur:
            row = await cur.fetchone()
            assert row is not None
            assert row[0] == "assistant integration reply"
            assert row[1] == 1


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_requeue_stale_processing_items_updates_stale_row(
    seeded_queue_item,
) -> None:
    """Very old ``processing`` rows become ``pending`` again (crash recovery path)."""

    _letta_user_id, _message_id, queue_id = seeded_queue_item
    item = await atomic_dequeue_item()
    assert item is not None
    assert item.status == "processing"

    async with get_pool().connection() as db:
        await db.execute(
            """
            UPDATE queue
            SET timestamp = ?
            WHERE id = ?
            """,
            ("2000-01-01T00:00:00", queue_id),
        )
        await db.commit()

    n = await requeue_stale_processing_items(max_age_seconds=300)
    assert n >= 1

    status, _ = await _queue_row(queue_id)
    assert status == "pending"


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_outer_timeout_when_mark_failed_db_errors_row_stays_processing_no_requeue(
    seeded_queue_item,
) -> None:
    """If persisting ``failed`` raises, row stays ``processing`` and is not requeued."""

    _letta_user_id, _message_id, queue_id = seeded_queue_item
    item = await atomic_dequeue_item()
    assert item is not None

    async def boom_wait_for(coro, timeout=None):  # noqa: ARG002
        _discard_unawaited_coroutine(coro)
        raise TimeoutError()

    mock_client = MagicMock()
    with patch.dict(
        "os.environ",
        {"AGENT_ID": "integration-agent-db-boom"},
        clear=False,
    ):
        with patch("runtime.core.queue.get_letta_client", return_value=mock_client):
            processor = QueueProcessor(AsyncMock(), message_mode="live")

    boom = AsyncMock(side_effect=RuntimeError("database unavailable"))

    with patch("runtime.core.queue.asyncio.wait_for", side_effect=boom_wait_for):
        with patch("runtime.core.queue.update_queue_status", boom):
            await processor._process_single_message(item)

    status, attempts = await _queue_row(queue_id)
    assert status == "processing"
    assert attempts == 0


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_echo_mode_completes_with_real_db_write(seeded_queue_item) -> None:
    """Sanity: echo path still writes through with real pool (regression guard)."""

    _letta_user_id, message_id, queue_id = seeded_queue_item
    item = await atomic_dequeue_item()
    assert item is not None

    mock_client = MagicMock()
    mock_client.agents.blocks.attach.return_value = None
    mock_client.agents.blocks.detach.return_value = None

    async def echo_processor(msg: str, sender_id: str | None = None) -> str:
        return msg

    with patch.dict(
        "os.environ",
        {"AGENT_ID": "integration-echo-agent"},
        clear=False,
    ):
        with patch("runtime.core.queue.get_letta_client", return_value=mock_client):
            processor = QueueProcessor(
                echo_processor,
                message_mode="echo",
                plugin_manager=None,
            )

    await processor._process_single_message(item)

    status, _ = await _queue_row(queue_id)
    assert status == "completed"

    async with get_pool().connection() as db:
        async with db.execute(
            "SELECT processed FROM messages WHERE id = ?", (message_id,)
        ) as cur:
            row = await cur.fetchone()
            assert row is not None
            assert row[0] == 1
