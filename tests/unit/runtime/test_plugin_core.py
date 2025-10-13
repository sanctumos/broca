"""Unit tests for runtime core plugin functionality."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from plugins import Plugin
from runtime.core.plugin import PluginManager


@pytest.mark.unit
def test_plugin_manager_init():
    """Test PluginManager initialization."""
    manager = PluginManager()
    assert manager is not None
    assert hasattr(manager, "plugins")
    assert hasattr(manager, "event_handlers")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_plugin_manager_load_plugin():
    """Test PluginManager load_plugin."""
    manager = PluginManager()

    with patch("runtime.core.plugin.importlib.import_module") as mock_import:
        mock_module = MagicMock()
        mock_plugin_class = MagicMock()
        mock_plugin_instance = MagicMock()
        mock_plugin_class.return_value = mock_plugin_instance
        mock_module.Plugin = mock_plugin_class
        mock_import.return_value = mock_module

        await manager.load_plugin("test_plugin")
        assert "test_plugin" in manager.plugins


@pytest.mark.unit
@pytest.mark.asyncio
async def test_plugin_manager_unload_plugin():
    """Test PluginManager unload_plugin."""
    manager = PluginManager()

    # Add a mock plugin
    mock_plugin = MagicMock()
    mock_plugin.stop = AsyncMock()
    manager.plugins["test_plugin"] = mock_plugin

    await manager.unload_plugin("test_plugin")
    assert "test_plugin" not in manager.plugins


@pytest.mark.unit
@pytest.mark.asyncio
async def test_plugin_manager_start_all():
    """Test PluginManager start_all."""
    manager = PluginManager()

    # Add mock plugins
    mock_plugin1 = MagicMock()
    mock_plugin1.start = AsyncMock()
    mock_plugin2 = MagicMock()
    mock_plugin2.start = AsyncMock()
    manager.plugins = {"plugin1": mock_plugin1, "plugin2": mock_plugin2}

    await manager.start_all()
    mock_plugin1.start.assert_called_once()
    mock_plugin2.start.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_plugin_manager_stop_all():
    """Test PluginManager stop_all."""
    manager = PluginManager()

    # Add mock plugins
    mock_plugin1 = MagicMock()
    mock_plugin1.stop = AsyncMock()
    mock_plugin2 = MagicMock()
    mock_plugin2.stop = AsyncMock()
    manager.plugins = {"plugin1": mock_plugin1, "plugin2": mock_plugin2}

    await manager.stop_all()
    mock_plugin1.stop.assert_called_once()
    mock_plugin2.stop.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_plugin_manager_emit_event():
    """Test PluginManager emit_event."""
    manager = PluginManager()

    # Add mock event handler
    mock_handler = AsyncMock()
    manager.event_handlers["test_event"] = [mock_handler]

    await manager.emit_event("test_event", {"data": "test"})
    mock_handler.assert_called_once_with({"data": "test"})


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
    manager.plugins["test_plugin"] = mock_plugin

    result = manager.get_plugin("test_plugin")
    assert result == mock_plugin

    result = manager.get_plugin("nonexistent")
    assert result is None


@pytest.mark.unit
def test_plugin_manager_list_plugins():
    """Test PluginManager list_plugins."""
    manager = PluginManager()
    manager.plugins = {"plugin1": MagicMock(), "plugin2": MagicMock()}

    plugins = manager.list_plugins()
    assert len(plugins) == 2
    assert "plugin1" in plugins
    assert "plugin2" in plugins
