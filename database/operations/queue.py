"""Queue-related database operations (add, get, update, flush, etc)."""

import logging
import os
from datetime import datetime
from typing import Any

import aiosqlite

from ..models import QueueItem

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "sanctum.db")

# Set up logger
logger = logging.getLogger(__name__)


async def add_to_queue(letta_user_id: int, message_id: int) -> None:
    """Add a message to the processing queue."""
    now = datetime.utcnow().isoformat()

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO queue (
                letta_user_id,
                message_id,
                status,
                timestamp,
                attempts
            ) VALUES (?, ?, 'pending', ?, 0)
        """,
            (letta_user_id, message_id, now),
        )
        await db.commit()


async def get_pending_queue_item() -> QueueItem | None:
    """Get the next pending item from the queue."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT * FROM queue
            WHERE status = 'pending'
            ORDER BY timestamp ASC
            LIMIT 1
        """
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return QueueItem(
                    id=row[0],
                    letta_user_id=row[1],
                    message_id=row[2],
                    status=row[3],
                    attempts=row[4],
                    timestamp=row[5],
                )
            return None


async def update_queue_status(
    queue_id: int, status: str, increment_attempt: bool = False
) -> QueueItem:
    """Update the status of a queue item."""
    now = datetime.utcnow().isoformat()

    async with aiosqlite.connect(DB_PATH) as db:
        if increment_attempt:
            await db.execute(
                """
                UPDATE queue
                SET status = ?, timestamp = ?, attempts = attempts + 1
                WHERE id = ?
            """,
                (status, now, queue_id),
            )
        else:
            await db.execute(
                """
                UPDATE queue
                SET status = ?, timestamp = ?
                WHERE id = ?
            """,
                (status, now, queue_id),
            )

        await db.commit()

        async with db.execute(
            "SELECT * FROM queue WHERE id = ?", (queue_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return QueueItem(
                    id=row[0],
                    letta_user_id=row[1],
                    message_id=row[2],
                    status=row[3],
                    attempts=row[4],
                    timestamp=row[5],
                )
            raise ValueError(f"Queue item with ID {queue_id} not found")


async def get_all_queue_items() -> list[dict[str, Any]]:
    """Get all queue items with their details."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT
                q.id, q.letta_user_id, q.message_id, q.status,
                q.timestamp, q.attempts,
                pp.username, pp.display_name,
                m.message, m.agent_response
            FROM queue q
            LEFT JOIN platform_profiles pp ON q.letta_user_id = pp.letta_user_id
            LEFT JOIN messages m ON q.message_id = m.id
            WHERE q.status IN ('pending', 'processing', 'failed')
            ORDER BY q.timestamp DESC
        """
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "letta_user_id": row[1],
                    "message_id": row[2],
                    "status": row[3],
                    "timestamp": row[4],
                    "attempts": row[5],
                    "username": row[6],
                    "display_name": row[7],
                    "message": row[8],
                    "agent_response": row[9],
                }
                for row in rows
            ]


async def flush_all_queue_items(current_mode: str) -> bool:
    """Flush all queue items for the current mode."""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                """
                UPDATE queue
                SET status = 'flushed'
                WHERE status = 'pending'
            """
            )
            await db.commit()
            return True
        except Exception as e:
            logger.error(f"Error flushing queue items: {str(e)}")
            return False


async def delete_queue_item(queue_id: int) -> bool:
    """Delete a specific queue item."""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute("DELETE FROM queue WHERE id = ?", (queue_id,))
            await db.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting queue item {queue_id}: {str(e)}")
            return False
