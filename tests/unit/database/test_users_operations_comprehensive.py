"""Comprehensive tests for database user operations."""

import asyncio
import json
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from database.models import LettaUser, PlatformProfile
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


class TestUserOperationsComprehensive:
    """Comprehensive tests for user operations."""

    @pytest.mark.asyncio
    async def test_get_or_create_letta_user_success(self):
        """Test successful creation of Letta user."""
        with patch("database.operations.users.get_letta_client") as mock_get_client:
            mock_client = MagicMock()
            mock_identity = MagicMock()
            mock_identity.id = "identity_123"
            mock_block = MagicMock()
            mock_block.id = "block_456"
            mock_client.identities.create.return_value = mock_identity
            mock_client.blocks.create.return_value = mock_block
            mock_get_client.return_value = mock_client

            with patch("aiosqlite.connect") as mock_connect:
                mock_db = AsyncMock()
                mock_cursor = AsyncMock()
                mock_cursor.lastrowid = 1
                mock_db.execute.return_value = mock_cursor
                mock_connect.return_value.__aenter__.return_value = mock_db

                result = await get_or_create_letta_user(
                    username="testuser",
                    display_name="Test User",
                    platform_user_id="123",
                )

                assert isinstance(result, LettaUser)
                assert result.id == 1
                assert result.letta_identity_id == "identity_123"
                assert result.letta_block_id == "block_456"

    @pytest.mark.asyncio
    async def test_get_or_create_letta_user_minimal_data(self):
        """Test Letta user creation with minimal data."""
        with patch("database.operations.users.get_letta_client") as mock_get_client:
            mock_client = MagicMock()
            mock_identity = MagicMock()
            mock_identity.id = "identity_123"
            mock_block = MagicMock()
            mock_block.id = "block_456"
            mock_client.identities.create.return_value = mock_identity
            mock_client.blocks.create.return_value = mock_block
            mock_get_client.return_value = mock_client

            with patch("aiosqlite.connect") as mock_connect:
                mock_db = AsyncMock()
                mock_cursor = AsyncMock()
                mock_cursor.lastrowid = 1
                mock_db.execute.return_value = mock_cursor
                mock_connect.return_value.__aenter__.return_value = mock_db

                result = await get_or_create_letta_user()

                assert isinstance(result, LettaUser)
                assert result.id == 1

    @pytest.mark.asyncio
    async def test_get_or_create_letta_user_exception(self):
        """Test Letta user creation with exception."""
        with patch("database.operations.users.get_letta_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.identities.create.side_effect = Exception("Letta API error")
            mock_get_client.return_value = mock_client

            with pytest.raises(Exception, match="Letta API error"):
                await get_or_create_letta_user(
                    username="testuser",
                    display_name="Test User",
                    platform_user_id="123",
                )

    @pytest.mark.asyncio
    async def test_get_or_create_platform_profile_existing(self):
        """Test getting existing platform profile."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = (
                1,  # id
                123,  # letta_user_id
                "telegram",  # platform
                "456",  # platform_user_id
                "old_username",  # username
                "Old Display",  # display_name
                None,  # metadata
                "2023-01-01T12:00:00",  # created_at
            )
            mock_db.execute.return_value.__aenter__.return_value = mock_cursor
            mock_connect.return_value.__aenter__.return_value = mock_db

            # Mock user fetch
            mock_user_cursor = AsyncMock()
            mock_user_cursor.fetchone.return_value = (
                123,  # id
                "2023-01-01T12:00:00",  # created_at
                "2023-01-01T12:00:00",  # last_active
                "identity_123",  # letta_identity_id
                None,  # agent_preferences
                None,  # custom_instructions
                True,  # is_active
            )
            mock_db.execute.return_value.__aenter__.return_value = mock_user_cursor

            profile, user = await get_or_create_platform_profile(
                platform="telegram",
                platform_user_id="456",
                username="new_username",
                display_name="New Display",
                metadata={"key": "value"},
            )

            assert isinstance(profile, PlatformProfile)
            assert isinstance(user, LettaUser)
            assert profile.username == "new_username"
            assert profile.display_name == "New Display"

    @pytest.mark.asyncio
    async def test_get_or_create_platform_profile_new(self):
        """Test creating new platform profile."""
        with patch(
            "database.operations.users.get_or_create_letta_user"
        ) as mock_create_user:
            mock_user = LettaUser(
                id=123,
                created_at="2023-01-01T12:00:00",
                last_active="2023-01-01T12:00:00",
                letta_identity_id="identity_123",
                letta_block_id="block_456",
                agent_preferences=None,
                custom_instructions=None,
                is_active=True,
            )
            mock_create_user.return_value = mock_user

            with patch("aiosqlite.connect") as mock_connect:
                mock_db = AsyncMock()
                mock_cursor = AsyncMock()
                mock_cursor.lastrowid = 1
                mock_db.execute.return_value = mock_cursor
                mock_connect.return_value.__aenter__.return_value = mock_db

                # Mock profile fetch returning None (new profile)
                mock_profile_cursor = AsyncMock()
                mock_profile_cursor.fetchone.return_value = None
                mock_db.execute.return_value.__aenter__.return_value = (
                    mock_profile_cursor
                )

                profile, user = await get_or_create_platform_profile(
                    platform="telegram",
                    platform_user_id="456",
                    username="testuser",
                    display_name="Test User",
                    metadata={"key": "value"},
                )

                assert isinstance(profile, PlatformProfile)
                assert isinstance(user, LettaUser)
                assert profile.platform == "telegram"
                assert profile.platform_user_id == "456"

    @pytest.mark.asyncio
    async def test_get_or_create_platform_profile_exception(self):
        """Test platform profile creation with exception."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = AsyncMock()
            mock_db.execute.side_effect = Exception("Database error")
            mock_connect.return_value.__aenter__.return_value = mock_db

            with pytest.raises(Exception, match="Database error"):
                await get_or_create_platform_profile(
                    platform="telegram",
                    platform_user_id="456",
                    username="testuser",
                    display_name="Test User",
                )

    @pytest.mark.asyncio
    async def test_update_letta_user_success(self):
        """Test successful user update."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = (
                123,  # id
                "2023-01-01T12:00:00",  # created_at
                "2023-01-01T12:00:00",  # last_active
                "identity_123",  # letta_identity_id
                '{"theme": "dark"}',  # agent_preferences
                "Custom instructions",  # custom_instructions
                True,  # is_active
            )
            mock_db.execute.return_value.__aenter__.return_value = mock_cursor
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await update_letta_user(
                user_id=123,
                agent_preferences={"theme": "dark"},
                custom_instructions="Custom instructions",
            )

            assert isinstance(result, LettaUser)
            assert result.id == 123
            assert result.custom_instructions == "Custom instructions"

    @pytest.mark.asyncio
    async def test_update_letta_user_no_updates(self):
        """Test user update with no updates specified."""
        with pytest.raises(ValueError, match="No updates specified"):
            await update_letta_user(user_id=123)

    @pytest.mark.asyncio
    async def test_update_letta_user_not_found(self):
        """Test user update when user not found."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = None
            mock_db.execute.return_value.__aenter__.return_value = mock_cursor
            mock_connect.return_value.__aenter__.return_value = mock_db

            with pytest.raises(ValueError, match="User with ID 123 not found"):
                await update_letta_user(user_id=123, custom_instructions="Test")

    @pytest.mark.asyncio
    async def test_update_letta_user_exception(self):
        """Test user update with database exception."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = AsyncMock()
            mock_db.execute.side_effect = Exception("Database error")
            mock_connect.return_value.__aenter__.return_value = mock_db

            with pytest.raises(Exception, match="Database error"):
                await update_letta_user(user_id=123, custom_instructions="Test")

    @pytest.mark.asyncio
    async def test_get_user_details_success(self):
        """Test successful retrieval of user details."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = ("Test User", "testuser")
            mock_db.execute.return_value.__aenter__.return_value = mock_cursor
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await get_user_details(123)

            assert result == ("Test User", "testuser")

    @pytest.mark.asyncio
    async def test_get_user_details_not_found(self):
        """Test user details retrieval when user not found."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = None
            mock_db.execute.return_value.__aenter__.return_value = mock_cursor
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await get_user_details(123)

            assert result is None

    @pytest.mark.asyncio
    async def test_get_user_details_exception(self):
        """Test user details retrieval with database exception."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = AsyncMock()
            mock_db.execute.side_effect = Exception("Database error")
            mock_connect.return_value.__aenter__.return_value = mock_db

            with pytest.raises(Exception, match="Database error"):
                await get_user_details(123)

    @pytest.mark.asyncio
    async def test_get_all_users_success(self):
        """Test successful retrieval of all users."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.fetchall.return_value = [
                (
                    123,  # id
                    "2023-01-01T12:00:00",  # created_at
                    "2023-01-01T12:00:00",  # last_active
                    "identity_123",  # letta_identity_id
                    '{"theme": "dark"}',  # agent_preferences
                    "Custom instructions",  # custom_instructions
                    True,  # is_active
                    "testuser",  # username
                    "Test User",  # display_name
                    "telegram",  # platform
                ),
                (
                    124,  # id
                    "2023-01-01T12:01:00",  # created_at
                    "2023-01-01T12:01:00",  # last_active
                    "identity_124",  # letta_identity_id
                    None,  # agent_preferences
                    None,  # custom_instructions
                    True,  # is_active
                    "user2",  # username
                    "User Two",  # display_name
                    "web_chat",  # platform
                ),
            ]
            mock_db.execute.return_value.__aenter__.return_value = mock_cursor
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await get_all_users()

            assert len(result) == 2
            assert result[0]["id"] == 123
            assert result[0]["username"] == "testuser"
            assert result[0]["agent_preferences"] == {"theme": "dark"}
            assert result[1]["id"] == 124
            assert result[1]["agent_preferences"] is None

    @pytest.mark.asyncio
    async def test_get_all_users_empty(self):
        """Test retrieval when no users exist."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.fetchall.return_value = []
            mock_db.execute.return_value.__aenter__.return_value = mock_cursor
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await get_all_users()

            assert result == []

    @pytest.mark.asyncio
    async def test_get_all_users_exception(self):
        """Test get_all_users with database exception."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = AsyncMock()
            mock_db.execute.side_effect = Exception("Database error")
            mock_connect.return_value.__aenter__.return_value = mock_db

            with pytest.raises(Exception, match="Database error"):
                await get_all_users()

    @pytest.mark.asyncio
    async def test_get_platform_profile_id_success(self):
        """Test successful retrieval of platform profile ID."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = (1, "456")
            mock_db.execute.return_value.__aenter__.return_value = mock_cursor
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await get_platform_profile_id(123)

            assert result == (1, "456")

    @pytest.mark.asyncio
    async def test_get_platform_profile_id_not_found(self):
        """Test platform profile ID retrieval when not found."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = None
            mock_db.execute.return_value.__aenter__.return_value = mock_cursor
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await get_platform_profile_id(123)

            assert result is None

    @pytest.mark.asyncio
    async def test_get_platform_profile_success(self):
        """Test successful retrieval of platform profile."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = (
                1,  # id
                123,  # letta_user_id
                "telegram",  # platform
                "456",  # platform_user_id
                "testuser",  # username
                "Test User",  # display_name
                '{"key": "value"}',  # metadata
                "2023-01-01T12:00:00",  # created_at
                "2023-01-01T12:00:00",  # last_active
            )
            mock_db.execute.return_value.__aenter__.return_value = mock_cursor
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await get_platform_profile(1)

            assert isinstance(result, PlatformProfile)
            assert result.id == 1
            assert result.platform == "telegram"
            assert result.username == "testuser"

    @pytest.mark.asyncio
    async def test_get_platform_profile_not_found(self):
        """Test platform profile retrieval when not found."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = None
            mock_db.execute.return_value.__aenter__.return_value = mock_cursor
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await get_platform_profile(1)

            assert result is None

    @pytest.mark.asyncio
    async def test_get_letta_user_block_id_success(self):
        """Test successful retrieval of Letta user block ID."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = ("block_123",)
            mock_db.execute.return_value.__aenter__.return_value = mock_cursor
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await get_letta_user_block_id(123)

            assert result == "block_123"

    @pytest.mark.asyncio
    async def test_get_letta_user_block_id_not_found(self):
        """Test Letta user block ID retrieval when not found."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = None
            mock_db.execute.return_value.__aenter__.return_value = mock_cursor
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await get_letta_user_block_id(123)

            assert result is None

    @pytest.mark.asyncio
    async def test_upsert_user_success(self):
        """Test successful user upsert."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = AsyncMock()
            mock_connect.return_value.__aenter__.return_value = mock_db

            await upsert_user(user_id=123, username="testuser", first_name="Test")

            mock_db.execute.assert_called_once()
            mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_upsert_user_exception(self):
        """Test user upsert with database exception."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = AsyncMock()
            mock_db.execute.side_effect = Exception("Database error")
            mock_connect.return_value.__aenter__.return_value = mock_db

            with pytest.raises(Exception, match="Database error"):
                await upsert_user(user_id=123, username="testuser", first_name="Test")

    @pytest.mark.asyncio
    async def test_user_operations_with_different_platforms(self):
        """Test user operations with different platforms."""
        platforms = ["telegram", "web_chat", "discord", "slack"]

        for platform in platforms:
            with patch(
                "database.operations.users.get_or_create_letta_user"
            ) as mock_create_user:
                mock_user = LettaUser(
                    id=123,
                    created_at="2023-01-01T12:00:00",
                    last_active="2023-01-01T12:00:00",
                    letta_identity_id="identity_123",
                    letta_block_id="block_456",
                    agent_preferences=None,
                    custom_instructions=None,
                    is_active=True,
                )
                mock_create_user.return_value = mock_user

                with patch("aiosqlite.connect") as mock_connect:
                    mock_db = AsyncMock()
                    mock_cursor = AsyncMock()
                    mock_cursor.lastrowid = 1
                    mock_db.execute.return_value = mock_cursor
                    mock_connect.return_value.__aenter__.return_value = mock_db

                    # Mock profile fetch returning None (new profile)
                    mock_profile_cursor = AsyncMock()
                    mock_profile_cursor.fetchone.return_value = None
                    mock_db.execute.return_value.__aenter__.return_value = (
                        mock_profile_cursor
                    )

                    profile, user = await get_or_create_platform_profile(
                        platform=platform,
                        platform_user_id="456",
                        username="testuser",
                        display_name="Test User",
                    )

                    assert isinstance(profile, PlatformProfile)
                    assert profile.platform == platform

    @pytest.mark.asyncio
    async def test_user_operations_with_edge_cases(self):
        """Test user operations with edge cases."""
        # Test with None values
        with patch("database.operations.users.get_letta_client") as mock_get_client:
            mock_client = MagicMock()
            mock_identity = MagicMock()
            mock_identity.id = "identity_123"
            mock_block = MagicMock()
            mock_block.id = "block_456"
            mock_client.identities.create.return_value = mock_identity
            mock_client.blocks.create.return_value = mock_block
            mock_get_client.return_value = mock_client

            with patch("aiosqlite.connect") as mock_connect:
                mock_db = AsyncMock()
                mock_cursor = AsyncMock()
                mock_cursor.lastrowid = 1
                mock_db.execute.return_value = mock_cursor
                mock_connect.return_value.__aenter__.return_value = mock_db

                result = await get_or_create_letta_user(
                    username=None, display_name=None, platform_user_id=None
                )

                assert isinstance(result, LettaUser)

        # Test with empty strings
        with patch("database.operations.users.get_letta_client") as mock_get_client:
            mock_client = MagicMock()
            mock_identity = MagicMock()
            mock_identity.id = "identity_123"
            mock_block = MagicMock()
            mock_block.id = "block_456"
            mock_client.identities.create.return_value = mock_identity
            mock_client.blocks.create.return_value = mock_block
            mock_get_client.return_value = mock_client

            with patch("aiosqlite.connect") as mock_connect:
                mock_db = AsyncMock()
                mock_cursor = AsyncMock()
                mock_cursor.lastrowid = 1
                mock_db.execute.return_value = mock_cursor
                mock_connect.return_value.__aenter__.return_value = mock_db

                result = await get_or_create_letta_user(
                    username="", display_name="", platform_user_id=""
                )

                assert isinstance(result, LettaUser)

    @pytest.mark.asyncio
    async def test_user_operations_with_special_characters(self):
        """Test user operations with special characters."""
        special_names = [
            "Test User with Spaces",
            "User-With-Dashes",
            "User_With_Underscores",
            "User.With.Dots",
            "User@With@Symbols",
            "User With Émojis 🚀",
            "用户中文",
            "ユーザー日本語",
        ]

        for name in special_names:
            with patch("database.operations.users.get_letta_client") as mock_get_client:
                mock_client = MagicMock()
                mock_identity = MagicMock()
                mock_identity.id = "identity_123"
                mock_block = MagicMock()
                mock_block.id = "block_456"
                mock_client.identities.create.return_value = mock_identity
                mock_client.blocks.create.return_value = mock_block
                mock_get_client.return_value = mock_client

                with patch("aiosqlite.connect") as mock_connect:
                    mock_db = AsyncMock()
                    mock_cursor = AsyncMock()
                    mock_cursor.lastrowid = 1
                    mock_db.execute.return_value = mock_cursor
                    mock_connect.return_value.__aenter__.return_value = mock_db

                    result = await get_or_create_letta_user(
                        username=name, display_name=name, platform_user_id="123"
                    )

                    assert isinstance(result, LettaUser)

    @pytest.mark.asyncio
    async def test_concurrent_user_operations(self):
        """Test concurrent user operations."""
        with patch("database.operations.users.get_letta_client") as mock_get_client:
            mock_client = MagicMock()
            mock_identity = MagicMock()
            mock_identity.id = "identity_123"
            mock_block = MagicMock()
            mock_block.id = "block_456"
            mock_client.identities.create.return_value = mock_identity
            mock_client.blocks.create.return_value = mock_block
            mock_get_client.return_value = mock_client

            with patch("aiosqlite.connect") as mock_connect:
                mock_db = AsyncMock()
                mock_cursor = AsyncMock()
                mock_cursor.lastrowid = 1
                mock_db.execute.return_value = mock_cursor
                mock_connect.return_value.__aenter__.return_value = mock_db

                # Test concurrent operations
                tasks = [
                    get_or_create_letta_user(username="user1", display_name="User 1"),
                    get_or_create_letta_user(username="user2", display_name="User 2"),
                    get_user_details(123),
                    get_all_users(),
                ]

                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Should not raise exceptions
                for result in results:
                    assert not isinstance(result, Exception)
