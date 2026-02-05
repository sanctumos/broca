"""
E2E tests: full message flow through Application and queue with real DB.

Starts Application (mocked externals), seeds queue, waits for processing, then shutdown.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import aiosqlite
import pytest

from database.operations.messages import insert_message
from database.operations.queue import add_to_queue
from database.pool import get_pool


@pytest.mark.e2e
@pytest.mark.database
@pytest.mark.asyncio
async def test_full_message_flow_through_app(temp_db: str):
    """Application runs, one message is queued and processed by the queue loop."""
    project_root = Path(__file__).resolve().parent.parent.parent
    fixtures_plugins_dir = str(project_root / "tests" / "fixtures")

    now = datetime.utcnow().isoformat()
    async with get_pool().connection() as db:
        await db.execute(
            """
            INSERT INTO letta_users (
                created_at, last_active, letta_identity_id, letta_block_id,
                agent_preferences, custom_instructions, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (now, now, "e2e-identity", "e2e-block", None, None, 1),
        )
        await db.commit()
        cursor = await db.execute("SELECT last_insert_rowid()")
        letta_user_id = (await cursor.fetchone())[0]
        await db.execute(
            """
            INSERT INTO platform_profiles (
                letta_user_id, platform, platform_user_id, username, display_name,
                created_at, last_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (letta_user_id, "telegram", "e2e-tg", "e2euser", "E2E User", now, now),
        )
        await db.commit()
        cursor = await db.execute("SELECT last_insert_rowid()")
        platform_profile_id = (await cursor.fetchone())[0]

    message_id = await insert_message(
        letta_user_id=letta_user_id,
        platform_profile_id=platform_profile_id,
        role="user",
        message="E2E hello",
    )
    await add_to_queue(letta_user_id, message_id)

    mock_client = MagicMock()
    mock_client.agents.retrieve.return_value = MagicMock(id="e2e-agent", name="E2E")
    mock_client.agents.blocks.attach.return_value = None
    mock_client.agents.blocks.detach.return_value = None

    with (
        patch("main.PIDManager") as mock_pid_class,
        patch("main.create_default_settings"),
        patch("runtime.core.letta_client.get_letta_client", return_value=mock_client),
        patch("runtime.core.queue.get_letta_client", return_value=mock_client),
        patch("runtime.core.agent.get_letta_client", return_value=mock_client),
        patch("main.validate_environment_variables"),
    ):
        mock_pid_class.return_value.create_pid_file.return_value = None
        mock_pid_class.return_value.cleanup.return_value = None

        from main import Application

        app = Application()
        app.agent.initialize = AsyncMock(return_value=True)

        real_discover = app.plugin_manager.discover_plugins

        async def discover_and_await(**kwargs):
            await real_discover(
                plugins_dir=fixtures_plugins_dir,
                config=kwargs.get("config") or {},
            )

        app.plugin_manager.discover_plugins = AsyncMock(side_effect=discover_and_await)

        start_task = asyncio.create_task(app.start())
        await asyncio.sleep(3.5)
        app._shutdown_event.set()
        await asyncio.wait_for(start_task, timeout=12.0)

    # Pool is closed after app.stop(); use direct connection to temp DB for asserts
    async with aiosqlite.connect(temp_db) as db:
        async with db.execute(
            "SELECT agent_response, processed FROM messages WHERE id = ?",
            (message_id,),
        ) as cur:
            row = await cur.fetchone()
            assert row is not None
            assert row[0] is not None
            assert row[1] == 1
        async with db.execute(
            "SELECT status FROM queue WHERE message_id = ?", (message_id,)
        ) as cur:
            row = await cur.fetchone()
            assert row is not None
            assert row[0] == "completed"
