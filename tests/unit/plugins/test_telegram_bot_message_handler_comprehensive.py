"""Comprehensive tests for plugins/telegram_bot/message_handler.py."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from plugins.telegram_bot.message_handler import TelegramMessageHandler


class TestTelegramMessageHandler:
    """Test cases for TelegramMessageHandler class."""

    def test_initialization(self):
        """Test TelegramMessageHandler initialization."""
        handler = TelegramMessageHandler()
        assert handler.formatter is not None
        assert handler.letta_client is None

    @pytest.mark.asyncio
    async def test_process_incoming_message_success(self):
        """Test successful processing of incoming message."""
        handler = TelegramMessageHandler()
        
        # Mock message object
        mock_message = MagicMock()
        mock_message.from_user.id = 123
        mock_message.from_user.username = "testuser"
        mock_message.from_user.first_name = "Test User"
        mock_message.date = datetime.now()
        mock_message.text = "Hello world"
        
        # Mock formatter
        handler.formatter.sanitize_text.side_effect = lambda x: x if x else "Unknown"
        
        # Mock database operations
        mock_profile = MagicMock()
        mock_profile.id = "profile_123"
        mock_letta_user = MagicMock()
        mock_letta_user.id = "letta_123"
        
        with patch('plugins.telegram_bot.message_handler.get_or_create_platform_profile', new_callable=AsyncMock) as mock_get_profile:
            mock_get_profile.return_value = (mock_profile, mock_letta_user)
            
            with patch('plugins.telegram_bot.message_handler.insert_message', new_callable=AsyncMock) as mock_insert:
                mock_insert.return_value = "message_123"
                
                with patch('plugins.telegram_bot.message_handler.add_to_queue', new_callable=AsyncMock) as mock_add_queue:
                    result = await handler.process_incoming_message(mock_message)
                    
                    # Verify calls
                    mock_get_profile.assert_called_once_with(
                        platform="telegram",
                        platform_user_id="123",
                        username="testuser",
                        display_name="Test User"
                    )
                    
                    mock_insert.assert_called_once()
                    mock_add_queue.assert_called_once_with("letta_123", "message_123")
                    
                    # Verify result
                    assert result["message_id"] == "message_123"
                    assert result["letta_user_id"] == "letta_123"
                    assert result["platform_profile_id"] == "profile_123"
                    assert result["user_id"] == 123
                    assert result["username"] == "testuser"
                    assert result["first_name"] == "Test User"

    @pytest.mark.asyncio
    async def test_process_incoming_message_no_username(self):
        """Test processing message with no username."""
        handler = TelegramMessageHandler()
        
        # Mock message object
        mock_message = MagicMock()
        mock_message.from_user.id = 123
        mock_message.from_user.username = None
        mock_message.from_user.first_name = "Test User"
        mock_message.date = datetime.now()
        mock_message.text = "Hello world"
        
        # Mock formatter
        handler.formatter.sanitize_text.side_effect = lambda x: x if x else "Unknown"
        
        # Mock database operations
        mock_profile = MagicMock()
        mock_profile.id = "profile_123"
        mock_letta_user = MagicMock()
        mock_letta_user.id = "letta_123"
        
        with patch('plugins.telegram_bot.message_handler.get_or_create_platform_profile', new_callable=AsyncMock) as mock_get_profile:
            mock_get_profile.return_value = (mock_profile, mock_letta_user)
            
            with patch('plugins.telegram_bot.message_handler.insert_message', new_callable=AsyncMock) as mock_insert:
                mock_insert.return_value = "message_123"
                
                with patch('plugins.telegram_bot.message_handler.add_to_queue', new_callable=AsyncMock):
                    result = await handler.process_incoming_message(mock_message)
                    
                    mock_get_profile.assert_called_once_with(
                        platform="telegram",
                        platform_user_id="123",
                        username=None,
                        display_name="Test User"
                    )

    @pytest.mark.asyncio
    async def test_process_incoming_message_no_first_name(self):
        """Test processing message with no first name."""
        handler = TelegramMessageHandler()
        
        # Mock message object
        mock_message = MagicMock()
        mock_message.from_user.id = 123
        mock_message.from_user.username = "testuser"
        mock_message.from_user.first_name = None
        mock_message.date = datetime.now()
        mock_message.text = "Hello world"
        
        # Mock formatter
        handler.formatter.sanitize_text.side_effect = lambda x: x if x else "Unknown"
        
        # Mock database operations
        mock_profile = MagicMock()
        mock_profile.id = "profile_123"
        mock_letta_user = MagicMock()
        mock_letta_user.id = "letta_123"
        
        with patch('plugins.telegram_bot.message_handler.get_or_create_platform_profile', new_callable=AsyncMock) as mock_get_profile:
            mock_get_profile.return_value = (mock_profile, mock_letta_user)
            
            with patch('plugins.telegram_bot.message_handler.insert_message', new_callable=AsyncMock) as mock_insert:
                mock_insert.return_value = "message_123"
                
                with patch('plugins.telegram_bot.message_handler.add_to_queue', new_callable=AsyncMock):
                    result = await handler.process_incoming_message(mock_message)
                    
                    mock_get_profile.assert_called_once_with(
                        platform="telegram",
                        platform_user_id="123",
                        username="testuser",
                        display_name="Unknown"
                    )

    @pytest.mark.asyncio
    async def test_process_incoming_message_exception(self):
        """Test processing message with exception."""
        handler = TelegramMessageHandler()
        
        # Mock message object
        mock_message = MagicMock()
        mock_message.from_user.id = 123
        mock_message.from_user.username = "testuser"
        mock_message.from_user.first_name = "Test User"
        mock_message.date = datetime.now()
        mock_message.text = "Hello world"
        
        # Mock formatter
        handler.formatter.sanitize_text.side_effect = lambda x: x if x else "Unknown"
        
        # Mock database operations to raise exception
        with patch('plugins.telegram_bot.message_handler.get_or_create_platform_profile', new_callable=AsyncMock) as mock_get_profile:
            mock_get_profile.side_effect = Exception("Database error")
            
            with pytest.raises(Exception, match="Database error"):
                await handler.process_incoming_message(mock_message)

    @pytest.mark.asyncio
    async def test_process_outgoing_message_success(self):
        """Test successful processing of outgoing message."""
        handler = TelegramMessageHandler()
        
        # Mock message object
        mock_message = MagicMock()
        mock_message.answer = AsyncMock()
        
        with patch.object(handler, 'update_message_status', new_callable=AsyncMock) as mock_update:
            await handler.process_outgoing_message(mock_message, "Test response")
            
            mock_message.answer.assert_called_once_with("Test response")
            mock_update.assert_called_once_with(mock_message, "sent")

    @pytest.mark.asyncio
    async def test_process_outgoing_message_exception(self):
        """Test processing outgoing message with exception."""
        handler = TelegramMessageHandler()
        
        # Mock message object
        mock_message = MagicMock()
        mock_message.answer.side_effect = Exception("Send error")
        
        with pytest.raises(Exception, match="Send error"):
            await handler.process_outgoing_message(mock_message, "Test response")

    @pytest.mark.asyncio
    async def test_update_message_status_with_letta_client_initialization(self):
        """Test update_message_status with letta_client initialization."""
        handler = TelegramMessageHandler()
        
        # Mock message object
        mock_message = MagicMock()
        mock_message.message_id = "msg_123"
        
        # Mock letta_client
        mock_letta_client = AsyncMock()
        mock_letta_client.update_message_status = AsyncMock()
        
        with patch('plugins.telegram_bot.message_handler.LettaClient', return_value=mock_letta_client):
            await handler.update_message_status(mock_message, "sent")
            
            mock_letta_client.update_message_status.assert_called_once_with(
                message_id="msg_123", status="sent"
            )
            assert handler.letta_client == mock_letta_client

    @pytest.mark.asyncio
    async def test_update_message_status_with_existing_letta_client(self):
        """Test update_message_status with existing letta_client."""
        handler = TelegramMessageHandler()
        
        # Mock message object
        mock_message = MagicMock()
        mock_message.message_id = "msg_123"
        
        # Mock letta_client
        mock_letta_client = AsyncMock()
        mock_letta_client.update_message_status = AsyncMock()
        handler.letta_client = mock_letta_client
        
        await handler.update_message_status(mock_message, "sent")
        
        mock_letta_client.update_message_status.assert_called_once_with(
            message_id="msg_123", status="sent"
        )

    @pytest.mark.asyncio
    async def test_update_message_status_import_error(self):
        """Test update_message_status with ImportError."""
        handler = TelegramMessageHandler()
        
        # Mock message object
        mock_message = MagicMock()
        mock_message.message_id = "msg_123"
        
        with patch('plugins.telegram_bot.message_handler.LettaClient', side_effect=ImportError("Module not found")):
            with pytest.raises(ImportError, match="Module not found"):
                await handler.update_message_status(mock_message, "sent")

    @pytest.mark.asyncio
    async def test_update_message_status_general_exception(self):
        """Test update_message_status with general exception."""
        handler = TelegramMessageHandler()
        
        # Mock message object
        mock_message = MagicMock()
        mock_message.message_id = "msg_123"
        
        # Mock letta_client
        mock_letta_client = AsyncMock()
        mock_letta_client.update_message_status.side_effect = Exception("Update error")
        
        with patch('plugins.telegram_bot.message_handler.LettaClient', return_value=mock_letta_client):
            with pytest.raises(Exception, match="Update error"):
                await handler.update_message_status(mock_message, "sent")

    @pytest.mark.asyncio
    async def test_handle_private_message(self):
        """Test handle_private_message delegates to process_incoming_message."""
        handler = TelegramMessageHandler()
        
        mock_message = MagicMock()
        
        with patch.object(handler, 'process_incoming_message', new_callable=AsyncMock) as mock_process:
            await handler.handle_private_message(mock_message)
            mock_process.assert_called_once_with(mock_message)

    @pytest.mark.asyncio
    async def test_handle_group_message(self):
        """Test handle_group_message sends not supported message."""
        handler = TelegramMessageHandler()
        
        mock_message = MagicMock()
        mock_message.answer = AsyncMock()
        
        await handler.handle_group_message(mock_message)
        mock_message.answer.assert_called_once_with("Group messages are not supported")

    @pytest.mark.asyncio
    async def test_handle_channel_message(self):
        """Test handle_channel_message sends not supported message."""
        handler = TelegramMessageHandler()
        
        mock_message = MagicMock()
        mock_message.answer = AsyncMock()
        
        await handler.handle_channel_message(mock_message)
        mock_message.answer.assert_called_once_with("Channel messages are not supported")

    def test_format_message(self):
        """Test format_message delegates to formatter."""
        handler = TelegramMessageHandler()
        
        handler.formatter.format_message.return_value = "formatted message"
        
        result = handler.format_message("test message")
        
        handler.formatter.format_message.assert_called_once_with("test message")
        assert result == "formatted message"

    @pytest.mark.asyncio
    async def test_process_incoming_message_sanitizes_input(self):
        """Test that process_incoming_message sanitizes user input."""
        handler = TelegramMessageHandler()
        
        # Mock message object
        mock_message = MagicMock()
        mock_message.from_user.id = 123
        mock_message.from_user.username = "testuser"
        mock_message.from_user.first_name = "Test User"
        mock_message.date = datetime.now()
        mock_message.text = "Hello world"
        
        # Mock formatter
        handler.formatter.sanitize_text.side_effect = lambda x: f"sanitized_{x}" if x else "Unknown"
        
        # Mock database operations
        mock_profile = MagicMock()
        mock_profile.id = "profile_123"
        mock_letta_user = MagicMock()
        mock_letta_user.id = "letta_123"
        
        with patch('plugins.telegram_bot.message_handler.get_or_create_platform_profile', new_callable=AsyncMock) as mock_get_profile:
            mock_get_profile.return_value = (mock_profile, mock_letta_user)
            
            with patch('plugins.telegram_bot.message_handler.insert_message', new_callable=AsyncMock) as mock_insert:
                mock_insert.return_value = "message_123"
                
                with patch('plugins.telegram_bot.message_handler.add_to_queue', new_callable=AsyncMock):
                    await handler.process_incoming_message(mock_message)
                    
                    # Verify sanitize_text was called
                    assert handler.formatter.sanitize_text.call_count >= 3
                    
                    # Verify insert_message was called with sanitized message
                    call_args = mock_insert.call_args
                    assert call_args[1]["message"] == "sanitized_Hello world"

    @pytest.mark.asyncio
    async def test_process_incoming_message_timestamp_formatting(self):
        """Test that process_incoming_message formats timestamp correctly."""
        handler = TelegramMessageHandler()
        
        # Mock message object
        test_date = datetime(2023, 12, 25, 15, 30, 45)
        mock_message = MagicMock()
        mock_message.from_user.id = 123
        mock_message.from_user.username = "testuser"
        mock_message.from_user.first_name = "Test User"
        mock_message.date = test_date
        mock_message.text = "Hello world"
        
        # Mock formatter
        handler.formatter.sanitize_text.side_effect = lambda x: x if x else "Unknown"
        
        # Mock database operations
        mock_profile = MagicMock()
        mock_profile.id = "profile_123"
        mock_letta_user = MagicMock()
        mock_letta_user.id = "letta_123"
        
        with patch('plugins.telegram_bot.message_handler.get_or_create_platform_profile', new_callable=AsyncMock) as mock_get_profile:
            mock_get_profile.return_value = (mock_profile, mock_letta_user)
            
            with patch('plugins.telegram_bot.message_handler.insert_message', new_callable=AsyncMock) as mock_insert:
                mock_insert.return_value = "message_123"
                
                with patch('plugins.telegram_bot.message_handler.add_to_queue', new_callable=AsyncMock):
                    await handler.process_incoming_message(mock_message)
                    
                    # Verify timestamp formatting
                    call_args = mock_insert.call_args
                    assert call_args[1]["timestamp"] == "2023-12-25 15:30 UTC"
