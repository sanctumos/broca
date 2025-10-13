"""Database operations module - split into focused submodules for better organization.

This module provides a clean interface to all database operations, organized into
focused submodules:

users.py:
    - User management (get_or_create_letta_user, get_or_create_platform_profile)
    - User preferences (update_letta_user)
    - User lookups (get_user_details, get_all_users)
    - Platform profile management (get_platform_profile_id, upsert_user)

messages.py:
    - Message operations (insert_message, get_message_text)
    - Message updates (update_message_with_response)
    - Message history (get_message_history)

queue.py:
    - Queue management (add_to_queue, get_pending_queue_item)
    - Queue status (update_queue_status)
    - Queue monitoring (get_all_queue_items, flush_all_queue_items)

shared.py:
    - Database initialization (initialize_database, check_and_migrate_db)
    - Utility functions (get_dashboard_stats)

All functions are re-exported here for convenience, but can also be imported
directly from their respective submodules for better code organization.
"""

from .messages import (
    get_message_history,
    get_message_text,
    insert_message,
    update_message_with_response,
)
from .queue import (
    add_to_queue,
    delete_queue_item,
    flush_all_queue_items,
    get_all_queue_items,
    get_pending_queue_item,
    update_queue_status,
)
from .shared import check_and_migrate_db, get_dashboard_stats, initialize_database
from .users import (
    get_all_users,
    get_letta_user_block_id,
    get_or_create_letta_user,
    get_or_create_platform_profile,
    get_platform_profile_id,
    get_user_details,
    update_letta_user,
    upsert_user,
)

# Re-export everything for backward compatibility
__all__ = [
    # Users
    "get_or_create_letta_user",
    "get_or_create_platform_profile",
    "update_letta_user",
    "get_user_details",
    "get_all_users",
    "get_platform_profile_id",
    "get_letta_user_block_id",
    "upsert_user",
    # Messages
    "insert_message",
    "get_message_text",
    "update_message_with_response",
    "get_message_history",
    # Queue
    "add_to_queue",
    "get_pending_queue_item",
    "update_queue_status",
    "get_all_queue_items",
    "flush_all_queue_items",
    "delete_queue_item",
    # Shared
    "initialize_database",
    "check_and_migrate_db",
    "get_dashboard_stats",
]
