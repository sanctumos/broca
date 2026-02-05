"""Unit tests for database message operations."""


from datetime import datetime

import pytest

from database.operations.messages import (
    get_message_text,
    insert_message,
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
async def test_insert_message(temp_db):
    """Test inserting a new message."""
    letta_user_id, platform_profile_id = await _seed_user_and_profile()
    message_data = {
        "letta_user_id": letta_user_id,
        "platform_profile_id": platform_profile_id,
        "role": "user",
        "message": "Hello world",
    }

    message_id = await insert_message(**message_data)
    assert message_id is not None
    assert isinstance(message_id, int)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_message_text(temp_db):
    """Test getting message text by ID."""
    letta_user_id, platform_profile_id = await _seed_user_and_profile()
    # First insert a message
    message_data = {
        "letta_user_id": letta_user_id,
        "platform_profile_id": platform_profile_id,
        "role": "user",
        "message": "Test message",
    }

    message_id = await insert_message(**message_data)
    text = await get_message_text(message_id)
    assert text == ("user", "Test message")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_message_with_response(temp_db):
    """Test updating message with response."""
    # This test will need to be implemented based on the actual function
    pass


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_message_history(temp_db):
    """Test getting message history."""
    # This test will need to be implemented based on the actual function
    pass


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_messages(temp_db):
    """Test getting messages."""
    # This test will need to be implemented based on the actual function
    pass
