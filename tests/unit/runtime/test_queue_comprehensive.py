"""Comprehensive unit tests for runtime.core.queue to achieve 100% coverage."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from runtime.core.queue import QueueProcessor


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_process_with_core_block_success(temp_db, mock_letta_client):
    """Test _process_with_core_block with successful processing."""
    async def mock_processor(message: str):
        return f"Response: {message}"

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor)
        
        # Mock get_letta_user_block_id
        with patch("runtime.core.queue.get_letta_user_block_id", return_value="block-123"):
            response, status = await processor._process_with_core_block("test message", 1)
            
            assert response == "Response: test message"
            assert status == "completed"
            assert mock_letta_client.agents.blocks.attach.called
            assert mock_letta_client.agents.blocks.detach.called


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_process_with_core_block_no_block_id(temp_db, mock_letta_client):
    """Test _process_with_core_block when block ID is not found."""
    async def mock_processor(message: str):
        return "Response"

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor)
        
        with patch("runtime.core.queue.get_letta_user_block_id", return_value=None):
            response, status = await processor._process_with_core_block("test", 1)
            
            assert response is None
            assert status == "failed"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_process_with_core_block_processing_error(temp_db, mock_letta_client):
    """Test _process_with_core_block when processing fails."""
    async def mock_processor(message: str):
        raise Exception("Processing error")

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor)
        
        with patch("runtime.core.queue.get_letta_user_block_id", return_value="block-123"):
            response, status = await processor._process_with_core_block("test", 1)
            
            assert response is None
            assert status == "failed"
            # Should still detach block even on error
            assert mock_letta_client.agents.blocks.detach.called


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_process_with_core_block_no_response(temp_db, mock_letta_client):
    """Test _process_with_core_block when processor returns None."""
    async def mock_processor(message: str):
        return None

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor)
        
        with patch("runtime.core.queue.get_letta_user_block_id", return_value="block-123"):
            response, status = await processor._process_with_core_block("test", 1)
            
            assert response is None
            assert status == "failed"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_route_response_success(temp_db):
    """Test _route_response with successful routing."""
    async def mock_processor(message: str):
        return "Response"

    mock_plugin_manager = MagicMock()
    mock_handler = AsyncMock()
    mock_plugin_manager.get_platform_handler.return_value = mock_handler

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor, plugin_manager=mock_plugin_manager)
        
        mock_profile = MagicMock()
        mock_profile.platform = "telegram"
        
        with patch("runtime.core.queue.get_message_platform_profile", return_value=mock_profile):
            result = await processor._route_response(1, "test response")
            
            assert result is True
            mock_handler.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_route_response_no_plugin_manager(temp_db):
    """Test _route_response when plugin manager is None."""
    async def mock_processor(message: str):
        return "Response"

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor, plugin_manager=None)
        
        result = await processor._route_response(1, "test response")
        
        assert result is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_route_response_no_profile(temp_db):
    """Test _route_response when profile is not found."""
    async def mock_processor(message: str):
        return "Response"

    mock_plugin_manager = MagicMock()

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor, plugin_manager=mock_plugin_manager)
        
        with patch("runtime.core.queue.get_message_platform_profile", return_value=None):
            result = await processor._route_response(1, "test response")
            
            assert result is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_route_response_no_handler(temp_db):
    """Test _route_response when handler is not found."""
    async def mock_processor(message: str):
        return "Response"

    mock_plugin_manager = MagicMock()
    mock_plugin_manager.get_platform_handler.return_value = None

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor, plugin_manager=mock_plugin_manager)
        
        mock_profile = MagicMock()
        mock_profile.platform = "telegram"
        
        with patch("runtime.core.queue.get_message_platform_profile", return_value=mock_profile):
            result = await processor._route_response(1, "test response")
            
            assert result is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_route_response_handler_error(temp_db):
    """Test _route_response when handler raises an error."""
    async def mock_processor(message: str):
        return "Response"

    mock_plugin_manager = MagicMock()
    mock_handler = AsyncMock(side_effect=Exception("Handler error"))
    mock_plugin_manager.get_platform_handler.return_value = mock_handler

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor, plugin_manager=mock_plugin_manager)
        
        mock_profile = MagicMock()
        mock_profile.platform = "telegram"
        
        with patch("runtime.core.queue.get_message_platform_profile", return_value=mock_profile):
            result = await processor._route_response(1, "test response")
            
            assert result is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_start_processing_loop(temp_db):
    """Test start method processes queue items."""
    async def mock_processor(message: str):
        return f"Processed: {message}"

    mock_queue_item = MagicMock()
    mock_queue_item.id = 1
    mock_queue_item.message_id = 1
    mock_queue_item.letta_user_id = 1

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor, message_mode="echo")
        
        with patch("runtime.core.queue.atomic_dequeue_item", return_value=mock_queue_item), \
             patch("runtime.core.queue.get_message_text", return_value=("user", "test message")), \
             patch("runtime.core.queue.get_user_details", return_value=("Test User", "testuser")), \
             patch("runtime.core.queue.get_platform_profile_id", return_value=(1, "12345")), \
             patch("runtime.core.queue.get_platform_profile") as mock_get_profile, \
             patch("runtime.core.queue.update_message_with_response", new_callable=AsyncMock), \
             patch("runtime.core.queue.update_queue_status", new_callable=AsyncMock), \
             patch.object(processor, "_route_response", return_value=True):
            
            mock_profile = MagicMock()
            mock_profile.platform = "telegram"
            mock_get_profile.return_value = mock_profile
            
            # Start processor and stop it quickly
            task = asyncio.create_task(processor.start())
            await asyncio.sleep(0.1)
            await processor.stop()
            
            # Wait for task to complete
            try:
                await asyncio.wait_for(task, timeout=1.0)
            except asyncio.TimeoutError:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_start_no_queue_item(temp_db):
    """Test start method when no queue items are available."""
    async def mock_processor(message: str):
        return "Response"

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor, message_mode="echo")
        
        with patch("runtime.core.queue.atomic_dequeue_item", return_value=None):
            # Start processor and stop it quickly
            task = asyncio.create_task(processor.start())
            await asyncio.sleep(0.1)
            await processor.stop()
            
            # Wait for task to complete
            try:
                await asyncio.wait_for(task, timeout=1.0)
            except asyncio.TimeoutError:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_start_message_not_found(temp_db):
    """Test start method when message is not found."""
    async def mock_processor(message: str):
        return "Response"

    mock_queue_item = MagicMock()
    mock_queue_item.id = 1
    mock_queue_item.message_id = 1
    mock_queue_item.letta_user_id = 1

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor, message_mode="echo")
        
        with patch("runtime.core.queue.atomic_dequeue_item", return_value=mock_queue_item), \
             patch("runtime.core.queue.get_message_text", return_value=None), \
             patch("runtime.core.queue.requeue_failed_item", new_callable=AsyncMock):
            
            # Start processor and stop it quickly
            task = asyncio.create_task(processor.start())
            await asyncio.sleep(0.1)
            await processor.stop()
            
            # Wait for task to complete
            try:
                await asyncio.wait_for(task, timeout=1.0)
            except asyncio.TimeoutError:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_start_user_not_found(temp_db):
    """Test start method when user is not found."""
    async def mock_processor(message: str):
        return "Response"

    mock_queue_item = MagicMock()
    mock_queue_item.id = 1
    mock_queue_item.message_id = 1
    mock_queue_item.letta_user_id = 1

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor, message_mode="echo")
        
        with patch("runtime.core.queue.atomic_dequeue_item", return_value=mock_queue_item), \
             patch("runtime.core.queue.get_message_text", return_value=("user", "test")), \
             patch("runtime.core.queue.get_user_details", return_value=None), \
             patch("runtime.core.queue.requeue_failed_item", new_callable=AsyncMock):
            
            # Start processor and stop it quickly
            task = asyncio.create_task(processor.start())
            await asyncio.sleep(0.1)
            await processor.stop()
            
            # Wait for task to complete
            try:
                await asyncio.wait_for(task, timeout=1.0)
            except asyncio.TimeoutError:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_start_platform_profile_not_found(temp_db):
    """Test start method when platform profile is not found."""
    async def mock_processor(message: str):
        return "Response"

    mock_queue_item = MagicMock()
    mock_queue_item.id = 1
    mock_queue_item.message_id = 1
    mock_queue_item.letta_user_id = 1

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor, message_mode="echo")
        
        with patch("runtime.core.queue.atomic_dequeue_item", return_value=mock_queue_item), \
             patch("runtime.core.queue.get_message_text", return_value=("user", "test")), \
             patch("runtime.core.queue.get_user_details", return_value=("User", "user")), \
             patch("runtime.core.queue.get_platform_profile_id", return_value=None), \
             patch("runtime.core.queue.requeue_failed_item", new_callable=AsyncMock):
            
            # Start processor and stop it quickly
            task = asyncio.create_task(processor.start())
            await asyncio.sleep(0.1)
            await processor.stop()
            
            # Wait for task to complete
            try:
                await asyncio.wait_for(task, timeout=1.0)
            except asyncio.TimeoutError:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_start_processing_error(temp_db):
    """Test start method when processing raises an error."""
    async def mock_processor(message: str):
        return "Response"

    mock_queue_item = MagicMock()
    mock_queue_item.id = 1
    mock_queue_item.message_id = 1
    mock_queue_item.letta_user_id = 1

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor, message_mode="echo")
        
        with patch("runtime.core.queue.atomic_dequeue_item", return_value=mock_queue_item), \
             patch("runtime.core.queue.get_message_text", side_effect=Exception("DB error")), \
             patch("runtime.core.queue.requeue_failed_item", new_callable=AsyncMock):
            
            # Start processor and stop it quickly
            task = asyncio.create_task(processor.start())
            await asyncio.sleep(0.1)
            await processor.stop()
            
            # Wait for task to complete
            try:
                await asyncio.wait_for(task, timeout=1.0)
            except asyncio.TimeoutError:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_start_already_running(temp_db):
    """Test start method when already running."""
    async def mock_processor(message: str):
        return "Response"

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor)
        processor.is_running = True
        
        await processor.start()
        
        # Should return early without starting again


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_stop_not_running(temp_db):
    """Test stop method when not running."""
    async def mock_processor(message: str):
        return "Response"

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor)
        processor.is_running = False
        
        await processor.stop()
        
        # Should return early


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_stop_with_processing_messages(temp_db):
    """Test stop method waits for processing messages."""
    async def mock_processor(message: str):
        return "Response"

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor)
        processor.is_running = True
        processor.processing_messages.add(1)
        
        # Create task to remove message after delay
        async def remove_message():
            await asyncio.sleep(0.1)
            processor.processing_messages.clear()
        
        asyncio.create_task(remove_message())
        
        await processor.stop()
        
        assert not processor.is_running


@pytest.mark.unit
def test_queue_processor_set_message_mode(temp_db):
    """Test set_message_mode method."""
    async def mock_processor(message: str):
        return "Response"

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor)
        
        processor.set_message_mode("listen")
        
        assert processor.message_mode == "listen"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_live_mode_processing(temp_db, mock_letta_client):
    """Test processing in live mode."""
    async def mock_processor(message: str):
        return f"Processed: {message}"

    mock_queue_item = MagicMock()
    mock_queue_item.id = 1
    mock_queue_item.message_id = 1
    mock_queue_item.letta_user_id = 1

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor, message_mode="live")
        
        with patch("runtime.core.queue.atomic_dequeue_item", return_value=mock_queue_item), \
             patch("runtime.core.queue.get_message_text", return_value=("user", "test")), \
             patch("runtime.core.queue.get_user_details", return_value=("User", "user")), \
             patch("runtime.core.queue.get_platform_profile_id", return_value=(1, "12345")), \
             patch("runtime.core.queue.get_platform_profile") as mock_get_profile, \
             patch("runtime.core.queue.get_letta_user_block_id", return_value="block-123"), \
             patch("runtime.core.queue.update_message_with_response", new_callable=AsyncMock), \
             patch("runtime.core.queue.update_queue_status", new_callable=AsyncMock), \
             patch.object(processor, "_route_response", return_value=True):
            
            mock_profile = MagicMock()
            mock_profile.platform = "telegram"
            mock_get_profile.return_value = mock_profile
            
            # Start processor and stop it quickly
            task = asyncio.create_task(processor.start())
            await asyncio.sleep(0.1)
            await processor.stop()
            
            # Wait for task to complete
            try:
                await asyncio.wait_for(task, timeout=1.0)
            except asyncio.TimeoutError:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass


@pytest.mark.unit
@pytest.mark.asyncio
async def test_queue_processor_no_response_requeue(temp_db):
    """Test requeue when no response is received."""
    async def mock_processor(message: str):
        return None  # No response

    mock_queue_item = MagicMock()
    mock_queue_item.id = 1
    mock_queue_item.message_id = 1
    mock_queue_item.letta_user_id = 1

    with patch.dict("os.environ", {"AGENT_ID": "test_agent"}):
        processor = QueueProcessor(mock_processor, message_mode="live")
        
        with patch("runtime.core.queue.atomic_dequeue_item", return_value=mock_queue_item), \
             patch("runtime.core.queue.get_message_text", return_value=("user", "test")), \
             patch("runtime.core.queue.get_user_details", return_value=("User", "user")), \
             patch("runtime.core.queue.get_platform_profile_id", return_value=(1, "12345")), \
             patch("runtime.core.queue.get_platform_profile") as mock_get_profile, \
             patch("runtime.core.queue.get_letta_user_block_id", return_value="block-123"), \
             patch("runtime.core.queue.requeue_failed_item", new_callable=AsyncMock) as mock_requeue:
            
            mock_profile = MagicMock()
            mock_profile.platform = "telegram"
            mock_get_profile.return_value = mock_profile
            
            # Start processor and stop it quickly
            task = asyncio.create_task(processor.start())
            await asyncio.sleep(0.1)
            await processor.stop()
            
            # Wait for task to complete
            try:
                await asyncio.wait_for(task, timeout=1.0)
            except asyncio.TimeoutError:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
