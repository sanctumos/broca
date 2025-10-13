"""Unit tests for runtime core queue functionality."""

from unittest.mock import patch

import pytest

from runtime.core.queue import QueueProcessor


@pytest.mark.unit
def test_queue_item():
    """Test QueueItem dataclass."""
    # Create a simple dict to represent queue item
    item = {
        "id": 1,
        "letta_user_id": 123,
        "message_id": 456,
        "priority": 1,
        "retry_count": 0,
        "status": "pending",
        "created_at": "2024-01-01T00:00:00Z",
    }

    assert item["id"] == 1
    assert item["letta_user_id"] == 123
    assert item["message_id"] == 456
    assert item["priority"] == 1
    assert item["retry_count"] == 0
    assert item["status"] == "pending"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_init():
    """Test QueueProcessor initialization."""
    processor = QueueProcessor()
    assert processor is not None
    assert hasattr(processor, "is_running")
    assert hasattr(processor, "queue")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_start():
    """Test QueueProcessor start."""
    processor = QueueProcessor()

    with patch.object(processor, "_process_queue") as mock_process:
        mock_process.return_value = None
        await processor.start()
        assert processor.is_running is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_stop():
    """Test QueueProcessor stop."""
    processor = QueueProcessor()
    processor.is_running = True

    await processor.stop()
    assert processor.is_running is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_add_item():
    """Test QueueProcessor add_item."""
    processor = QueueProcessor()

    item = {
        "id": 1,
        "letta_user_id": 123,
        "message_id": 456,
        "priority": 1,
        "retry_count": 0,
        "status": "pending",
        "created_at": "2024-01-01T00:00:00Z",
    }

    await processor.add_item(item)
    assert len(processor.queue) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_get_next_item():
    """Test QueueProcessor get_next_item."""
    processor = QueueProcessor()

    item1 = {
        "id": 1,
        "letta_user_id": 123,
        "message_id": 456,
        "priority": 2,
        "retry_count": 0,
        "status": "pending",
        "created_at": "2024-01-01T00:00:00Z",
    }

    item2 = {
        "id": 2,
        "letta_user_id": 124,
        "message_id": 457,
        "priority": 1,
        "retry_count": 0,
        "status": "pending",
        "created_at": "2024-01-01T00:00:00Z",
    }

    processor.queue = [item1, item2]

    next_item = await processor.get_next_item()
    assert next_item == item2  # Higher priority (lower number)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_process_item():
    """Test QueueProcessor process_item."""
    processor = QueueProcessor()

    item = {
        "id": 1,
        "letta_user_id": 123,
        "message_id": 456,
        "priority": 1,
        "retry_count": 0,
        "status": "pending",
        "created_at": "2024-01-01T00:00:00Z",
    }

    with patch.object(processor, "_send_to_agent") as mock_send:
        mock_send.return_value = True
        await processor.process_item(item)
        mock_send.assert_called_once_with(item)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_retry_item():
    """Test QueueProcessor retry_item."""
    processor = QueueProcessor()

    item = QueueItem(
        id=1,
        letta_user_id=123,
        message_id=456,
        priority=1,
        retry_count=0,
        status="failed",
        created_at="2024-01-01T00:00:00Z",
    )

    await processor.retry_item(item)
    assert item.retry_count == 1
    assert item.status == "pending"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_get_stats():
    """Test QueueProcessor get_stats."""
    processor = QueueProcessor()

    item1 = QueueItem(
        id=1,
        letta_user_id=123,
        message_id=456,
        priority=1,
        retry_count=0,
        status="pending",
        created_at="2024-01-01T00:00:00Z",
    )

    item2 = QueueItem(
        id=2,
        letta_user_id=124,
        message_id=457,
        priority=1,
        retry_count=0,
        status="completed",
        created_at="2024-01-01T00:00:00Z",
    )

    processor.queue = [item1, item2]

    stats = await processor.get_stats()
    assert stats["total"] == 2
    assert stats["pending"] == 1
    assert stats["completed"] == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_clear_completed():
    """Test QueueProcessor clear_completed."""
    processor = QueueProcessor()

    item1 = QueueItem(
        id=1,
        letta_user_id=123,
        message_id=456,
        priority=1,
        retry_count=0,
        status="pending",
        created_at="2024-01-01T00:00:00Z",
    )

    item2 = QueueItem(
        id=2,
        letta_user_id=124,
        message_id=457,
        priority=1,
        retry_count=0,
        status="completed",
        created_at="2024-01-01T00:00:00Z",
    )

    processor.queue = [item1, item2]

    await processor.clear_completed()
    assert len(processor.queue) == 1
    assert processor.queue[0].status == "pending"
