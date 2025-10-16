"""Comprehensive tests for database queue operations."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from database.models import QueueItem
from database.operations.queue import (
    add_to_queue,
    atomic_dequeue_item,
    delete_queue_item,
    flush_all_queue_items,
    get_all_queue_items,
    get_pending_queue_item,
    get_queue_statistics,
    requeue_failed_item,
    update_queue_status,
)


class AsyncContextManagerMock:
    """Mock async context manager for database operations."""

    def __init__(self, return_value=None):
        self.return_value = return_value

    async def __aenter__(self):
        return self.return_value

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class HybridExecuteMock:
    """Mock that can be both awaited and used as async context manager."""

    def __init__(self, cursor=None):
        self.cursor = cursor

    async def __aenter__(self):
        return self.cursor

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def __await__(self):
        # Make it awaitable for direct await calls
        return self.__aenter__().__await__()


class MockDatabase:
    """Mock database with proper async context manager support."""

    def __init__(self):
        self.commit = AsyncMock()
        self.total_changes = 1
        self._cursor = None
        self._execute_calls = []
        self._execute_side_effect = None

    def execute(self, *args, **kwargs):
        """Execute SQL and return a hybrid mock for both await and async with."""
        if self._execute_side_effect:
            # Only raise exception for non-BEGIN and non-ROLLBACK commands to allow transaction to start and rollback
            sql = args[0] if args else ""
            if not sql.strip().upper().startswith(("BEGIN", "ROLLBACK")):
                raise self._execute_side_effect
        self._execute_calls.append((args, kwargs))
        return HybridExecuteMock(self._cursor)

    def set_cursor(self, cursor):
        """Set the cursor for execute operations."""
        self._cursor = cursor

    def set_execute_side_effect(self, side_effect):
        """Set side effect for execute method."""
        self._execute_side_effect = side_effect

    def assert_execute_called_once(self):
        """Assert that execute was called once."""
        assert len(self._execute_calls) == 1


class TestQueueOperationsComprehensive:
    """Comprehensive tests for queue operations."""

    @pytest.mark.asyncio
    async def test_add_to_queue_success(self):
        """Test successful addition to queue."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_connect.return_value.__aenter__.return_value = mock_db

            await add_to_queue(123, 456)

            mock_db.assert_execute_called_once()
            mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_to_queue_with_exception(self):
        """Test add_to_queue with database exception."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_db.set_execute_side_effect(Exception("Database error"))
            mock_connect.return_value.__aenter__.return_value = mock_db

            with pytest.raises(Exception, match="Database error"):
                await add_to_queue(123, 456)

    @pytest.mark.asyncio
    async def test_get_pending_queue_item_success(self):
        """Test successful retrieval of pending queue item."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = (
                1,
                123,
                456,
                "pending",
                0,
                "2023-01-01T12:00:00",
            )
            mock_db.set_cursor(mock_cursor)
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await get_pending_queue_item()

            assert isinstance(result, QueueItem)
            assert result.id == 1
            assert result.letta_user_id == 123
            assert result.message_id == 456
            assert result.status == "pending"

    @pytest.mark.asyncio
    async def test_get_pending_queue_item_empty(self):
        """Test retrieval when no pending items exist."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = None
            mock_db.set_cursor(mock_cursor)
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await get_pending_queue_item()

            assert result is None

    @pytest.mark.asyncio
    async def test_get_pending_queue_item_with_exception(self):
        """Test get_pending_queue_item with database exception."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_db.set_execute_side_effect(Exception("Database error"))
            mock_connect.return_value.__aenter__.return_value = mock_db

            with pytest.raises(Exception, match="Database error"):
                await get_pending_queue_item()

    @pytest.mark.asyncio
    async def test_atomic_dequeue_item_success(self):
        """Test successful atomic dequeue operation."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = (
                1,
                123,
                456,
                "pending",
                0,
                "2023-01-01T12:00:00",
            )
            mock_db.set_cursor(mock_cursor)
            mock_db.total_changes = 1
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await atomic_dequeue_item()

            assert isinstance(result, QueueItem)
            assert result.id == 1
            assert result.status == "processing"

    @pytest.mark.asyncio
    async def test_atomic_dequeue_item_no_pending(self):
        """Test atomic dequeue when no pending items exist."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = None
            mock_db.set_cursor(mock_cursor)
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await atomic_dequeue_item()

            assert result is None

    @pytest.mark.asyncio
    async def test_atomic_dequeue_item_race_condition(self):
        """Test atomic dequeue with race condition (no rows affected)."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = (
                1,
                123,
                456,
                "pending",
                0,
                "2023-01-01T12:00:00",
            )
            mock_db.set_cursor(mock_cursor)
            mock_db.total_changes = 0  # Race condition - no rows affected
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await atomic_dequeue_item()

            assert result is None

    @pytest.mark.asyncio
    async def test_atomic_dequeue_item_exception(self):
        """Test atomic dequeue with exception during transaction."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_db.set_execute_side_effect(Exception("Database error"))
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await atomic_dequeue_item()

            assert result is None

    @pytest.mark.asyncio
    async def test_requeue_failed_item_success(self):
        """Test successful requeue of failed item."""
        with patch("database.operations.queue.exponential_backoff") as mock_backoff:
            mock_backoff.return_value = True

            async def mock_requeue_operation():
                with patch("aiosqlite.connect") as mock_connect:
                    mock_db = MockDatabase()
                    mock_cursor = AsyncMock()
                    mock_cursor.fetchone.return_value = (2,)  # attempts = 2
                    mock_db.execute.return_value = AsyncContextManagerMock(mock_cursor)
                    mock_connect.return_value.__aenter__.return_value = mock_db

                    return True

            with patch(
                "database.operations.queue._requeue_operation",
                side_effect=mock_requeue_operation,
            ):
                result = await requeue_failed_item(1, max_attempts=3)

                assert result is True

    @pytest.mark.asyncio
    async def test_requeue_failed_item_max_attempts_exceeded(self):
        """Test requeue when max attempts exceeded."""
        with patch("database.operations.queue.exponential_backoff") as mock_backoff:
            mock_backoff.return_value = False

            async def mock_requeue_operation():
                with patch("aiosqlite.connect") as mock_connect:
                    mock_db = MockDatabase()
                    mock_cursor = AsyncMock()
                    mock_cursor.fetchone.return_value = (3,)  # attempts = 3, max = 3
                    mock_db.execute.return_value = AsyncContextManagerMock(mock_cursor)
                    mock_connect.return_value.__aenter__.return_value = mock_db

                    return False

            with patch(
                "database.operations.queue._requeue_operation",
                side_effect=mock_requeue_operation,
            ):
                result = await requeue_failed_item(1, max_attempts=3)

                assert result is False

    @pytest.mark.asyncio
    async def test_requeue_failed_item_not_found(self):
        """Test requeue when item not found."""
        with patch("database.operations.queue.exponential_backoff") as mock_backoff:
            mock_backoff.return_value = False

            async def mock_requeue_operation():
                with patch("aiosqlite.connect") as mock_connect:
                    mock_db = MockDatabase()
                    mock_cursor = AsyncMock()
                    mock_cursor.fetchone.return_value = None
                    mock_db.execute.return_value = AsyncContextManagerMock(mock_cursor)
                    mock_connect.return_value.__aenter__.return_value = mock_db

                    return False

            with patch(
                "database.operations.queue._requeue_operation",
                side_effect=mock_requeue_operation,
            ):
                result = await requeue_failed_item(1, max_attempts=3)

                assert result is False

    @pytest.mark.asyncio
    async def test_requeue_failed_item_exception(self):
        """Test requeue with exception."""
        with patch("database.operations.queue.exponential_backoff") as mock_backoff:
            mock_backoff.side_effect = Exception("Retry failed")

            result = await requeue_failed_item(1, max_attempts=3)

            assert result is False

    @pytest.mark.asyncio
    async def test_update_queue_status_success(self):
        """Test successful queue status update."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = (
                1,
                123,
                456,
                "completed",
                1,
                "2023-01-01T12:00:00",
            )
            mock_db.execute.return_value = AsyncContextManagerMock(mock_cursor)
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await update_queue_status(1, "completed")

            assert isinstance(result, QueueItem)
            assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_update_queue_status_with_increment(self):
        """Test queue status update with attempt increment."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = (
                1,
                123,
                456,
                "failed",
                2,
                "2023-01-01T12:00:00",
            )
            mock_db.execute.return_value = AsyncContextManagerMock(mock_cursor)
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await update_queue_status(1, "failed", increment_attempt=True)

            assert isinstance(result, QueueItem)
            assert result.status == "failed"

    @pytest.mark.asyncio
    async def test_update_queue_status_not_found(self):
        """Test update queue status when item not found."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = None
            mock_db.set_cursor(mock_cursor)
            mock_connect.return_value.__aenter__.return_value = mock_db

            with pytest.raises(ValueError, match="Queue item with ID 1 not found"):
                await update_queue_status(1, "completed")

    @pytest.mark.asyncio
    async def test_update_queue_status_exception(self):
        """Test update queue status with database exception."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_db.set_execute_side_effect(Exception("Database error"))
            mock_connect.return_value.__aenter__.return_value = mock_db

            with pytest.raises(Exception, match="Database error"):
                await update_queue_status(1, "completed")

    @pytest.mark.asyncio
    async def test_get_all_queue_items_success(self):
        """Test successful retrieval of all queue items."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_cursor = AsyncMock()
            mock_cursor.fetchall.return_value = [
                (
                    1,
                    123,
                    456,
                    "pending",
                    "2023-01-01T12:00:00",
                    0,
                    "user1",
                    "User One",
                    "Hello",
                    None,
                ),
                (
                    2,
                    124,
                    457,
                    "processing",
                    "2023-01-01T12:01:00",
                    1,
                    "user2",
                    "User Two",
                    "Hi",
                    "Response",
                ),
            ]
            mock_db.execute.return_value = AsyncContextManagerMock(mock_cursor)
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await get_all_queue_items()

            assert len(result) == 2
            assert result[0]["id"] == 1
            assert result[0]["status"] == "pending"
            assert result[1]["id"] == 2
            assert result[1]["status"] == "processing"

    @pytest.mark.asyncio
    async def test_get_all_queue_items_empty(self):
        """Test retrieval when no queue items exist."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_cursor = AsyncMock()
            mock_cursor.fetchall.return_value = []
            mock_db.execute.return_value = AsyncContextManagerMock(mock_cursor)
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await get_all_queue_items()

            assert result == []

    @pytest.mark.asyncio
    async def test_get_all_queue_items_exception(self):
        """Test get_all_queue_items with database exception."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_db.set_execute_side_effect(Exception("Database error"))
            mock_connect.return_value.__aenter__.return_value = mock_db

            with pytest.raises(Exception, match="Database error"):
                await get_all_queue_items()

    @pytest.mark.asyncio
    async def test_get_queue_statistics_success(self):
        """Test successful retrieval of queue statistics."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_cursor = AsyncMock()
            mock_cursor.fetchall.return_value = [
                ("pending", 5),
                ("processing", 2),
                ("completed", 10),
                ("failed", 1),
            ]
            mock_db.execute.return_value = AsyncContextManagerMock(mock_cursor)
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await get_queue_statistics()

            assert result["pending"] == 5
            assert result["processing"] == 2
            assert result["completed"] == 10
            assert result["failed"] == 1
            assert result["flushed"] == 0  # Should be 0 if not in results

    @pytest.mark.asyncio
    async def test_get_queue_statistics_empty(self):
        """Test queue statistics when no items exist."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_cursor = AsyncMock()
            mock_cursor.fetchall.return_value = []
            mock_db.execute.return_value = AsyncContextManagerMock(mock_cursor)
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await get_queue_statistics()

            # All statuses should be 0
            for status in ["pending", "processing", "failed", "completed", "flushed"]:
                assert result[status] == 0

    @pytest.mark.asyncio
    async def test_get_queue_statistics_exception(self):
        """Test get_queue_statistics with database exception."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_db.set_execute_side_effect(Exception("Database error"))
            mock_connect.return_value.__aenter__.return_value = mock_db

            with pytest.raises(Exception, match="Database error"):
                await get_queue_statistics()

    @pytest.mark.asyncio
    async def test_flush_all_queue_items_success(self):
        """Test successful flush of all queue items."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await flush_all_queue_items("echo")

            assert result is True
            mock_db.assert_execute_called_once()
            mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_flush_all_queue_items_exception(self):
        """Test flush_all_queue_items with database exception."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_db.set_execute_side_effect(Exception("Database error"))
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await flush_all_queue_items("echo")

            assert result is False

    @pytest.mark.asyncio
    async def test_delete_queue_item_success(self):
        """Test successful deletion of queue item."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await delete_queue_item(1)

            assert result is True
            mock_db.assert_execute_called_once()
            mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_queue_item_exception(self):
        """Test delete_queue_item with database exception."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_db.set_execute_side_effect(Exception("Database error"))
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await delete_queue_item(1)

            assert result is False

    @pytest.mark.asyncio
    async def test_queue_item_creation(self):
        """Test QueueItem model creation."""
        item = QueueItem(
            id=1,
            letta_user_id=123,
            message_id=456,
            status="pending",
            attempts=0,
            timestamp="2023-01-01T12:00:00",
        )

        assert item.id == 1
        assert item.letta_user_id == 123
        assert item.message_id == 456
        assert item.status == "pending"
        assert item.attempts == 0
        assert item.timestamp == "2023-01-01T12:00:00"

    @pytest.mark.asyncio
    async def test_concurrent_queue_operations(self):
        """Test concurrent queue operations."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = (
                1,
                123,
                456,
                "pending",
                0,
                "2023-01-01T12:00:00",
            )
            mock_db.set_cursor(mock_cursor)
            mock_connect.return_value.__aenter__.return_value = mock_db

            # Test concurrent operations
            tasks = [
                add_to_queue(123, 456),
                add_to_queue(124, 457),
                get_pending_queue_item(),
                get_queue_statistics(),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Should not raise exceptions
            for result in results:
                assert not isinstance(result, Exception)

    @pytest.mark.asyncio
    async def test_queue_operations_with_different_statuses(self):
        """Test queue operations with different status values."""
        statuses = ["pending", "processing", "completed", "failed", "flushed"]

        for status in statuses:
            with patch("aiosqlite.connect") as mock_connect:
                mock_db = MockDatabase()
                mock_cursor = AsyncMock()
                mock_cursor.fetchone.return_value = (
                    1,
                    123,
                    456,
                    status,
                    0,
                    "2023-01-01T12:00:00",
                )
                mock_db.execute.return_value = AsyncContextManagerMock(mock_cursor)
                mock_connect.return_value.__aenter__.return_value = mock_db

                result = await update_queue_status(1, status)

                assert isinstance(result, QueueItem)
                assert result.status == status

    @pytest.mark.asyncio
    async def test_queue_operations_edge_cases(self):
        """Test queue operations with edge cases."""
        # Test with zero values
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_connect.return_value.__aenter__.return_value = mock_db

            await add_to_queue(0, 0)
            mock_db.assert_execute_called_once()

        # Test with large values
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_connect.return_value.__aenter__.return_value = mock_db

            await add_to_queue(999999, 999999)
            mock_db.assert_execute_called_once()

    @pytest.mark.asyncio
    async def test_queue_operations_with_none_values(self):
        """Test queue operations handling of None values."""
        with patch("aiosqlite.connect") as mock_connect:
            mock_db = MockDatabase()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = (1, 123, 456, "pending", 0, None)
            mock_db.execute.return_value = AsyncContextManagerMock(mock_cursor)
            mock_connect.return_value.__aenter__.return_value = mock_db

            result = await get_pending_queue_item()

            assert isinstance(result, QueueItem)
            assert result.timestamp is None
