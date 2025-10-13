"""Additional comprehensive tests for runtime core components."""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from runtime.core.agent import AgentClient
from runtime.core.plugin import PluginManager
from runtime.core.queue import QueueProcessor
from runtime.core.message import Message


class TestRuntimeCoreComprehensive:
    """Comprehensive test cases for runtime core components."""

    # AgentClient Tests
    def test_agent_client_initialization_default(self):
        """Test AgentClient initialization with default settings."""
        agent = AgentClient()
        assert agent is not None
        assert hasattr(agent, 'config')
        assert hasattr(agent, 'status')

    def test_agent_client_initialization_with_config(self):
        """Test AgentClient initialization with custom config."""
        config = {"timeout": 30, "retries": 3}
        agent = AgentClient(config=config)
        assert agent is not None

    @pytest.mark.asyncio
    async def test_agent_client_start(self):
        """Test AgentClient start method."""
        agent = AgentClient()
        
        with patch.object(agent, '_initialize_connection', new_callable=AsyncMock) as mock_init:
            mock_init.return_value = None
            await agent.start()
            mock_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_agent_client_stop(self):
        """Test AgentClient stop method."""
        agent = AgentClient()
        
        with patch.object(agent, '_cleanup_connection', new_callable=AsyncMock) as mock_cleanup:
            mock_cleanup.return_value = None
            await agent.stop()
            mock_cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_agent_client_process_message(self):
        """Test AgentClient process_message method."""
        agent = AgentClient()
        message = {"text": "Hello, world!"}
        
        with patch.object(agent, '_handle_message', new_callable=AsyncMock) as mock_handle:
            mock_handle.return_value = {"response": "Processed"}
            result = await agent.process_message(message)
            assert result == {"response": "Processed"}

    @pytest.mark.asyncio
    async def test_agent_client_send_message(self):
        """Test AgentClient send_message method."""
        agent = AgentClient()
        message = {"text": "Hello, world!"}
        
        with patch.object(agent, '_send_to_letta', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {"response": "Sent"}
            result = await agent.send_message(message)
            assert result == {"response": "Sent"}

    def test_agent_client_get_status(self):
        """Test AgentClient get_status method."""
        agent = AgentClient()
        status = agent.get_status()
        assert isinstance(status, dict)

    def test_agent_client_is_connected(self):
        """Test AgentClient is_connected method."""
        agent = AgentClient()
        connected = agent.is_connected()
        assert isinstance(connected, bool)

    def test_agent_client_get_config(self):
        """Test AgentClient get_config method."""
        agent = AgentClient()
        config = agent.get_config()
        assert isinstance(config, dict)

    def test_agent_client_set_config(self):
        """Test AgentClient set_config method."""
        agent = AgentClient()
        new_config = {"timeout": 60}
        
        with patch.object(agent, '_validate_config') as mock_validate:
            mock_validate.return_value = True
            result = agent.set_config(new_config)
            assert result is True

    def test_agent_client_reset(self):
        """Test AgentClient reset method."""
        agent = AgentClient()
        
        with patch.object(agent, '_reset_state') as mock_reset:
            mock_reset.return_value = None
            agent.reset()
            mock_reset.assert_called_once()

    def test_agent_client_get_version(self):
        """Test AgentClient get_version method."""
        agent = AgentClient()
        version = agent.get_version()
        assert isinstance(version, str)

    def test_agent_client_get_capabilities(self):
        """Test AgentClient get_capabilities method."""
        agent = AgentClient()
        capabilities = agent.get_capabilities()
        assert isinstance(capabilities, list)

    def test_agent_client_has_capability(self):
        """Test AgentClient has_capability method."""
        agent = AgentClient()
        has_cap = agent.has_capability("message_processing")
        assert isinstance(has_cap, bool)

    def test_agent_client_enable_capability(self):
        """Test AgentClient enable_capability method."""
        agent = AgentClient()
        
        with patch.object(agent, '_update_capabilities') as mock_update:
            mock_update.return_value = None
            agent.enable_capability("message_processing")
            mock_update.assert_called_once()

    def test_agent_client_disable_capability(self):
        """Test AgentClient disable_capability method."""
        agent = AgentClient()
        
        with patch.object(agent, '_update_capabilities') as mock_update:
            mock_update.return_value = None
            agent.disable_capability("message_processing")
            mock_update.assert_called_once()

    def test_agent_client_get_metrics(self):
        """Test AgentClient get_metrics method."""
        agent = AgentClient()
        metrics = agent.get_metrics()
        assert isinstance(metrics, dict)

    def test_agent_client_clear_metrics(self):
        """Test AgentClient clear_metrics method."""
        agent = AgentClient()
        
        with patch.object(agent, '_reset_metrics') as mock_reset:
            mock_reset.return_value = None
            agent.clear_metrics()
            mock_reset.assert_called_once()

    def test_agent_client_get_logs(self):
        """Test AgentClient get_logs method."""
        agent = AgentClient()
        logs = agent.get_logs()
        assert isinstance(logs, list)

    def test_agent_client_clear_logs(self):
        """Test AgentClient clear_logs method."""
        agent = AgentClient()
        
        with patch.object(agent, '_reset_logs') as mock_reset:
            mock_reset.return_value = None
            agent.clear_logs()
            mock_reset.assert_called_once()

    def test_agent_client_is_healthy(self):
        """Test AgentClient is_healthy method."""
        agent = AgentClient()
        healthy = agent.is_healthy()
        assert isinstance(healthy, bool)

    def test_agent_client_get_uptime(self):
        """Test AgentClient get_uptime method."""
        agent = AgentClient()
        uptime = agent.get_uptime()
        assert isinstance(uptime, (int, float))

    def test_agent_client_to_dict(self):
        """Test AgentClient to_dict method."""
        agent = AgentClient()
        agent_dict = agent.to_dict()
        assert isinstance(agent_dict, dict)

    @pytest.mark.asyncio
    async def test_agent_client_from_dict(self):
        """Test AgentClient from_dict method."""
        agent_data = {"config": {"timeout": 30}, "status": "active"}
        
        with patch.object(AgentClient, '__init__', return_value=None):
            agent = await AgentClient.from_dict(agent_data)
            assert agent is not None

    # PluginManager Tests
    def test_plugin_manager_initialization(self):
        """Test PluginManager initialization."""
        manager = PluginManager()
        assert manager is not None
        assert hasattr(manager, 'plugins')
        assert hasattr(manager, 'event_handlers')

    def test_plugin_manager_load_plugins(self):
        """Test PluginManager load_plugins method."""
        manager = PluginManager()
        
        with patch.object(manager, '_discover_plugins') as mock_discover:
            mock_discover.return_value = []
            with patch.object(manager, '_load_plugin') as mock_load:
                mock_load.return_value = None
                manager.load_plugins()
                mock_discover.assert_called_once()

    def test_plugin_manager_get_plugin(self):
        """Test PluginManager get_plugin method."""
        manager = PluginManager()
        
        with patch.object(manager, 'plugins', {'test_plugin': MagicMock()}):
            plugin = manager.get_plugin('test_plugin')
            assert plugin is not None

    def test_plugin_manager_get_plugin_not_found(self):
        """Test PluginManager get_plugin with non-existent plugin."""
        manager = PluginManager()
        
        with patch.object(manager, 'plugins', {}):
            plugin = manager.get_plugin('nonexistent')
            assert plugin is None

    def test_plugin_manager_register_event_handler(self):
        """Test PluginManager register_event_handler method."""
        manager = PluginManager()
        
        def test_handler(event):
            pass
        
        manager.register_event_handler('test_event', test_handler)
        assert 'test_event' in manager.event_handlers

    def test_plugin_manager_unregister_event_handler(self):
        """Test PluginManager unregister_event_handler method."""
        manager = PluginManager()
        
        def test_handler(event):
            pass
        
        manager.register_event_handler('test_event', test_handler)
        manager.unregister_event_handler('test_event', test_handler)
        assert 'test_event' not in manager.event_handlers

    def test_plugin_manager_emit_event(self):
        """Test PluginManager emit_event method."""
        manager = PluginManager()
        
        handler_called = False
        def test_handler(event):
            nonlocal handler_called
            handler_called = True
        
        manager.register_event_handler('test_event', test_handler)
        manager.emit_event('test_event', {'data': 'test'})
        assert handler_called

    def test_plugin_manager_update_message_mode(self):
        """Test PluginManager update_message_mode method."""
        manager = PluginManager()
        
        with patch.object(manager, '_notify_plugins') as mock_notify:
            mock_notify.return_value = None
            manager.update_message_mode('live')
            mock_notify.assert_called_once()

    # QueueProcessor Tests
    def test_queue_processor_initialization(self):
        """Test QueueProcessor initialization."""
        processor = QueueProcessor()
        assert processor is not None
        assert hasattr(processor, 'queue')
        assert hasattr(processor, 'is_running')

    @pytest.mark.asyncio
    async def test_queue_processor_start(self):
        """Test QueueProcessor start method."""
        processor = QueueProcessor()
        
        with patch.object(processor, '_start_processing_loop', new_callable=AsyncMock) as mock_start:
            mock_start.return_value = None
            await processor.start()
            mock_start.assert_called_once()

    @pytest.mark.asyncio
    async def test_queue_processor_stop(self):
        """Test QueueProcessor stop method."""
        processor = QueueProcessor()
        
        with patch.object(processor, '_stop_processing_loop', new_callable=AsyncMock) as mock_stop:
            mock_stop.return_value = None
            await processor.stop()
            mock_stop.assert_called_once()

    def test_queue_processor_set_message_mode(self):
        """Test QueueProcessor set_message_mode method."""
        processor = QueueProcessor()
        
        with patch.object(processor, '_update_processing_mode') as mock_update:
            mock_update.return_value = None
            processor.set_message_mode('echo')
            mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_queue_processor_process_queue_item(self):
        """Test QueueProcessor _process_queue_item method."""
        processor = QueueProcessor()
        item = {"id": 1, "data": {"text": "test"}}
        
        with patch.object(processor, '_handle_item', new_callable=AsyncMock) as mock_handle:
            mock_handle.return_value = None
            await processor._process_queue_item(item)
            mock_handle.assert_called_once()

    @pytest.mark.asyncio
    async def test_queue_processor_process_message_live_mode(self):
        """Test QueueProcessor _process_message_live_mode method."""
        processor = QueueProcessor()
        message = {"text": "Hello, world!"}
        
        with patch.object(processor, '_send_to_letta', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {"response": "Sent"}
            result = await processor._process_message_live_mode(message)
            assert result == {"response": "Sent"}

    @pytest.mark.asyncio
    async def test_queue_processor_process_message_echo_mode(self):
        """Test QueueProcessor _process_message_echo_mode method."""
        processor = QueueProcessor()
        message = {"text": "Hello, world!"}
        
        result = await processor._process_message_echo_mode(message)
        assert result == message

    @pytest.mark.asyncio
    async def test_queue_processor_process_message_dry_run_mode(self):
        """Test QueueProcessor _process_message_dry_run_mode method."""
        processor = QueueProcessor()
        message = {"text": "Hello, world!"}
        
        result = await processor._process_message_dry_run_mode(message)
        assert result == {"status": "dry_run", "message": message}

    @pytest.mark.asyncio
    async def test_queue_processor_handle_message_processing_error(self):
        """Test QueueProcessor _handle_message_processing_error method."""
        processor = QueueProcessor()
        error = Exception("Processing failed")
        
        with patch.object(processor, '_log_error') as mock_log:
            mock_log.return_value = None
            await processor._handle_message_processing_error(error)
            mock_log.assert_called_once()

    @pytest.mark.asyncio
    async def test_queue_processor_handle_plugin_response(self):
        """Test QueueProcessor _handle_plugin_response method."""
        processor = QueueProcessor()
        response = {"status": "success", "data": "processed"}
        
        with patch.object(processor, '_update_metrics') as mock_update:
            mock_update.return_value = None
            await processor._handle_plugin_response(response)
            mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_queue_processor_handle_plugin_error(self):
        """Test QueueProcessor _handle_plugin_error method."""
        processor = QueueProcessor()
        error = Exception("Plugin error")
        
        with patch.object(processor, '_log_error') as mock_log:
            mock_log.return_value = None
            await processor._handle_plugin_error(error)
            mock_log.assert_called_once()

    @pytest.mark.asyncio
    async def test_queue_processor_handle_message_processed_callback(self):
        """Test QueueProcessor _handle_message_processed_callback method."""
        processor = QueueProcessor()
        callback_data = {"message_id": 1, "status": "processed"}
        
        with patch.object(processor, '_notify_callbacks') as mock_notify:
            mock_notify.return_value = None
            await processor._handle_message_processed_callback(callback_data)
            mock_notify.assert_called_once()

    # Message Tests
    def test_message_initialization(self):
        """Test Message initialization."""
        message = Message()
        assert message is not None
        assert hasattr(message, 'id')
        assert hasattr(message, 'content')

    def test_message_initialization_with_data(self):
        """Test Message initialization with data."""
        data = {"text": "Hello, world!", "user_id": "user123"}
        message = Message(data=data)
        assert message is not None

    def test_message_get_content(self):
        """Test Message get_content method."""
        message = Message()
        content = message.get_content()
        assert isinstance(content, str)

    def test_message_set_content(self):
        """Test Message set_content method."""
        message = Message()
        new_content = "Updated content"
        
        with patch.object(message, '_validate_content') as mock_validate:
            mock_validate.return_value = True
            result = message.set_content(new_content)
            assert result is True

    def test_message_get_metadata(self):
        """Test Message get_metadata method."""
        message = Message()
        metadata = message.get_metadata()
        assert isinstance(metadata, dict)

    def test_message_set_metadata(self):
        """Test Message set_metadata method."""
        message = Message()
        new_metadata = {"priority": "high", "tags": ["important"]}
        
        with patch.object(message, '_validate_metadata') as mock_validate:
            mock_validate.return_value = True
            result = message.set_metadata(new_metadata)
            assert result is True

    def test_message_get_timestamp(self):
        """Test Message get_timestamp method."""
        message = Message()
        timestamp = message.get_timestamp()
        assert isinstance(timestamp, str)

    def test_message_is_valid(self):
        """Test Message is_valid method."""
        message = Message()
        valid = message.is_valid()
        assert isinstance(valid, bool)

    def test_message_to_dict(self):
        """Test Message to_dict method."""
        message = Message()
        message_dict = message.to_dict()
        assert isinstance(message_dict, dict)

    def test_message_from_dict(self):
        """Test Message from_dict method."""
        message_data = {"content": "test", "metadata": {"key": "value"}}
        
        with patch.object(Message, '__init__', return_value=None):
            message = Message.from_dict(message_data)
            assert message is not None

    def test_message_str_representation(self):
        """Test Message string representation."""
        message = Message()
        message_str = str(message)
        assert isinstance(message_str, str)

    def test_message_repr_representation(self):
        """Test Message repr representation."""
        message = Message()
        message_repr = repr(message)
        assert isinstance(message_repr, str)

    def test_message_equality(self):
        """Test Message equality."""
        message1 = Message()
        message2 = Message()
        
        # Should not be equal (different instances)
        assert message1 != message2

    def test_message_hash(self):
        """Test Message hash."""
        message = Message()
        message_hash = hash(message)
        assert isinstance(message_hash, int)

    # Integration Tests
    @pytest.mark.asyncio
    async def test_agent_plugin_integration(self):
        """Test AgentClient and PluginManager integration."""
        agent = AgentClient()
        manager = PluginManager()
        
        with patch.object(agent, '_initialize_connection', new_callable=AsyncMock):
            with patch.object(manager, '_discover_plugins') as mock_discover:
                mock_discover.return_value = []
                await agent.start()
                manager.load_plugins()

    @pytest.mark.asyncio
    async def test_queue_processor_agent_integration(self):
        """Test QueueProcessor and AgentClient integration."""
        processor = QueueProcessor()
        agent = AgentClient()
        
        with patch.object(processor, '_start_processing_loop', new_callable=AsyncMock):
            with patch.object(agent, '_initialize_connection', new_callable=AsyncMock):
                await processor.start()
                await agent.start()

    @pytest.mark.asyncio
    async def test_full_message_processing_flow(self):
        """Test full message processing flow."""
        agent = AgentClient()
        processor = QueueProcessor()
        message = Message()
        
        with patch.object(agent, '_handle_message', new_callable=AsyncMock) as mock_handle:
            with patch.object(processor, '_process_queue_item', new_callable=AsyncMock) as mock_process:
                mock_handle.return_value = {"response": "processed"}
                mock_process.return_value = None
                
                result = await agent.process_message({"text": "test"})
                await processor._process_queue_item({"id": 1, "data": result})
                
                mock_handle.assert_called_once()
                mock_process.assert_called_once()

    # Error Handling Tests
    @pytest.mark.asyncio
    async def test_agent_client_start_with_error(self):
        """Test AgentClient start with error."""
        agent = AgentClient()
        
        with patch.object(agent, '_initialize_connection', new_callable=AsyncMock) as mock_init:
            mock_init.side_effect = Exception("Connection failed")
            
            with pytest.raises(Exception, match="Connection failed"):
                await agent.start()

    @pytest.mark.asyncio
    async def test_plugin_manager_load_plugins_with_error(self):
        """Test PluginManager load_plugins with error."""
        manager = PluginManager()
        
        with patch.object(manager, '_discover_plugins') as mock_discover:
            mock_discover.side_effect = Exception("Discovery failed")
            
            with pytest.raises(Exception, match="Discovery failed"):
                manager.load_plugins()

    @pytest.mark.asyncio
    async def test_queue_processor_start_with_error(self):
        """Test QueueProcessor start with error."""
        processor = QueueProcessor()
        
        with patch.object(processor, '_start_processing_loop', new_callable=AsyncMock) as mock_start:
            mock_start.side_effect = Exception("Start failed")
            
            with pytest.raises(Exception, match="Start failed"):
                await processor.start()

    def test_message_set_content_with_validation_error(self):
        """Test Message set_content with validation error."""
        message = Message()
        
        with patch.object(message, '_validate_content') as mock_validate:
            mock_validate.return_value = False
            
            with pytest.raises(ValueError):
                message.set_content("invalid content")

    def test_message_set_metadata_with_validation_error(self):
        """Test Message set_metadata with validation error."""
        message = Message()
        
        with patch.object(message, '_validate_metadata') as mock_validate:
            mock_validate.return_value = False
            
            with pytest.raises(ValueError):
                message.set_metadata({"invalid": "metadata"})
