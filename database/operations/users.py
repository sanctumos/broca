"""User-related database operations (get_or_create_user, platform lookup, etc)."""

import json
import logging
import uuid
from datetime import datetime
from typing import Any

import aiosqlite

from runtime.core.letta_client import get_letta_client

from ..models import LettaUser, PlatformProfile
from ..pool import get_pool

# Set up logging
logger = logging.getLogger(__name__)


async def get_or_create_letta_user(
    username: str = None, display_name: str = None, platform_user_id: str = None
) -> LettaUser:
    """Create a new Letta user with default settings and associated Letta identity."""
    now = datetime.utcnow().isoformat()

    try:
        # Get the singleton Letta client
        client = get_letta_client()

        # Parse name components
        name_parts = (display_name or username or "Unknown User").split()
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else None

        # 1. Create Letta identity
        unique_id = str(uuid.uuid4())[:8]
        identity_data = {
            "identifier_key": f"broca_user_{unique_id}",
            "name": display_name or username or f"Unknown User {platform_user_id}",
            "identity_type": "user",
        }
        identity = client.identities.create(**identity_data)

        # 2. Create core block with standardized format
        block_content = []
        if first_name and last_name:
            block_content.append(f"About Me ({first_name}, {last_name})")
        elif first_name:
            block_content.append(f"About Me ({first_name})")
        else:
            block_content.append(f"About Me ({username or 'Unknown User'})")

        block_content.append(f"This user's Telegram ID is: {platform_user_id}")
        if username:
            block_content.append(f"This user's Telegram Username is: {username}")

        block_data = {
            "label": "human",  # Always use "human" as the label
            "value": json.dumps(
                {
                    "type": "human_core",
                    "data": {
                        "name": display_name
                        or username
                        or f"Unknown User {platform_user_id}",
                        "created_at": now,
                        "content": "\n".join(block_content),
                    },
                }
            ),
        }
        block = client.blocks.create(**block_data)

        # 3. Create user record with Letta identity ID and block ID
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
                (now, now, identity.id, block.id, None, None, True),
            )
            await db.commit()

            user_id = cursor.lastrowid
            return LettaUser(
                id=user_id,
                created_at=now,
                last_active=now,
                letta_identity_id=identity.id,
                letta_block_id=block.id,
                agent_preferences=None,
                custom_instructions=None,
                is_active=True,
            )

    except Exception as e:
        logger.error(f"Error creating Letta user and identity: {str(e)}")
        raise


async def get_or_create_platform_profile(
    platform: str,
    platform_user_id: str,
    username: str,
    display_name: str,
    metadata: dict[str, Any] | None = None,
) -> tuple[PlatformProfile, LettaUser]:
    """Get or create a platform profile and its associated Letta user."""
    now = datetime.utcnow().isoformat()
    metadata_json = json.dumps(metadata) if metadata else None

    async with get_pool().connection() as db:
        # Check if profile exists
        async with db.execute(
            "SELECT * FROM platform_profiles WHERE platform = ? AND platform_user_id = ?",
            (platform, platform_user_id),
        ) as cursor:
            profile_row = await cursor.fetchone()

            if profile_row:
                # Update existing profile
                await db.execute(
                    """
                    UPDATE platform_profiles
                    SET username = ?, display_name = ?, metadata = ?, last_active = ?
                    WHERE id = ?
                """,
                    (username, display_name, metadata_json, now, profile_row[0]),
                )
                await db.commit()

                # Get associated Letta user
                async with db.execute(
                    "SELECT * FROM letta_users WHERE id = ?",
                    (profile_row[1],),  # letta_user_id
                ) as user_cursor:
                    user_row = await user_cursor.fetchone()
                    letta_user = LettaUser(
                        id=user_row[0],
                        created_at=user_row[1],
                        last_active=user_row[2],
                        letta_identity_id=user_row[3],
                        agent_preferences=user_row[4],
                        custom_instructions=user_row[5],
                        is_active=bool(user_row[6]),
                    )

                profile = PlatformProfile(
                    id=profile_row[0],
                    letta_user_id=profile_row[1],
                    platform=profile_row[2],
                    platform_user_id=profile_row[3],
                    username=username,
                    display_name=display_name,
                    metadata=metadata_json,
                    created_at=profile_row[7],
                    last_active=now,
                )

                return profile, letta_user

            # Create new Letta user and profile
            letta_user = await get_or_create_letta_user(
                username=username,
                display_name=display_name,
                platform_user_id=platform_user_id,
            )

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
                    letta_user.id,
                    platform,
                    platform_user_id,
                    username,
                    display_name,
                    metadata_json,
                    now,
                    now,
                ),
            )
            await db.commit()

            profile = PlatformProfile(
                id=cursor.lastrowid,
                letta_user_id=letta_user.id,
                platform=platform,
                platform_user_id=platform_user_id,
                username=username,
                display_name=display_name,
                metadata=metadata_json,
                created_at=now,
                last_active=now,
            )

            return profile, letta_user


async def update_letta_user(
    user_id: int,
    agent_preferences: dict[str, Any] | None = None,
    custom_instructions: str | None = None,
) -> LettaUser:
    """
    Update a Letta user's preferences and settings in the database.

    Args:
        user_id: The ID of the user to update.
        agent_preferences: Optional dictionary of agent preferences to store as JSON.
        custom_instructions: Optional custom instructions for the user.

    Returns:
        LettaUser: The updated user object.
    """
    now = datetime.utcnow().isoformat()
    updates = []
    values = []

    if agent_preferences is not None:
        updates.append("agent_preferences = ?")
        values.append(json.dumps(agent_preferences))

    if custom_instructions is not None:
        updates.append("custom_instructions = ?")
        values.append(custom_instructions)

    updates.append("last_active = ?")
    values.append(now)

    if not updates:
        raise ValueError("No updates specified")

    async with get_pool().connection() as db:
        query = f"""
            UPDATE letta_users
            SET {', '.join(updates)}
            WHERE id = ?
            RETURNING *
        """
        values.append(user_id)

        async with db.execute(query, values) as cursor:
            row = await cursor.fetchone()
            if not row:
                raise ValueError(f"User with ID {user_id} not found")

            await db.commit()
            return LettaUser(
                id=row[0],
                created_at=row[1],
                last_active=row[2],
                letta_identity_id=row[3],
                agent_preferences=row[4],
                custom_instructions=row[5],
                is_active=bool(row[6]),
            )


async def get_user_details(letta_user_id: int) -> tuple[str, str] | None:
    """Get user details for a Letta user."""
    async with get_pool().connection() as db:
        async with db.execute(
            """
            SELECT display_name, username
            FROM platform_profiles
            WHERE letta_user_id = ?
        """,
            (letta_user_id,),
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0], row[1]
            return None


async def get_all_users() -> list[dict[str, Any]]:
    """
    Retrieve all users with their details, including platform profile information.

    Returns:
        List[Dict[str, Any]]: List of user records with associated profile data.
    """
    async with get_pool().connection() as db:
        async with db.execute(
            """
            SELECT
                lu.id, lu.created_at, lu.last_active, lu.letta_identity_id,
                lu.agent_preferences, lu.custom_instructions,
                lu.is_active,
                pp.username, pp.display_name, pp.platform
            FROM letta_users lu
            LEFT JOIN platform_profiles pp ON lu.id = pp.letta_user_id
        """
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "created_at": row[1],
                    "last_active": row[2],
                    "letta_identity_id": row[3],
                    "agent_preferences": json.loads(row[4]) if row[4] else None,
                    "custom_instructions": row[5],
                    "is_active": bool(row[6]),
                    "username": row[7],
                    "display_name": row[8],
                    "platform": row[9],
                }
                for row in rows
            ]


async def get_platform_profile_id(letta_user_id: int) -> tuple[int, str] | None:
    """Get platform profile ID and platform user ID for a Letta user."""
    async with get_pool().connection() as db:
        async with db.execute(
            """
            SELECT id, platform_user_id
            FROM platform_profiles
            WHERE letta_user_id = ?
        """,
            (letta_user_id,),
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0], row[1]
            return None


async def get_platform_profile(profile_id: int) -> PlatformProfile | None:
    """Get platform profile by ID."""
    async with get_pool().connection() as db:
        async with db.execute(
            """
            SELECT id, letta_user_id, platform, platform_user_id, username,
                   display_name, metadata, created_at, last_active
            FROM platform_profiles
            WHERE id = ?
        """,
            (profile_id,),
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return PlatformProfile(
                    id=row[0],
                    letta_user_id=row[1],
                    platform=row[2],
                    platform_user_id=row[3],
                    username=row[4],
                    display_name=row[5],
                    metadata=row[6],
                    created_at=row[7],
                    last_active=row[8],
                )
            return None


async def get_letta_user_block_id(letta_user_id: int) -> str | None:
    """Get the Letta block ID for a user."""
    async with get_pool().connection() as db:
        async with db.execute(
            """
            SELECT letta_block_id
            FROM letta_users
            WHERE id = ?
        """,
            (letta_user_id,),
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]
            return None


async def upsert_user(user_id: int, username: str, first_name: str) -> None:
    """Upsert a user's details."""
    now = datetime.utcnow().isoformat()
    async with get_pool().connection() as db:
        await db.execute(
            """
            INSERT INTO platform_profiles (
                letta_user_id, platform, platform_user_id, username, display_name,
                created_at, last_active
            ) VALUES (?, 'telegram', ?, ?, ?, ?, ?)
            ON CONFLICT(platform, platform_user_id) DO UPDATE SET
                username = excluded.username,
                display_name = excluded.display_name,
                last_active = excluded.last_active
        """,
            (user_id, str(user_id), username, first_name, now, now),
        )
        await db.commit()
