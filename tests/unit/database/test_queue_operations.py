"""Unit tests for database queue operations."""


from datetime import datetime

import pytest

from database.operations.messages import insert_message
from database.operations.queue import (
    add_to_queue,
    get_pending_queue_item,
)
from database.pool import get_pool


async def _seed_user_and_profile() -> tuple[int, int]:
    now = datetime.utcnow().isoformat()
    async with get_pool().connection() as db:
        cursor = await db.execute(
            """
            INSERT INTO letta_users (
                created_at,
                last_active,
                letta_identity_id,
                letta_block_id,
                agent_preferences,
                custom_instructions,
                is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (now, now, None, None, None, None, True),
        )
        letta_user_id = cursor.lastrowid
        cursor = await db.execute(
            """
            INSERT INTO platform_profiles (
                letta_user_id,
                platform,
                platform_user_id,
                username,
                display_name,
                metadata,
                created_at,
                last_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                letta_user_id,
                "telegram",
                "123456789",
                "testuser",
                "Test User",
                None,
                now,
                now,
            ),
        )
        platform_profile_id = cursor.lastrowid
        await db.commit()
    return letta_user_id, platform_profile_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_to_queue(temp_db):
    """Test adding item to queue."""
    letta_user_id, platform_profile_id = await _seed_user_and_profile()
    message_id = await insert_message(
        letta_user_id=letta_user_id,
        platform_profile_id=platform_profile_id,
        role="user",
        message="Hello world",
    )
    queue_data = {"letta_user_id": letta_user_id, "message_id": message_id}

    await add_to_queue(**queue_data)
    # Function returns None, so we just verify it doesn't raise an exception


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_pending_queue_item(temp_db):
    """Test getting pending queue item."""
    # First add an item to queue
    letta_user_id, platform_profile_id = await _seed_user_and_profile()
    message_id = await insert_message(
        letta_user_id=letta_user_id,
        platform_profile_id=platform_profile_id,
        role="user",
        message="Test message",
    )
    queue_data = {"letta_user_id": letta_user_id, "message_id": message_id}

    await add_to_queue(**queue_data)
    item = await get_pending_queue_item()
    assert item is not None
    assert item.message_id == message_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_queue_status(temp_db):
    """Test updating queue item status."""
    # This test will need to be implemented based on the actual function
    pass


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_all_queue_items(temp_db):
    """Test getting all queue items."""
    # This test will need to be implemented based on the actual function
    pass


@pytest.mark.unit
@pytest.mark.asyncio
async def test_flush_all_queue_items(temp_db):
    """Test flushing all queue items."""
    # This test will need to be implemented based on the actual function
    pass


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_queue_item(temp_db):
    """Test deleting queue item."""
    # This test will need to be implemented based on the actual function
    pass


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_queue_statistics(temp_db):
    """Test getting queue statistics."""
    # This test will need to be implemented based on the actual function
    pass
