"""Shared database operations (initialization, migration, and common utilities)."""

import logging
import os

import aiosqlite

from ..models import SCHEMA
from ..pool import get_pool

# Whitelist of valid table names for SQL injection prevention
VALID_TABLE_NAMES = set(SCHEMA.keys())


def validate_table_name(table_name: str) -> str:
    """Validate that a table name is in the whitelist.

    This prevents SQL injection by ensuring only known table names
    can be used in dynamic SQL queries.

    Args:
        table_name: Table name to validate

    Returns:
        The validated table name

    Raises:
        ValueError: If table name is not in whitelist
    """
    if table_name not in VALID_TABLE_NAMES:
        raise ValueError(
            f"Invalid table name: {table_name}. "
            f"Must be one of: {sorted(VALID_TABLE_NAMES)}"
        )
    return table_name


def get_db_path() -> str:
    """Get the database path, respecting environment variables and test environment.

    Priority:
    1. TEST_DB_PATH (for tests)
    2. DB_PATH (for configuration)
    3. Default: sanctum.db in project root

    Returns:
        Path to the database file
    """
    # Test environment takes precedence
    if "TEST_DB_PATH" in os.environ:
        return os.environ["TEST_DB_PATH"]

    # Allow configuration via DB_PATH environment variable
    if "DB_PATH" in os.environ:
        return os.environ["DB_PATH"]

    # Default to sanctum.db in project root
    return os.path.join(os.path.dirname(__file__), "..", "..", "sanctum.db")


# Set up logging
logger = logging.getLogger(__name__)


async def initialize_database():
    """Safely initialize the database by creating tables if they don't exist.
    This function will never drop or modify existing data.
    
    Note: Uses direct connection (not pool) since this is called during initialization
    before the pool is ready.
    """
    try:
        # Use direct connection for initialization (pool may not be ready yet)
        import aiosqlite
        async with aiosqlite.connect(get_db_path()) as db:
            # Enable foreign keys
            await db.execute("PRAGMA foreign_keys = ON")

            # Create tables if they don't exist
            for table_name, create_sql in SCHEMA.items():
                try:
                    await db.execute(create_sql)
                    logger.info(f"Created table {table_name} if it didn't exist")
                except Exception as e:
                    logger.error(f"Error creating table {table_name}: {str(e)}")
                    raise

            await db.commit()
            logger.info("Database initialization completed successfully")

    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


async def check_and_migrate_db():
    """Check and migrate the database schema if needed."""
    async with get_pool().connection() as db:
        # Check if all tables exist
        for table_name in SCHEMA.keys():
            try:
                # Validate table name against whitelist to prevent SQL injection
                validated_table = validate_table_name(table_name)
                await db.execute(f"SELECT 1 FROM {validated_table} LIMIT 1")
            except aiosqlite.OperationalError:
                logger.info(f"Table {table_name} does not exist, creating...")
                await db.execute(SCHEMA[table_name])

        await db.commit()


async def get_dashboard_stats() -> dict:
    """Get statistics for the dashboard."""
    async with get_pool().connection() as db:
        stats = {}

        # Get user count
        async with db.execute("SELECT COUNT(*) FROM letta_users") as cursor:
            stats["user_count"] = (await cursor.fetchone())[0]

        # Get message count
        async with db.execute("SELECT COUNT(*) FROM messages") as cursor:
            stats["message_count"] = (await cursor.fetchone())[0]

        # Get queue stats
        async with db.execute(
            """
            SELECT status, COUNT(*)
            FROM queue
            GROUP BY status
        """
        ) as cursor:
            queue_stats = await cursor.fetchall()
            stats["queue_stats"] = {row[0]: row[1] for row in queue_stats}

        return stats
