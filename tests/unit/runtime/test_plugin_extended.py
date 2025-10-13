"""Extended unit tests for runtime plugin manager."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from plugins import Event, EventType, Plugin
from runtime.core.plugin import PluginManager


class MockPlugin(Plugin):
    """Mock plugin for testing."""

    def __init__(self, name="test_plugin", platform="test"):
        self._name = name
        self._platform = platform
        self._enabled = True
        self._settings = {}
        self._event_handlers = {}

    def get_name(self) -> str:
        return self._name

    def get_platform(self) -> str:
        return self._platform

    def get_message_handler(self):
        return AsyncMock()

    async def start(self):
        pass

    async def stop(self):
        pass

    def register_event_handler(self, event_type: EventType, handler):
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    def emit_event(self, event: Event):
        if event.type in self._event_handlers:
            for handler in self._event_handlers[event.type]:
                handler(event)


class TestPluginManagerExtended:
    """Extended test cases for PluginManager."""

    def test_plugin_manager_initialization(self):
        """Test plugin manager initialization."""
        manager = PluginManager()
        assert manager is not None
        assert not manager.is_running()

    @pytest.mark.asyncio
    async def test_load_plugin(self):
        """Test loading a plugin."""
        manager = PluginManager()

        with patch(
            "runtime.core.plugin.importlib.util.spec_from_file_location"
        ) as mock_spec:
            with patch(
                "runtime.core.plugin.importlib.util.module_from_spec"
            ) as mock_module:
                mock_spec.return_value = MagicMock()
                mock_module.return_value = MagicMock()

                # Mock the module to contain our MockPlugin
                mock_module.return_value.__dict__ = {
                    "MockPlugin": MockPlugin,
                    "Plugin": Plugin,
                }

                with patch("builtins.open", create=True):
                    await manager.load_plugin("test_plugin.py")

                assert "test_plugin" in manager.get_loaded_plugins()

    @pytest.mark.asyncio
    async def test_unload_plugin(self):
        """Test unloading a plugin."""
        manager = PluginManager()

        # First load a plugin
        plugin = MockPlugin()
        manager._plugins["test_plugin"] = plugin

        await manager.unload_plugin("test_plugin")
        assert "test_plugin" not in manager.get_loaded_plugins()

    @pytest.mark.asyncio
    async def test_start_plugin(self):
        """Test starting a plugin."""
        manager = PluginManager()

        plugin = MockPlugin()
        plugin.start = AsyncMock()
        manager._plugins["test_plugin"] = plugin

        await manager.start_plugin("test_plugin")
        plugin.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_plugin(self):
        """Test stopping a plugin."""
        manager = PluginManager()

        plugin = MockPlugin()
        plugin.stop = AsyncMock()
        manager._plugins["test_plugin"] = plugin

        await manager.stop_plugin("test_plugin")
        plugin.stop.assert_called_once()

    def test_register_event_handler(self):
        """Test registering event handler."""
        manager = PluginManager()
        handler = MagicMock()

        manager.register_event_handler(EventType.MESSAGE, handler)
        assert EventType.MESSAGE in manager._event_handlers
        assert handler in manager._event_handlers[EventType.MESSAGE]

    def test_unregister_event_handler(self):
        """Test unregistering event handler."""
        manager = PluginManager()
        handler = MagicMock()

        manager.register_event_handler(EventType.MESSAGE, handler)
        manager.unregister_event_handler(EventType.MESSAGE, handler)

        assert EventType.MESSAGE not in manager._event_handlers

    def test_emit_event(self):
        """Test emitting event."""
        manager = PluginManager()
        handler = MagicMock()

        manager.register_event_handler(EventType.MESSAGE, handler)

        event = Event(type=EventType.MESSAGE, data={}, source="test")
        manager.emit_event(event)

        handler.assert_called_once_with(event)

    def test_get_platform_handler(self):
        """Test getting platform handler."""
        manager = PluginManager()

        MockPlugin(platform="telegram")
        handler = AsyncMock()
        manager._platform_handlers["telegram"] = handler

        result = manager.get_platform_handler("telegram")
        assert result == handler

    @pytest.mark.asyncio
    async def test_discover_plugins(self):
        """Test discovering plugins."""
        manager = PluginManager()

        with patch("runtime.core.plugin.Path") as mock_path:
            mock_plugins_dir = MagicMock()
            mock_plugin_dir = MagicMock()
            mock_plugin_file = MagicMock()

            mock_plugin_dir.is_dir.return_value = True
            mock_plugin_dir.name = "test_plugin"
            mock_plugin_file.exists.return_value = True

            mock_plugins_dir.iterdir.return_value = [mock_plugin_dir]
            mock_plugin_dir.__truediv__.return_value = mock_plugin_file
            mock_path.return_value = mock_plugins_dir

            with patch.object(manager, "load_plugin") as mock_load:
                await manager.discover_plugins()
                mock_load.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_all_plugins(self):
        """Test starting all plugins."""
        manager = PluginManager()

        plugin1 = MockPlugin("plugin1")
        plugin2 = MockPlugin("plugin2")
        plugin1.start = AsyncMock()
        plugin2.start = AsyncMock()

        manager._plugins = {"plugin1": plugin1, "plugin2": plugin2}

        await manager.start()

        assert manager.is_running()
        plugin1.start.assert_called_once()
        plugin2.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_all_plugins(self):
        """Test stopping all plugins."""
        manager = PluginManager()

        plugin1 = MockPlugin("plugin1")
        plugin2 = MockPlugin("plugin2")
        plugin1.stop = AsyncMock()
        plugin2.stop = AsyncMock()

        manager._plugins = {"plugin1": plugin1, "plugin2": plugin2}
        manager._running = True

        await manager.stop()

        assert not manager.is_running()
        plugin1.stop.assert_called_once()
        plugin2.stop.assert_called_once()

    def test_get_plugin(self):
        """Test getting a plugin by name."""
        manager = PluginManager()

        plugin = MockPlugin("test_plugin")
        manager._plugins["test_plugin"] = plugin

        result = manager.get_plugin("test_plugin")
        assert result == plugin

        result = manager.get_plugin("nonexistent")
        assert result is None

    def test_get_loaded_plugins(self):
        """Test getting loaded plugin names."""
        manager = PluginManager()

        plugin1 = MockPlugin("plugin1")
        plugin2 = MockPlugin("plugin2")
        manager._plugins = {"plugin1": plugin1, "plugin2": plugin2}

        result = manager.get_loaded_plugins()
        assert set(result) == {"plugin1", "plugin2"}

    @pytest.mark.asyncio
    async def test_update_message_mode(self):
        """Test updating message mode for plugins."""
        manager = PluginManager()

        plugin = MockPlugin("test_plugin")
        plugin.set_message_mode = MagicMock()
        manager._plugins["test_plugin"] = plugin

        await manager.update_message_mode("live")

        plugin.set_message_mode.assert_called_once_with("live")
