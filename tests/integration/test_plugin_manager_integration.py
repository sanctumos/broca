"""
Integration tests: PluginManager discover, load, start, stop with a real plugin module.

Uses the minimal integration_plugin from tests/fixtures so no Telegram/Letta deps.
"""

from pathlib import Path

import pytest

from runtime.core.plugin import PluginManager


@pytest.mark.integration
@pytest.mark.asyncio
async def test_plugin_manager_discovers_and_starts_minimal_plugin():
    """Discover plugin from tests/fixtures, start it, get handler, stop."""
    project_root = Path(__file__).resolve().parent.parent.parent
    plugins_dir = str(project_root / "tests" / "fixtures")

    manager = PluginManager()
    await manager.discover_plugins(plugins_dir=plugins_dir, config={})

    assert "integration_test" in manager._plugins
    assert manager.get_platform_handler("integration_test") is not None

    await manager.start()
    plugin = manager.get_plugin("integration_test")
    assert plugin is not None
    assert plugin._running

    await manager.stop()
    assert not plugin._running


@pytest.mark.integration
@pytest.mark.asyncio
async def test_plugin_manager_load_plugin_by_path():
    """Load a single plugin by path and start/stop it."""
    project_root = Path(__file__).resolve().parent.parent.parent
    plugin_path = str(
        project_root / "tests" / "fixtures" / "integration_plugin" / "plugin.py"
    )

    manager = PluginManager()
    await manager.load_plugin(plugin_path)

    assert manager.get_plugin("integration_test") is not None
    handler = manager.get_platform_handler("integration_test")
    assert handler is not None

    await manager.start()
    await manager.stop()
