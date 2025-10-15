"""Queue-related database operations (add, get, update, flush, etc)."""

import logging
import os
from datetime import datetime
from typing import Any

import aiosqlite

from common.retry import RetryConfig, exponential_backoff, is_retryable_exception

from ..models import QueueItem


def get_db_path() -> str:
    """Get the database path, respecting test environment."""
    return os.environ.get("TEST_DB_PATH") or os.path.join(
        os.path.dirname(__file__), "..", "..", "sanctum.db"
    )


# Set up logger
logger = logging.getLogger(__name__)

# Retry configuration for database operations
DB_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    base_delay=0.5,
    max_delay=10.0,
    jitter=True,
)


async def add_to_queue(letta_user_id: int, message_id: int) -> None:
    """Add a message to the processing queue."""
    now = datetime.utcnow().isoformat()

    async with aiosqlite.connect(get_db_path()) as db:
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
    async with aiosqlite.connect(get_db_path()) as db:
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


async def atomic_dequeue_item() -> QueueItem | None:
    """Atomically dequeue the next pending item and mark it as processing.

    This prevents race conditions where multiple processes could pick up
    the same queue item. Uses a single transaction to both select and update.

    Returns:
        QueueItem if a pending item was found and marked as processing, None otherwise
    """
    async with aiosqlite.connect(get_db_path()) as db:
        # Start transaction
        await db.execute("BEGIN IMMEDIATE")

        try:
            # Find the next pending item
            async with db.execute(
                """
                SELECT * FROM queue
                WHERE status = 'pending'
                ORDER BY timestamp ASC
                LIMIT 1
            """
            ) as cursor:
                row = await cursor.fetchone()

                if not row:
                    await db.execute("ROLLBACK")
                    return None

                queue_id = row[0]

                # Atomically mark as processing
                await db.execute(
                    """
                    UPDATE queue
                    SET status = 'processing', timestamp = ?
                    WHERE id = ? AND status = 'pending'
                """,
                    (datetime.utcnow().isoformat(), queue_id),
                )

                # Check if the update affected any rows (prevents race condition)
                if db.total_changes == 0:
                    await db.execute("ROLLBACK")
                    return None

                # Commit the transaction
                await db.execute("COMMIT")

                # Return the updated item
                return QueueItem(
                    id=row[0],
                    letta_user_id=row[1],
                    message_id=row[2],
                    status="processing",  # Status is now processing
                    attempts=row[4],
                    timestamp=datetime.utcnow().isoformat(),
                )

        except Exception as e:
            await db.execute("ROLLBACK")
            logger.error(f"Error in atomic dequeue: {str(e)}")
            return None


async def requeue_failed_item(queue_id: int, max_attempts: int = 3) -> bool:
    """Requeue a failed item if it hasn't exceeded max attempts.

    Args:
        queue_id: ID of the queue item to requeue
        max_attempts: Maximum number of attempts before giving up

    Returns:
        True if item was requeued, False if max attempts exceeded
    """

    async def _requeue_operation():
        async with aiosqlite.connect(get_db_path()) as db:
            # Check current attempts
            async with db.execute(
                "SELECT attempts FROM queue WHERE id = ?", (queue_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return False

                attempts = row[0]

                if attempts >= max_attempts:
                    # Mark as permanently failed
                    await db.execute(
                        """
                        UPDATE queue
                        SET status = 'failed', timestamp = ?
                        WHERE id = ?
                    """,
                        (datetime.utcnow().isoformat(), queue_id),
                    )
                    await db.commit()
                    logger.warning(
                        f"Queue item {queue_id} exceeded max attempts ({max_attempts}), marking as failed"
                    )
                    return False

                # Requeue as pending
                await db.execute(
                    """
                    UPDATE queue
                    SET status = 'pending', timestamp = ?
                    WHERE id = ?
                """,
                    (datetime.utcnow().isoformat(), queue_id),
                )
                await db.commit()
                logger.info(
                    f"Requeued item {queue_id} (attempt {attempts + 1}/{max_attempts})"
                )
                return True

    try:
        return await exponential_backoff(
            _requeue_operation,
            config=DB_RETRY_CONFIG,
            retry_on_exception=is_retryable_exception,
        )
    except Exception as e:
        logger.error(f"Failed to requeue item {queue_id} after retries: {e}")
        return False


async def update_queue_status(
    queue_id: int, status: str, increment_attempt: bool = False
) -> QueueItem:
    """Update the status of a queue item."""
    now = datetime.utcnow().isoformat()

    async with aiosqlite.connect(get_db_path()) as db:
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
    async with aiosqlite.connect(get_db_path()) as db:
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


async def get_queue_statistics() -> dict[str, int]:
    """Get queue statistics by status.

    Returns:
        Dictionary with counts for each status
    """
    async with aiosqlite.connect(get_db_path()) as db:
        async with db.execute(
            """
            SELECT status, COUNT(*) as count
            FROM queue
            WHERE status IN ('pending', 'processing', 'failed', 'completed', 'flushed')
            GROUP BY status
        """
        ) as cursor:
            rows = await cursor.fetchall()
            stats = {row[0]: row[1] for row in rows}

            # Ensure all statuses are present with 0 count
            all_statuses = ["pending", "processing", "failed", "completed", "flushed"]
            for status in all_statuses:
                if status not in stats:
                    stats[status] = 0

            return stats


async def flush_all_queue_items(current_mode: str) -> bool:
    """Flush all queue items for the current mode."""
    async with aiosqlite.connect(get_db_path()) as db:
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
    async with aiosqlite.connect(get_db_path()) as db:
        try:
            await db.execute("DELETE FROM queue WHERE id = ?", (queue_id,))
            await db.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting queue item {queue_id}: {str(e)}")
            return False
