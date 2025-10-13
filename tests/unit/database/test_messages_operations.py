"""Unit tests for database message operations."""


import pytest

from database.operations.messages import (
    get_message_text,
    insert_message,
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_insert_message(temp_db):
    """Test inserting a new message."""
    message_data = {
        "letta_user_id": 1,
        "platform_profile_id": 1,
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
    # First insert a message
    message_data = {
        "letta_user_id": 1,
        "platform_profile_id": 1,
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
