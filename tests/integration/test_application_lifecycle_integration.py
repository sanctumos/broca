"""
Integration tests: Application start/stop lifecycle with real DB and mocked externals.

Uses temp_db, mocks PID file, Letta agent, and discovers only the minimal test plugin.
"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.asyncio
async def test_application_starts_and_stops_gracefully(temp_db: str):
    """Application starts (with mocks), runs briefly, then stops cleanly."""
    project_root = Path(__file__).resolve().parent.parent.parent
    fixtures_plugins_dir = str(project_root / "tests" / "fixtures")

    mock_client = MagicMock()
    mock_client.agents.retrieve.return_value = MagicMock(id="test-agent", name="Test")
    mock_client.agents.blocks.attach.return_value = None
    mock_client.agents.blocks.detach.return_value = None

    with (
        patch("main.PIDManager") as mock_pid_class,
        patch("main.create_default_settings"),
        patch("runtime.core.letta_client.get_letta_client", return_value=mock_client),
        patch("runtime.core.queue.get_letta_client", return_value=mock_client),
        patch("runtime.core.agent.get_letta_client", return_value=mock_client),
        patch("main.validate_environment_variables"),
    ):
        mock_pid_class.return_value.create_pid_file.return_value = None
        mock_pid_class.return_value.cleanup.return_value = None

        from main import Application

        app = Application()
        app.agent.initialize = AsyncMock(return_value=True)

        real_discover = app.plugin_manager.discover_plugins

        async def discover_and_await(**kwargs):
            await real_discover(
                plugins_dir=fixtures_plugins_dir,
                config=kwargs.get("config") or {},
            )

        app.plugin_manager.discover_plugins = AsyncMock(side_effect=discover_and_await)

        start_task = asyncio.create_task(app.start())
        await asyncio.sleep(2.0)
        app._shutdown_event.set()
        await asyncio.wait_for(start_task, timeout=10.0)

    assert app.queue_processor.is_running is False
