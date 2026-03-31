"""Tests for headless outbound messaging."""

from unittest.mock import AsyncMock, patch

import pytest

from database.pool import get_pool
from database.operations.users import get_platform_profile_for_user_platform
from runtime.core.outbound import send_outbound_message


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_platform_profile_for_user_platform(temp_db):
    async with get_pool().connection() as db:
        await db.execute(
            "INSERT INTO letta_users (last_active, is_active) VALUES (datetime('now'), 1)"
        )
        await db.commit()
        cur = await db.execute("SELECT last_insert_rowid()")
        lu_id = (await cur.fetchone())[0]
        await db.execute(
            """
            INSERT INTO platform_profiles (
                letta_user_id, platform, platform_user_id, username, display_name
            ) VALUES (?, 'telegram', '999001', 'u', 'User')
            """,
            (lu_id,),
        )
        await db.commit()

    prof = await get_platform_profile_for_user_platform(lu_id, "telegram")
    assert prof is not None
    assert prof.platform_user_id == "999001"

    assert await get_platform_profile_for_user_platform(lu_id, "discord") is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_outbound_disabled(temp_db):
    with patch.dict("os.environ", {"ENABLE_OUTBOUND_TOOL": "false"}, clear=False):
        r = await send_outbound_message(
            letta_user_id=1, platform="telegram", message="hi", dry_run=False
        )
    assert r["success"] is False
    assert r["error"] == "outbound_disabled"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_outbound_dry_run_without_enable(temp_db):
    async with get_pool().connection() as db:
        await db.execute(
            "INSERT INTO letta_users (last_active, is_active) VALUES (datetime('now'), 1)"
        )
        await db.commit()
        cur = await db.execute("SELECT last_insert_rowid()")
        lu_id = (await cur.fetchone())[0]
        await db.execute(
            """
            INSERT INTO platform_profiles (
                letta_user_id, platform, platform_user_id, username, display_name
            ) VALUES (?, 'telegram', '999010', 'u0', 'U0')
            """,
            (lu_id,),
        )
        await db.commit()

    with patch.dict("os.environ", {"ENABLE_OUTBOUND_TOOL": "false"}, clear=False):
        r = await send_outbound_message(
            letta_user_id=lu_id,
            platform="telegram",
            message="hello",
            dry_run=True,
        )
    assert r["success"] is True
    assert r["delivery_status"] == "dry_run"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_outbound_dry_run_success(temp_db):
    async with get_pool().connection() as db:
        await db.execute(
            "INSERT INTO letta_users (last_active, is_active) VALUES (datetime('now'), 1)"
        )
        await db.commit()
        cur = await db.execute("SELECT last_insert_rowid()")
        lu_id = (await cur.fetchone())[0]
        await db.execute(
            """
            INSERT INTO platform_profiles (
                letta_user_id, platform, platform_user_id, username, display_name
            ) VALUES (?, 'telegram', '999002', 'u2', 'User2')
            """,
            (lu_id,),
        )
        await db.commit()

    with patch.dict("os.environ", {"ENABLE_OUTBOUND_TOOL": "true"}, clear=False):
        r = await send_outbound_message(
            letta_user_id=lu_id,
            platform="telegram",
            message="hello",
            dry_run=True,
        )
    assert r["success"] is True
    assert r["delivery_status"] == "dry_run"
    assert r["platform_user_id"] == "999002"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_send_outbound_telegram_mock_send(temp_db):
    async with get_pool().connection() as db:
        await db.execute(
            "INSERT INTO letta_users (last_active, is_active) VALUES (datetime('now'), 1)"
        )
        await db.commit()
        cur = await db.execute("SELECT last_insert_rowid()")
        lu_id = (await cur.fetchone())[0]
        await db.execute(
            """
            INSERT INTO platform_profiles (
                letta_user_id, platform, platform_user_id, username, display_name
            ) VALUES (?, 'telegram', '999003', 'u3', 'User3')
            """,
            (lu_id,),
        )
        await db.commit()

    with patch.dict("os.environ", {"ENABLE_OUTBOUND_TOOL": "true"}, clear=False):
        with patch(
            "runtime.core.outbound.deliver_telegram_markdown",
            new_callable=AsyncMock,
            return_value={"telegram_message_id": 42, "chat_id": 999003},
        ):
            r = await send_outbound_message(
                letta_user_id=lu_id,
                platform="telegram",
                message="hello",
                dry_run=False,
            )

    assert r["success"] is True
    assert r["delivery_status"] == "sent"
    assert r["message_id"] is not None
