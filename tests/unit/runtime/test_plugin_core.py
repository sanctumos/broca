"""Unit tests for runtime core plugin functionality."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from common.exceptions import PluginError
from plugins import Plugin
from runtime.core.plugin import PluginManager


@pytest.mark.unit
def test_plugin_manager_init():
    """Test PluginManager initialization."""
    manager = PluginManager()
    assert manager is not None
    assert hasattr(manager, "_plugins")
    assert hasattr(manager, "_event_handlers")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_plugin_manager_load_plugin():
    """Test PluginManager load_plugin."""
    manager = PluginManager()

    # Test that load_plugin raises PluginError for invalid plugin path
    with pytest.raises(PluginError):  # PluginError is raised
        await manager.load_plugin("nonexistent_plugin")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_plugin_manager_unload_plugin():
    """Test PluginManager unload_plugin."""
    manager = PluginManager()

    # Add a mock plugin
    mock_plugin = MagicMock()
    mock_plugin.stop = AsyncMock()
    manager._plugins["test_plugin"] = mock_plugin

    await manager.unload_plugin("test_plugin")
    assert "test_plugin" not in manager._plugins


@pytest.mark.unit
@pytest.mark.asyncio
async def test_plugin_manager_start():
    """Test PluginManager start."""
    manager = PluginManager()

    # Add mock plugins
    mock_plugin1 = MagicMock()
    mock_plugin1.start = AsyncMock()
    mock_plugin2 = MagicMock()
    mock_plugin2.start = AsyncMock()
    manager._plugins = {"plugin1": mock_plugin1, "plugin2": mock_plugin2}

    await manager.start()
    assert manager.is_running()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_plugin_manager_stop():
    """Test PluginManager stop."""
    manager = PluginManager()

    # Add mock plugins
    mock_plugin1 = MagicMock()
    mock_plugin1.stop = AsyncMock()
    mock_plugin2 = MagicMock()
    mock_plugin2.stop = AsyncMock()
    manager._plugins = {"plugin1": mock_plugin1, "plugin2": mock_plugin2}

    await manager.stop()
    assert not manager.is_running()


@pytest.mark.unit
def test_plugin_manager_emit_event():
    """Test PluginManager emit_event."""
    manager = PluginManager()

    # Add mock event handler
    mock_handler = MagicMock()
    from plugins import Event, EventType

    manager._event_handlers[EventType.MESSAGE] = [mock_handler]

    event = Event(type=EventType.MESSAGE, data={"data": "test"}, source="test")
    manager.emit_event(event)
    mock_handler.assert_called_once_with(event)


@pytest.mark.unit
def test_plugin_base():
    """Test Plugin abstract class."""
    # Plugin is abstract, so we can't instantiate it directly
    with pytest.raises(TypeError):
        Plugin()


@pytest.mark.unit
def test_plugin_manager_get_plugin():
    """Test PluginManager get_plugin."""
    manager = PluginManager()

    mock_plugin = MagicMock()
    manager._plugins["test_plugin"] = mock_plugin

    result = manager.get_plugin("test_plugin")
    assert result == mock_plugin

    result = manager.get_plugin("nonexistent")
    assert result is None


@pytest.mark.unit
def test_plugin_manager_get_loaded_plugins():
    """Test PluginManager get_loaded_plugins."""
    manager = PluginManager()
    manager._plugins = {"plugin1": MagicMock(), "plugin2": MagicMock()}

    plugins = manager.get_loaded_plugins()
    assert len(plugins) == 2
    assert "plugin1" in plugins
    assert "plugin2" in plugins
