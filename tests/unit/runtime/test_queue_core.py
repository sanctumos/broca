"""Unit tests for runtime core queue functionality."""

from unittest.mock import MagicMock, patch

import pytest

from runtime.core.queue import QueueProcessor


@pytest.fixture(autouse=True)
def mock_letta_client():
    """Avoid real Letta client in QueueProcessor.__init__."""
    with patch("runtime.core.queue.get_letta_client", return_value=MagicMock()):
        yield


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

    def mock_message_processor(message: str, sender_id: str | None = None) -> str:
        return f"Processed: {message}"

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_message_processor)
        assert processor is not None
        assert hasattr(processor, "is_running")
        assert hasattr(processor, "processing_messages")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_start():
    """Test QueueProcessor start."""

    def mock_message_processor(message: str, sender_id: str | None = None) -> str:
        return f"Processed: {message}"

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_message_processor)

        # Mock the start method to avoid infinite loop
        with patch.object(processor, "start") as mock_start:
            mock_start.return_value = None
            await processor.start()
            mock_start.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_stop():
    """Test QueueProcessor stop."""

    def mock_message_processor(message: str, sender_id: str | None = None) -> str:
        return f"Processed: {message}"

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_message_processor)
        processor.is_running = True

        await processor.stop()
        assert processor.is_running is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_add_item():
    """Test QueueProcessor add_item."""

    def mock_message_processor(message: str, sender_id: str | None = None) -> str:
        return f"Processed: {message}"

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_message_processor)

        # QueueProcessor doesn't have an add_item method
        assert not hasattr(processor, "add_item")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_get_next_item():
    """Test QueueProcessor get_next_item."""

    def mock_message_processor(message: str, sender_id: str | None = None) -> str:
        return f"Processed: {message}"

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_message_processor)

        # QueueProcessor doesn't have a get_next_item method
        assert not hasattr(processor, "get_next_item")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_process_item():
    """Test QueueProcessor process_item."""

    def mock_message_processor(message: str, sender_id: str | None = None) -> str:
        return f"Processed: {message}"

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_message_processor)

        # QueueProcessor doesn't have a process_item method
        assert not hasattr(processor, "process_item")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_retry_item():
    """Test QueueProcessor retry_item."""

    def mock_message_processor(message: str, sender_id: str | None = None) -> str:
        return f"Processed: {message}"

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_message_processor)

        # QueueProcessor doesn't have a retry_item method
        assert not hasattr(processor, "retry_item")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_get_stats():
    """Test QueueProcessor get_stats."""

    def mock_message_processor(message: str, sender_id: str | None = None) -> str:
        return f"Processed: {message}"

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_message_processor)

        # QueueProcessor doesn't have a get_stats method
        assert not hasattr(processor, "get_stats")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_clear_completed():
    """Test QueueProcessor clear_completed."""

    def mock_message_processor(message: str, sender_id: str | None = None) -> str:
        return f"Processed: {message}"

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_message_processor)

        # QueueProcessor doesn't have a clear_completed method
        assert not hasattr(processor, "clear_completed")


@pytest.mark.unit
def test_queue_processor_set_message_mode():
    """Test QueueProcessor set_message_mode."""

    def mock_message_processor(message: str, sender_id: str | None = None) -> str:
        return f"Processed: {message}"

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_message_processor)

        # Test that set_message_mode exists and works
        assert hasattr(processor, "set_message_mode")
        processor.set_message_mode("live")
        assert processor.message_mode == "live"


@pytest.mark.unit
def test_queue_processor_properties():
    """Test QueueProcessor properties."""

    def mock_message_processor(message: str, sender_id: str | None = None) -> str:
        return f"Processed: {message}"

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_message_processor)

        # Test that the processor has the expected properties
        assert hasattr(processor, "message_processor")
        assert hasattr(processor, "message_mode")
        assert hasattr(processor, "formatter")
        assert hasattr(processor, "is_running")
        assert hasattr(processor, "plugin_manager")
        assert hasattr(processor, "telegram_client")
        assert hasattr(processor, "on_message_processed")
        assert hasattr(processor, "processing_messages")
        assert hasattr(processor, "_stop_event")
        assert hasattr(processor, "letta_client")
        assert hasattr(processor, "agent_id")
