"""Comprehensive unit tests for database.operations.users to achieve 100% coverage."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from database.operations.users import (
    get_all_users,
    get_letta_user_block_id,
    get_or_create_letta_user,
    get_or_create_platform_profile,
    get_platform_profile,
    get_platform_profile_id,
    get_user_details,
    update_letta_user,
    upsert_user,
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_or_create_letta_user_new_user(temp_db, mock_letta_client):
    """Test creating a new Letta user."""
    mock_identity = MagicMock()
    mock_identity.id = "identity-123"
    mock_letta_client.identities.create.return_value = mock_identity
    
    mock_block = MagicMock()
    mock_block.id = "block-123"
    mock_letta_client.blocks.create.return_value = mock_block
    
    user = await get_or_create_letta_user(
        username="testuser",
        display_name="Test User",
        platform_user_id="12345"
    )
    
    assert user is not None
    assert user.letta_identity_id == "identity-123"
    assert user.letta_block_id == "block-123"
    assert user.is_active is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_or_create_letta_user_minimal_data(temp_db, mock_letta_client):
    """Test creating Letta user with minimal data."""
    mock_identity = MagicMock()
    mock_identity.id = "identity-123"
    mock_letta_client.identities.create.return_value = mock_identity
    
    mock_block = MagicMock()
    mock_block.id = "block-123"
    mock_letta_client.blocks.create.return_value = mock_block
    
    user = await get_or_create_letta_user()
    
    assert user is not None
    assert user.letta_identity_id == "identity-123"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_or_create_platform_profile_new_profile(temp_db, mock_letta_client):
    """Test creating a new platform profile."""
    mock_identity = MagicMock()
    mock_identity.id = "identity-123"
    mock_letta_client.identities.create.return_value = mock_identity
    
    mock_block = MagicMock()
    mock_block.id = "block-123"
    mock_letta_client.blocks.create.return_value = mock_block
    
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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_or_create_platform_profile_existing_profile(temp_db, mock_letta_client):
    """Test getting an existing platform profile."""
    import aiosqlite
    from database.operations.shared import get_db_path
    
    # First create a profile
    mock_identity = MagicMock()
    mock_identity.id = "identity-123"
    mock_letta_client.identities.create.return_value = mock_identity
    
    mock_block = MagicMock()
    mock_block.id = "block-123"
    mock_letta_client.blocks.create.return_value = mock_block
    
    # Create initial profile
    await get_or_create_platform_profile(
        platform="telegram",
        platform_user_id="12345",
        username="testuser",
        display_name="Test User"
    )
    
    # Get existing profile
    profile, user = await get_or_create_platform_profile(
        platform="telegram",
        platform_user_id="12345",
        username="updateduser",
        display_name="Updated User"
    )
    
    assert profile is not None
    assert profile.username == "updateduser"
    assert profile.display_name == "Updated User"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_or_create_platform_profile_with_metadata(temp_db, mock_letta_client):
    """Test creating platform profile with metadata."""
    mock_identity = MagicMock()
    mock_identity.id = "identity-123"
    mock_letta_client.identities.create.return_value = mock_identity
    
    mock_block = MagicMock()
    mock_block.id = "block-123"
    mock_letta_client.blocks.create.return_value = mock_block
    
    metadata = {"key": "value", "number": 42}
    
    profile, user = await get_or_create_platform_profile(
        platform="telegram",
        platform_user_id="12345",
        username="testuser",
        display_name="Test User",
        metadata=metadata
    )
    
    assert profile is not None
    assert profile.metadata is not None
    assert json.loads(profile.metadata) == metadata


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_letta_user_agent_preferences(temp_db, mock_letta_client):
    """Test updating user agent preferences."""
    import aiosqlite
    from database.operations.shared import get_db_path
    from database.models import LettaUser
    
    # First create a user
    mock_identity = MagicMock()
    mock_identity.id = "identity-123"
    mock_letta_client.identities.create.return_value = mock_identity
    
    mock_block = MagicMock()
    mock_block.id = "block-123"
    mock_letta_client.blocks.create.return_value = mock_block
    
    user = await get_or_create_letta_user(username="testuser")
    
    # Update preferences
    preferences = {"temperature": 0.7, "max_tokens": 1000}
    updated_user = await update_letta_user(
        user.id,
        agent_preferences=preferences
    )
    
    assert updated_user is not None
    assert updated_user.agent_preferences is not None
    assert json.loads(updated_user.agent_preferences) == preferences


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_letta_user_custom_instructions(temp_db, mock_letta_client):
    """Test updating user custom instructions."""
    # First create a user
    mock_identity = MagicMock()
    mock_identity.id = "identity-123"
    mock_letta_client.identities.create.return_value = mock_identity
    
    mock_block = MagicMock()
    mock_block.id = "block-123"
    mock_letta_client.blocks.create.return_value = mock_block
    
    user = await get_or_create_letta_user(username="testuser")
    
    # Update instructions
    instructions = "Be helpful and concise"
    updated_user = await update_letta_user(
        user.id,
        custom_instructions=instructions
    )
    
    assert updated_user is not None
    assert updated_user.custom_instructions == instructions


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_letta_user_both_fields(temp_db, mock_letta_client):
    """Test updating both preferences and instructions."""
    # First create a user
    mock_identity = MagicMock()
    mock_identity.id = "identity-123"
    mock_letta_client.identities.create.return_value = mock_identity
    
    mock_block = MagicMock()
    mock_block.id = "block-123"
    mock_letta_client.blocks.create.return_value = mock_block
    
    user = await get_or_create_letta_user(username="testuser")
    
    # Update both
    preferences = {"temperature": 0.8}
    instructions = "New instructions"
    updated_user = await update_letta_user(
        user.id,
        agent_preferences=preferences,
        custom_instructions=instructions
    )
    
    assert updated_user is not None
    assert updated_user.custom_instructions == instructions


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_letta_user_no_updates(temp_db):
    """Test update_letta_user with no updates raises error."""
    with pytest.raises(ValueError, match="No updates specified"):
        await update_letta_user(1)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_letta_user_not_found(temp_db):
    """Test update_letta_user when user doesn't exist."""
    with pytest.raises(ValueError, match="not found"):
        await update_letta_user(99999, agent_preferences={"key": "value"})


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_user_details_found(temp_db, mock_letta_client):
    """Test getting user details when user exists."""
    import aiosqlite
    from database.operations.shared import get_db_path
    
    # Create a user and profile
    mock_identity = MagicMock()
    mock_identity.id = "identity-123"
    mock_letta_client.identities.create.return_value = mock_identity
    
    mock_block = MagicMock()
    mock_block.id = "block-123"
    mock_letta_client.blocks.create.return_value = mock_block
    
    profile, user = await get_or_create_platform_profile(
        platform="telegram",
        platform_user_id="12345",
        username="testuser",
        display_name="Test User"
    )
    
    details = await get_user_details(user.id)
    
    assert details is not None
    assert details[0] == "Test User"  # display_name
    assert details[1] == "testuser"   # username


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_user_details_not_found(temp_db):
    """Test getting user details when user doesn't exist."""
    details = await get_user_details(99999)
    
    assert details is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_all_users(temp_db, mock_letta_client):
    """Test getting all users."""
    # Create multiple users
    mock_identity1 = MagicMock()
    mock_identity1.id = "identity-1"
    mock_identity2 = MagicMock()
    mock_identity2.id = "identity-2"
    mock_letta_client.identities.create.side_effect = [mock_identity1, mock_identity2]
    
    mock_block1 = MagicMock()
    mock_block1.id = "block-1"
    mock_block2 = MagicMock()
    mock_block2.id = "block-2"
    mock_letta_client.blocks.create.side_effect = [mock_block1, mock_block2]
    
    await get_or_create_platform_profile(
        platform="telegram",
        platform_user_id="12345",
        username="user1",
        display_name="User 1"
    )
    
    await get_or_create_platform_profile(
        platform="telegram",
        platform_user_id="67890",
        username="user2",
        display_name="User 2"
    )
    
    users = await get_all_users()
    
    assert len(users) >= 2
    assert any(u["username"] == "user1" for u in users)
    assert any(u["username"] == "user2" for u in users)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_platform_profile_id_found(temp_db, mock_letta_client):
    """Test getting platform profile ID when profile exists."""
    # Create a profile
    mock_identity = MagicMock()
    mock_identity.id = "identity-123"
    mock_letta_client.identities.create.return_value = mock_identity
    
    mock_block = MagicMock()
    mock_block.id = "block-123"
    mock_letta_client.blocks.create.return_value = mock_block
    
    profile, user = await get_or_create_platform_profile(
        platform="telegram",
        platform_user_id="12345",
        username="testuser",
        display_name="Test User"
    )
    
    result = await get_platform_profile_id(user.id)
    
    assert result is not None
    assert result[0] == profile.id  # profile_id
    assert result[1] == "12345"     # platform_user_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_platform_profile_id_not_found(temp_db):
    """Test getting platform profile ID when profile doesn't exist."""
    result = await get_platform_profile_id(99999)
    
    assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_platform_profile_found(temp_db, mock_letta_client):
    """Test getting platform profile by ID when profile exists."""
    # Create a profile
    mock_identity = MagicMock()
    mock_identity.id = "identity-123"
    mock_letta_client.identities.create.return_value = mock_identity
    
    mock_block = MagicMock()
    mock_block.id = "block-123"
    mock_letta_client.blocks.create.return_value = mock_block
    
    profile, user = await get_or_create_platform_profile(
        platform="telegram",
        platform_user_id="12345",
        username="testuser",
        display_name="Test User"
    )
    
    retrieved_profile = await get_platform_profile(profile.id)
    
    assert retrieved_profile is not None
    assert retrieved_profile.id == profile.id
    assert retrieved_profile.platform == "telegram"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_platform_profile_not_found(temp_db):
    """Test getting platform profile when profile doesn't exist."""
    profile = await get_platform_profile(99999)
    
    assert profile is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_letta_user_block_id_found(temp_db, mock_letta_client):
    """Test getting Letta user block ID when user exists."""
    # Create a user
    mock_identity = MagicMock()
    mock_identity.id = "identity-123"
    mock_letta_client.identities.create.return_value = mock_identity
    
    mock_block = MagicMock()
    mock_block.id = "block-123"
    mock_letta_client.blocks.create.return_value = mock_block
    
    user = await get_or_create_letta_user(username="testuser")
    
    block_id = await get_letta_user_block_id(user.id)
    
    assert block_id == "block-123"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_letta_user_block_id_not_found(temp_db):
    """Test getting Letta user block ID when user doesn't exist."""
    block_id = await get_letta_user_block_id(99999)
    
    assert block_id is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_upsert_user_new_user(temp_db, mock_letta_client):
    """Test upsert_user creates new user."""
    import aiosqlite
    from database.operations.shared import get_db_path
    
    # Create a Letta user first
    mock_identity = MagicMock()
    mock_identity.id = "identity-123"
    mock_letta_client.identities.create.return_value = mock_identity
    
    mock_block = MagicMock()
    mock_block.id = "block-123"
    mock_letta_client.blocks.create.return_value = mock_block
    
    user = await get_or_create_letta_user(username="testuser")
    
    # Upsert platform profile
    await upsert_user(user.id, "testuser", "Test User")
    
    # Verify profile was created
    profile = await get_platform_profile_id(user.id)
    assert profile is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_upsert_user_existing_user(temp_db, mock_letta_client):
    """Test upsert_user updates existing user."""
    # Create a user and profile
    mock_identity = MagicMock()
    mock_identity.id = "identity-123"
    mock_letta_client.identities.create.return_value = mock_identity
    
    mock_block = MagicMock()
    mock_block.id = "block-123"
    mock_letta_client.blocks.create.return_value = mock_block
    
    profile, user = await get_or_create_platform_profile(
        platform="telegram",
        platform_user_id="12345",
        username="olduser",
        display_name="Old User"
    )
    
    # Upsert with new data
    await upsert_user(user.id, "newuser", "New User")
    
    # Verify profile was updated
    updated_profile = await get_platform_profile(profile.id)
    assert updated_profile is not None
    assert updated_profile.username == "newuser"
    assert updated_profile.display_name == "New User"
