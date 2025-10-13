"""Extended unit tests for runtime queue processor."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from runtime.core.queue import QueueProcessor


class TestQueueProcessorExtended:
    """Extended test cases for QueueProcessor."""

    @patch("runtime.core.queue.get_env_var")
    def test_queue_processor_initialization(self, mock_get_env_var):
        """Test queue processor initialization."""
        mock_get_env_var.return_value = "test-agent"
        message_processor = MagicMock()

        processor = QueueProcessor(
            message_processor=message_processor,
            message_mode="echo",
            plugin_manager=None,
            telegram_client=None,
            on_message_processed=None,
        )

        assert processor is not None
        assert processor.message_processor == message_processor
        assert processor.message_mode == "echo"
        assert not processor.is_running

    @patch("runtime.core.queue.get_env_var")
    @pytest.mark.asyncio
    async def test_queue_processor_start(self, mock_get_env_var):
        """Test starting queue processor."""
        mock_get_env_var.return_value = "test-agent"
        message_processor = MagicMock()

        processor = QueueProcessor(
            message_processor=message_processor, message_mode="echo"
        )

        with patch("runtime.core.queue.atomic_dequeue_item") as mock_dequeue:
            mock_dequeue.return_value = None  # No items to process

            # Start the processor in a task
            task = asyncio.create_task(processor.start())

            # Let it run briefly
            await asyncio.sleep(0.1)

            # Stop it
            await processor.stop()
            task.cancel()

            assert processor.is_running is False

    @patch("runtime.core.queue.get_env_var")
    @pytest.mark.asyncio
    async def test_queue_processor_stop(self, mock_get_env_var):
        """Test stopping queue processor."""
        mock_get_env_var.return_value = "test-agent"
        message_processor = MagicMock()

        processor = QueueProcessor(
            message_processor=message_processor, message_mode="echo"
        )

        processor.is_running = True

        await processor.stop()

        assert not processor.is_running

    @patch("runtime.core.queue.get_env_var")
    @pytest.mark.asyncio
    async def test_queue_processor_process_item_echo_mode(self, mock_get_env_var):
        """Test processing item in echo mode."""
        mock_get_env_var.return_value = "test-agent"
        message_processor = MagicMock()

        processor = QueueProcessor(
            message_processor=message_processor, message_mode="echo"
        )

        with patch("runtime.core.queue.atomic_dequeue_item") as mock_dequeue:
            with patch("runtime.core.queue.get_message_text") as mock_get_text:
                with patch("runtime.core.queue.get_user_details") as mock_get_user:
                    with patch(
                        "runtime.core.queue.get_platform_profile_id"
                    ) as mock_get_profile:
                        with patch(
                            "runtime.core.queue.update_message_with_response"
                        ) as mock_update_msg:
                            with patch(
                                "runtime.core.queue.update_queue_status"
                            ) as mock_update_queue:
                                with patch(
                                    "runtime.core.queue.get_platform_profile"
                                ) as mock_get_platform:
                                    # Mock queue item
                                    mock_item = MagicMock()
                                    mock_item.id = 1
                                    mock_item.message_id = 1
                                    mock_item.letta_user_id = 1
                                    mock_dequeue.return_value = mock_item

                                    # Mock message data
                                    mock_get_text.return_value = (
                                        "user",
                                        "Test message",
                                    )

                                    # Mock user data
                                    mock_get_user.return_value = (
                                        "Test User",
                                        "testuser",
                                    )

                                    # Mock platform profile
                                    mock_get_profile.return_value = (
                                        1,
                                        "platform_user_id",
                                    )
                                    mock_platform_profile = MagicMock()
                                    mock_platform_profile.platform = "telegram"
                                    mock_get_platform.return_value = (
                                        mock_platform_profile
                                    )

                                    # Start processor
                                    task = asyncio.create_task(processor.start())

                                    # Let it process one item
                                    await asyncio.sleep(0.1)

                                    # Stop processor
                                    await processor.stop()
                                    task.cancel()

                                    # Verify echo mode behavior
                                    mock_update_msg.assert_called_once()
                                    mock_update_queue.assert_called_once()

    @patch("runtime.core.queue.get_env_var")
    def test_set_message_mode(self, mock_get_env_var):
        """Test setting message mode."""
        mock_get_env_var.return_value = "test-agent"
        message_processor = MagicMock()

        processor = QueueProcessor(
            message_processor=message_processor, message_mode="echo"
        )

        processor.set_message_mode("live")

        assert processor.message_mode == "live"

    @patch("runtime.core.queue.get_env_var")
    @pytest.mark.asyncio
    async def test_route_response(self, mock_get_env_var):
        """Test routing response through platform handler."""
        mock_get_env_var.return_value = "test-agent"
        message_processor = MagicMock()
        plugin_manager = MagicMock()
        handler = AsyncMock()

        processor = QueueProcessor(
            message_processor=message_processor, plugin_manager=plugin_manager
        )

        with patch(
            "runtime.core.queue.get_message_platform_profile"
        ) as mock_get_profile:
            mock_profile = MagicMock()
            mock_profile.platform = "telegram"
            mock_get_profile.return_value = mock_profile

            plugin_manager.get_platform_handler.return_value = handler

            result = await processor._route_response(1, "Test response")

            assert result is True
            handler.assert_called_once_with("Test response", mock_profile, 1)

    @patch("runtime.core.queue.get_env_var")
    @pytest.mark.asyncio
    async def test_route_response_no_handler(self, mock_get_env_var):
        """Test routing response when no handler is available."""
        mock_get_env_var.return_value = "test-agent"
        message_processor = MagicMock()
        plugin_manager = MagicMock()

        processor = QueueProcessor(
            message_processor=message_processor, plugin_manager=plugin_manager
        )

        with patch(
            "runtime.core.queue.get_message_platform_profile"
        ) as mock_get_profile:
            mock_profile = MagicMock()
            mock_profile.platform = "telegram"
            mock_get_profile.return_value = mock_profile

            plugin_manager.get_platform_handler.return_value = None

            result = await processor._route_response(1, "Test response")

            assert result is False

    @patch("runtime.core.queue.get_env_var")
    @pytest.mark.asyncio
    async def test_process_with_core_block(self, mock_get_env_var):
        """Test processing with core block."""
        mock_get_env_var.return_value = "test-agent"
        message_processor = AsyncMock(return_value="Processed response")

        processor = QueueProcessor(
            message_processor=message_processor, message_mode="live"
        )

        with patch("runtime.core.queue.get_letta_user_block_id") as mock_get_block:
            with patch("runtime.core.queue.get_letta_client") as mock_get_client:
                mock_get_block.return_value = "block123"

                mock_client = MagicMock()
                mock_get_client.return_value = mock_client

                response, status = await processor._process_with_core_block(
                    "Test message", 1
                )

                assert response == "Processed response"
                assert status == "completed"
                message_processor.assert_called_once_with("Test message")

    @patch("runtime.core.queue.get_env_var")
    @pytest.mark.asyncio
    async def test_process_with_core_block_no_block_id(self, mock_get_env_var):
        """Test processing when no block ID is available."""
        mock_get_env_var.return_value = "test-agent"
        message_processor = AsyncMock()

        processor = QueueProcessor(
            message_processor=message_processor, message_mode="live"
        )

        with patch("runtime.core.queue.get_letta_user_block_id") as mock_get_block:
            mock_get_block.return_value = None

            response, status = await processor._process_with_core_block(
                "Test message", 1
            )

            assert response is None
            assert status == "failed"
            message_processor.assert_not_called()
