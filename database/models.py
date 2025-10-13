"""
Database models and schemas for the application.

Copyright (C) 2024 Sanctum OS

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from dataclasses import dataclass


@dataclass
class LettaUser:
    """Master user model representing a user across all platforms. Contains user identity, preferences, and status fields."""

    id: int | None
    created_at: str
    last_active: str
    letta_identity_id: str | None = None  # ID of the associated Letta identity
    letta_block_id: str | None = None  # ID of the associated Letta core block
    agent_preferences: str | None = None  # JSON string
    custom_instructions: str | None = None
    is_active: bool = True


@dataclass
class PlatformProfile:
    """Platform-specific profile for a user."""

    id: int | None
    letta_user_id: int
    platform: str
    platform_user_id: str
    username: str
    display_name: str
    metadata: str | None = None  # JSON string
    created_at: str | None = None
    last_active: str | None = None


@dataclass
class Message:
    """Message model representing a message in the system."""

    id: int | None
    letta_user_id: int
    platform_profile_id: int
    role: str
    message: str
    timestamp: str
    processed: bool = False
    agent_response: str | None = None


@dataclass
class QueueItem:
    """Queue item model representing a message in the processing queue."""

    id: int | None
    letta_user_id: int
    message_id: int
    status: str  # 'pending', 'processing', 'done', 'failed'
    attempts: int = 0
    timestamp: str | None = None


@dataclass
class QueueItemDisplay:
    """Queue item model with additional display information for the UI."""

    id: int
    user_id: int
    message_id: int
    status: str
    attempts: int
    message: str
    timestamp: str
    username: str
    first_name: str


# Database schema definitions
SCHEMA = {
    # Table definitions for all core entities in the application database.
    "letta_users": """
        CREATE TABLE IF NOT EXISTS letta_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_active TEXT,
            letta_identity_id TEXT,
            letta_block_id TEXT,
            agent_preferences TEXT,
            custom_instructions TEXT,
            is_active INTEGER DEFAULT 1
        )
    """,
    "platform_profiles": """
        CREATE TABLE IF NOT EXISTS platform_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            letta_user_id INTEGER,
            platform TEXT,
            platform_user_id TEXT,
            username TEXT,
            display_name TEXT,
            metadata TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_active TEXT,
            FOREIGN KEY (letta_user_id) REFERENCES letta_users(id),
            UNIQUE(platform, platform_user_id)
        )
    """,
    "messages": """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            letta_user_id INTEGER,
            platform_profile_id INTEGER,
            role TEXT,
            message TEXT,
            timestamp TEXT,
            processed INTEGER DEFAULT 0,
            agent_response TEXT,
            FOREIGN KEY (letta_user_id) REFERENCES letta_users(id),
            FOREIGN KEY (platform_profile_id) REFERENCES platform_profiles(id)
        )
    """,
    "queue": """
        CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            letta_user_id INTEGER,
            message_id INTEGER,
            status TEXT,
            attempts INTEGER DEFAULT 0,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (letta_user_id) REFERENCES letta_users(id),
            FOREIGN KEY (message_id) REFERENCES messages(id)
        )
    """,
}
