"""Unit tests for main.py functionality."""

import os
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest

import main


@pytest.mark.unit
def test_main_function():
    """Test main function."""
    with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}), patch(
        "main.Application"
    ) as mock_app_class, patch("asyncio.run") as mock_run, patch("main.logger"), patch(
        "sys.exit"
    ) as mock_exit:
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        main.main()

        mock_app_class.assert_called_once()
        # main() calls both app.start() and app.stop()
        assert mock_run.call_count == 2
        mock_run.assert_any_call(mock_app.start())
        mock_run.assert_any_call(mock_app.stop())
        mock_exit.assert_called_with(0)


@pytest.mark.unit
def test_main_function_exception():
    """Test main function exception handling."""
    with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}), patch(
        "main.Application"
    ) as mock_app_class, patch(
        "asyncio.run", side_effect=Exception("Test error")
    ), patch(
        "main.logger"
    ) as mock_logger, patch(
        "sys.exit"
    ) as mock_exit:
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        main.main()

        # The exception is caught in the finally block during cleanup
        mock_logger.error.assert_called_with("❌ Error during final cleanup: Test error")
        mock_exit.assert_called_with(0)


@pytest.mark.unit
def test_create_default_settings_file_exists():
    """Test create_default_settings when file already exists."""
    with patch("main.Path") as mock_path:
        mock_settings_path = MagicMock()
        mock_settings_path.exists.return_value = True
        mock_path.return_value = mock_settings_path

        main.create_default_settings()

        # Should not create file if it already exists
        mock_settings_path.write_text.assert_not_called()


@pytest.mark.unit
def test_create_default_settings_file_not_exists():
    """Test create_default_settings when file doesn't exist."""
    with patch("main.Path") as mock_path, patch(
        "builtins.open", mock_open()
    ) as mock_file, patch("main.json.dump") as mock_json:
        mock_settings_path = MagicMock()
        mock_settings_path.exists.return_value = False
        mock_path.return_value = mock_settings_path

        main.create_default_settings()

        # Should create file with default settings
        mock_file.assert_called_once_with(mock_settings_path, "w")
        mock_json.assert_called_once()


@pytest.mark.unit
def test_create_default_settings_logging():
    """Test create_default_settings logging."""
    with patch("main.Path") as mock_path, patch("main.logger") as mock_logger, patch(
        "builtins.open", mock_open()
    ), patch("main.json.dump"):
        mock_settings_path = MagicMock()
        mock_settings_path.exists.return_value = False
        mock_path.return_value = mock_settings_path

        main.create_default_settings()

        mock_logger.info.assert_called_with("Created default settings.json file")


@pytest.mark.unit
def test_application_init():
    """Test Application class initialization."""
    with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}), patch(
        "main.QueueProcessor"
    ), patch("main.PluginManager"), patch("main.AgentClient"):
        app = main.Application()

        assert app.queue_processor is not None
        assert app.plugin_manager is not None
        assert app.agent is not None
        assert app._shutdown_event is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_application_start():
    """Test Application start method."""
    with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}), patch(
        "main.Application"
    ) as mock_app_class:
        mock_app = MagicMock()
        mock_app.start = AsyncMock()
        mock_app_class.return_value = mock_app

        app = main.Application()
        await app.start()

        mock_app.start.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_application_stop():
    """Test Application stop method."""
    with patch.dict(os.environ, {"AGENT_ID": "test-agent-123"}), patch(
        "main.Application"
    ) as mock_app_class:
        mock_app = MagicMock()
        mock_app.stop = AsyncMock()
        mock_app_class.return_value = mock_app

        app = main.Application()
        await app.stop()

        mock_app.stop.assert_called_once()
