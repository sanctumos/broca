#!/usr/bin/env python3
"""Live Letta + queue smoke: DB init, create_identity + block, one live queue item.

Run on a host where Broca is installed (e.g. lettatest under /opt/broca-smoke) with
`.env` containing AGENT_ID, AGENT_ENDPOINT, AGENT_API_KEY.

  cd /opt/broca-smoke && .venv/bin/python tools/lettatest_live_queue_smoke.py

Optional: BROCA_SMOKE_ROOT (default: cwd), TEST_DB_PATH (default: /tmp/broca_smoke.db).
Exit 0 on success; 1 agent init failed; 2 dequeue empty; 3 no response; 4 queue not completed.
"""

from __future__ import annotations

import asyncio
import os
import sys


def _root() -> str:
    return os.environ.get("BROCA_SMOKE_ROOT", os.getcwd())


def main() -> int:
    root = _root()
    os.chdir(root)
    if root not in sys.path:
        sys.path.insert(0, root)

    os.environ.setdefault("TEST_DB_PATH", "/tmp/broca_smoke.db")

    from dotenv import load_dotenv

    load_dotenv(os.path.join(root, ".env"))

    return asyncio.run(_async_main())


async def _async_main() -> int:
    import database.pool as pool_mod
    from database.operations.messages import insert_message
    from database.operations.queue import add_to_queue, atomic_dequeue_item
    from database.operations.shared import initialize_database
    from database.operations.users import get_or_create_platform_profile
    from database.pool import get_pool, initialize_pool
    from runtime.core.agent import AgentClient
    from runtime.core.queue import QueueProcessor

    db_path = os.environ["TEST_DB_PATH"]
    if os.path.exists(db_path):
        os.unlink(db_path)

    pool_mod._pool = None
    pool = initialize_pool(2, 1)
    await pool.initialize()
    await initialize_database()

    uniq = f"smoke-{os.getpid()}"
    profile, lu = await get_or_create_platform_profile(
        "telegram",
        f"tg-{uniq}",
        "smokeuser",
        "Smoke User",
    )

    message_id = await insert_message(
        letta_user_id=lu.id,
        platform_profile_id=profile.id,
        role="user",
        message="Reply with one short sentence confirming you are online.",
    )
    await add_to_queue(lu.id, message_id)

    app = AgentClient()
    ok = await app.initialize()
    print("agent_init", ok)
    if not ok:
        return 1

    qp = QueueProcessor(
        app.process_message_async,
        message_mode="live",
        plugin_manager=None,
    )
    item = await atomic_dequeue_item()
    if item is None:
        print("dequeue_none")
        return 2

    await qp._process_single_message(item)

    async with get_pool().connection() as db:
        async with db.execute(
            "SELECT agent_response, processed FROM messages WHERE id = ?",
            (message_id,),
        ) as cur:
            row = await cur.fetchone()
        async with db.execute(
            "SELECT status FROM queue WHERE message_id = ?", (message_id,)
        ) as cur2:
            qrow = await cur2.fetchone()

    print("message_row", row)
    print("queue_status", qrow[0] if qrow else None)

    await get_pool().close()
    pool_mod._pool = None

    if not row or not row[0]:
        return 3
    if qrow and qrow[0] != "completed":
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
