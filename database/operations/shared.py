"""Shared database operations (initialization, migration, and common utilities)."""

import logging
import os

import aiosqlite

from ..models import SCHEMA


def get_db_path() -> str:
    """Get the database path, respecting test environment."""
    return os.environ.get("TEST_DB_PATH") or os.path.join(
        os.path.dirname(__file__), "..", "..", "sanctum.db"
    )


# Set up logging
logger = logging.getLogger(__name__)


async def initialize_database():
    """Safely initialize the database by creating tables if they don't exist.
    This function will never drop or modify existing data."""
    try:
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
    async with aiosqlite.connect(get_db_path()) as db:
        # Check if all tables exist
        for table_name in SCHEMA.keys():
            try:
                await db.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
            except aiosqlite.OperationalError:
                logger.info(f"Table {table_name} does not exist, creating...")
                await db.execute(SCHEMA[table_name])

        await db.commit()


async def get_dashboard_stats() -> dict:
    """Get statistics for the dashboard."""
    async with aiosqlite.connect(get_db_path()) as db:
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
