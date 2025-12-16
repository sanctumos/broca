"""Integration tests for database operations."""

import pytest

from database.operations.messages import insert_message, get_message_text
from database.operations.queue import add_to_queue, atomic_dequeue_item, update_queue_status
from database.operations.users import (
    get_or_create_platform_profile,
    get_user_details,
    update_letta_user,
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_creation_and_retrieval(temp_db, mock_letta_client):
    """Test creating a user and retrieving their details."""
    # Create a platform profile (which creates a Letta user)
    profile, user = await get_or_create_platform_profile(
        platform="telegram",
        platform_user_id="12345",
        username="testuser",
        display_name="Test User"
    )
    
    assert profile is not None
    assert user is not None
    assert profile.platform == "telegram"
    assert profile.platform_user_id == "12345"
    
    # Retrieve user details
    details = await get_user_details(user.id)
    assert details is not None
    assert details[0] == "Test User"  # display_name
    assert details[1] == "testuser"   # username


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_update_integration(temp_db, mock_letta_client):
    """Test updating user preferences and retrieving them."""
    # Create a user
    profile, user = await get_or_create_platform_profile(
        platform="telegram",
        platform_user_id="12345",
        username="testuser",
        display_name="Test User"
    )
    
    # Update user preferences
    preferences = {"temperature": 0.7, "max_tokens": 1000}
    updated_user = await update_letta_user(
        user.id,
        agent_preferences=preferences
    )
    
    assert updated_user is not None
    assert updated_user.agent_preferences is not None
    
    # Verify update persisted
    import json
    assert json.loads(updated_user.agent_preferences) == preferences


@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_creation_and_retrieval(temp_db, mock_letta_client):
    """Test creating a message and retrieving it."""
    # Create a user first
    profile, user = await get_or_create_platform_profile(
        platform="telegram",
        platform_user_id="12345",
        username="testuser",
        display_name="Test User"
    )
    
    # Create a message
    message_id = await insert_message(
        letta_user_id=user.id,
        platform_profile_id=profile.id,
        role="user",
        message="Hello, this is a test message"
    )
    
    assert message_id is not None
    
    # Retrieve the message
    message_data = await get_message_text(message_id)
    assert message_data is not None
    role, message_text = message_data
    assert role == "user"
    assert message_text == "Hello, this is a test message"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_queue_operations_integration(temp_db, mock_letta_client):
    """Test queue operations with real database."""
    # Create a user and message
    profile, user = await get_or_create_platform_profile(
        platform="telegram",
        platform_user_id="12345",
        username="testuser",
        display_name="Test User"
    )
    
    message_id = await insert_message(
        letta_user_id=user.id,
        platform_profile_id=profile.id,
        role="user",
        message="Test queue message"
    )
    
    # Enqueue the message
    await add_to_queue(
        letta_user_id=user.id,
        message_id=message_id
    )
    
    # Dequeue the message
    queue_item = await atomic_dequeue_item()
    assert queue_item is not None
    assert queue_item.message_id == message_id
    assert queue_item.message_id == message_id
    assert queue_item.letta_user_id == user.id
    
    # Update queue status
    await update_queue_status(queue_item.id, "completed")
    
    # Verify it's not dequeued again
    queue_item2 = await atomic_dequeue_item()
    assert queue_item2 is None or queue_item2.id != queue_item.id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multiple_users_and_messages(temp_db, mock_letta_client):
    """Test multiple users and messages in the same database."""
    # Create multiple users
    profile1, user1 = await get_or_create_platform_profile(
        platform="telegram",
        platform_user_id="11111",
        username="user1",
        display_name="User 1"
    )
    
    profile2, user2 = await get_or_create_platform_profile(
        platform="telegram",
        platform_user_id="22222",
        username="user2",
        display_name="User 2"
    )
    
    # Create messages for each user
    message1_id = await create_message(
        letta_user_id=user1.id,
        platform_profile_id=profile1.id,
        role="user",
        message="Message from user 1"
    )
    
    message2_id = await create_message(
        letta_user_id=user2.id,
        platform_profile_id=profile2.id,
        role="user",
        message="Message from user 2"
    )
    
    # Enqueue both messages
    await add_to_queue(user1.id, message1_id)
    await add_to_queue(user2.id, message2_id)
    
    # Dequeue and verify
    item1 = await atomic_dequeue_item()
    assert item1 is not None
    assert item1.message_id == message1_id or item1.message_id == message2_id
    
    item2 = await atomic_dequeue_item()
    assert item2 is not None
    assert item2.message_id != item1.message_id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_profile_update_integration(temp_db, mock_letta_client):
    """Test updating user profile and verifying changes."""
    # Create initial profile
    profile1, user = await get_or_create_platform_profile(
        platform="telegram",
        platform_user_id="12345",
        username="olduser",
        display_name="Old User"
    )
    
    # Update profile (get_or_create with same platform_user_id updates)
    profile2, user2 = await get_or_create_platform_profile(
        platform="telegram",
        platform_user_id="12345",
        username="newuser",
        display_name="New User"
    )
    
    # Should be the same user
    assert user.id == user2.id
    assert profile1.id == profile2.id
    
    # But profile should be updated
    assert profile2.username == "newuser"
    assert profile2.display_name == "New User"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cross_component_integration(temp_db, mock_letta_client):
    """Test integration across users, messages, and queue."""
    # Create user
    profile, user = await get_or_create_platform_profile(
        platform="telegram",
        platform_user_id="12345",
        username="testuser",
        display_name="Test User"
    )
    
    # Create message
    message_id = await insert_message(
        letta_user_id=user.id,
        platform_profile_id=profile.id,
        role="user",
        message="Integration test message"
    )
    
    # Enqueue
    await add_to_queue(user.id, message_id)
    
    # Dequeue
    queue_item = await atomic_dequeue_item()
    assert queue_item is not None
    
    # Get message
    message_data = await get_message_text(queue_item.message_id)
    assert message_data is not None
    
    # Get user details
    user_details = await get_user_details(queue_item.letta_user_id)
    assert user_details is not None
    
    # Update queue status
    await update_queue_status(queue_id, "completed")
    
    # All operations should work together seamlessly
    assert message_data[1] == "Integration test message"
    assert user_details[0] == "Test User"
