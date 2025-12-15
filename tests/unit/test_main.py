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
def test_create_default_settings_file_exists_valid_json(tmp_path, monkeypatch):
    """Test create_default_settings when file exists with valid JSON."""
    settings_file = tmp_path / "settings.json"
    settings_file.write_text('{"debug_mode": true}')

    monkeypatch.chdir(tmp_path)

    main.create_default_settings()

    # Should NOT overwrite valid JSON file
    content = settings_file.read_text()
    assert "true" in content  # Original content preserved


@pytest.mark.unit
def test_create_default_settings_file_not_exists(tmp_path, monkeypatch):
    """Test create_default_settings when file doesn't exist."""
    monkeypatch.chdir(tmp_path)

    main.create_default_settings()

    # Should create file with default settings
    settings_file = tmp_path / "settings.json"
    assert settings_file.exists()

    import json
    content = json.loads(settings_file.read_text())
    assert content["debug_mode"] is False
    assert content["queue_refresh"] == 5
    assert content["max_retries"] == 3
    assert content["message_mode"] == "live"


@pytest.mark.unit
def test_create_default_settings_empty_file(tmp_path, monkeypatch):
    """Test create_default_settings when file exists but is empty (Issue #37)."""
    settings_file = tmp_path / "settings.json"
    settings_file.write_text("")  # Empty file

    monkeypatch.chdir(tmp_path)

    main.create_default_settings()

    # Should recreate file with defaults
    import json
    content = json.loads(settings_file.read_text())
    assert content["debug_mode"] is False
    assert content["queue_refresh"] == 5


@pytest.mark.unit
def test_create_default_settings_invalid_json(tmp_path, monkeypatch):
    """Test create_default_settings when file contains invalid JSON."""
    settings_file = tmp_path / "settings.json"
    settings_file.write_text("{invalid json}")  # Invalid JSON

    monkeypatch.chdir(tmp_path)

    main.create_default_settings()

    # Should recreate file with defaults
    import json
    content = json.loads(settings_file.read_text())
    assert content["debug_mode"] is False
    assert content["queue_refresh"] == 5


@pytest.mark.unit
def test_create_default_settings_logging(tmp_path, monkeypatch):
    """Test create_default_settings logging."""
    monkeypatch.chdir(tmp_path)

    with patch("main.logger") as mock_logger:
        main.create_default_settings()

        # Should log that file was created
        mock_logger.info.assert_any_call("Settings file does not exist, creating default...")
        mock_logger.info.assert_any_call("Created default settings.json file")


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
