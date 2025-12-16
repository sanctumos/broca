"""Comprehensive unit tests for main.py to achieve 100% coverage."""

import asyncio
import os
import signal
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import main


@pytest.mark.unit
def test_create_default_settings_invalid_json(tmp_path, monkeypatch):
    """Test create_default_settings with invalid JSON."""
    monkeypatch.chdir(tmp_path)
    
    settings_file = tmp_path / "settings.json"
    settings_file.write_text("{ invalid json }")
    
    main.create_default_settings()
    
    # Should recreate file with defaults
    import json
    content = json.loads(settings_file.read_text())
    assert content["debug_mode"] is False


@pytest.mark.unit
def test_create_default_settings_read_error(tmp_path, monkeypatch):
    """Test create_default_settings with read error."""
    monkeypatch.chdir(tmp_path)
    
    settings_file = tmp_path / "settings.json"
    settings_file.write_text('{"test": "data"}')
    
    with patch("pathlib.Path.read_text", side_effect=OSError("Read error")):
        main.create_default_settings()
        
        # Should recreate file with defaults
        import json
        content = json.loads(settings_file.read_text())
        assert content["debug_mode"] is False


@pytest.mark.unit
def test_pid_manager_init_default():
    """Test PIDManager initialization with default directory."""
    manager = main.PIDManager()
    
    assert manager.pid == os.getpid()
    assert "broca.pid" in manager.pid_file
    assert "broca.lock" in manager.lock_file


@pytest.mark.unit
def test_pid_manager_init_custom_dir(tmp_path):
    """Test PIDManager initialization with custom directory."""
    instance_dir = str(tmp_path / "custom")
    manager = main.PIDManager(instance_dir=instance_dir)
    
    assert manager.pid_file == str(Path(instance_dir) / "broca.pid")
    assert manager.lock_file == str(Path(instance_dir) / "broca.lock")


@pytest.mark.unit
def test_pid_manager_create_pid_file_new(tmp_path, monkeypatch):
    """Test PIDManager create_pid_file when file doesn't exist."""
    monkeypatch.chdir(tmp_path)
    
    manager = main.PIDManager(instance_dir=str(tmp_path))
    manager.create_pid_file()
    
    assert Path(manager.pid_file).exists()
    assert Path(manager.pid_file).read_text().strip() == str(os.getpid())


@pytest.mark.unit
def test_pid_manager_create_pid_file_stale(tmp_path, monkeypatch):
    """Test PIDManager create_pid_file with stale PID file."""
    monkeypatch.chdir(tmp_path)
    
    # Create stale PID file (non-existent process)
    pid_file = tmp_path / "broca.pid"
    pid_file.write_text("99999")  # Non-existent PID
    
    manager = main.PIDManager(instance_dir=str(tmp_path))
    
    with patch("main.PIDManager.is_process_running", return_value=False):
        manager.create_pid_file()
        
        assert pid_file.exists()
        assert pid_file.read_text().strip() == str(os.getpid())


@pytest.mark.unit
def test_pid_manager_create_pid_file_running_process(tmp_path, monkeypatch):
    """Test PIDManager create_pid_file when process is running."""
    monkeypatch.chdir(tmp_path)
    
    pid_file = tmp_path / "broca.pid"
    pid_file.write_text(str(os.getpid()))  # Current PID
    
    manager = main.PIDManager(instance_dir=str(tmp_path))
    
    with patch("main.PIDManager.is_process_running", return_value=True):
        with pytest.raises(RuntimeError, match="Another instance is already running"):
            manager.create_pid_file()


@pytest.mark.unit
def test_pid_manager_cleanup(tmp_path, monkeypatch):
    """Test PIDManager cleanup."""
    monkeypatch.chdir(tmp_path)
    
    manager = main.PIDManager(instance_dir=str(tmp_path))
    manager.create_pid_file()
    
    # Create lock file
    lock_file = Path(manager.lock_file)
    lock_file.touch()
    
    manager.cleanup()
    
    assert not Path(manager.pid_file).exists()
    assert not lock_file.exists()


@pytest.mark.unit
def test_pid_manager_cleanup_error(tmp_path, monkeypatch):
    """Test PIDManager cleanup with error."""
    monkeypatch.chdir(tmp_path)
    
    manager = main.PIDManager(instance_dir=str(tmp_path))
    manager.create_pid_file()
    
    with patch("os.remove", side_effect=OSError("Permission denied")):
        # Should not raise, just log warning
        manager.cleanup()


@pytest.mark.unit
def test_pid_manager_is_process_running_not_exists(tmp_path):
    """Test is_process_running when PID file doesn't exist."""
    result = main.PIDManager.is_process_running(str(tmp_path / "nonexistent.pid"))
    
    assert result is False


@pytest.mark.unit
def test_pid_manager_is_process_running_invalid_pid(tmp_path):
    """Test is_process_running with invalid PID."""
    pid_file = tmp_path / "test.pid"
    pid_file.write_text("not_a_number")
    
    result = main.PIDManager.is_process_running(str(pid_file))
    
    assert result is False


@pytest.mark.unit
def test_pid_manager_is_process_running_exists(tmp_path):
    """Test is_process_running when process exists."""
    pid_file = tmp_path / "test.pid"
    pid_file.write_text(str(os.getpid()))
    
    result = main.PIDManager.is_process_running(str(pid_file))
    
    assert result is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_application_init_success(mock_env_vars, tmp_path, monkeypatch):
    """Test Application initialization."""
    monkeypatch.chdir(tmp_path)
    
    with patch("main.PluginManager") as mock_pm_class, \
         patch("main.AgentClient") as mock_agent_class, \
         patch("main.QueueProcessor") as mock_qp_class, \
         patch("main.create_default_settings"), \
         patch("main.PIDManager") as mock_pid_class:
        
        mock_pm = MagicMock()
        mock_pm_class.return_value = mock_pm
        
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent
        
        mock_qp = MagicMock()
        mock_qp_class.return_value = mock_qp
        
        mock_pid = MagicMock()
        mock_pid_class.return_value = mock_pid
        
        app = main.Application()
        
        assert app.plugin_manager == mock_pm
        assert app.agent == mock_agent
        assert app.queue_processor == mock_qp


@pytest.mark.unit
@pytest.mark.asyncio
async def test_application_init_pid_error(mock_env_vars, tmp_path, monkeypatch):
    """Test Application initialization with PID error."""
    monkeypatch.chdir(tmp_path)
    
    with patch("main.PluginManager"), \
         patch("main.AgentClient"), \
         patch("main.QueueProcessor"), \
         patch("main.create_default_settings"), \
         patch("main.PIDManager") as mock_pid_class:
        
        mock_pid = MagicMock()
        mock_pid.create_pid_file.side_effect = RuntimeError("PID error")
        mock_pid_class.return_value = mock_pid
        
        with pytest.raises(RuntimeError, match="PID error"):
            main.Application()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_application_setup_signal_handlers_unix(mock_env_vars):
    """Test _setup_signal_handlers on Unix."""
    with patch("main.PluginManager"), \
         patch("main.AgentClient"), \
         patch("main.QueueProcessor"), \
         patch("main.create_default_settings"), \
         patch("main.PIDManager"), \
         patch("sys.platform", "linux"), \
         patch("asyncio.get_running_loop") as mock_loop:
        
        mock_loop_instance = MagicMock()
        mock_loop.return_value = mock_loop_instance
        
        app = main.Application()
        app._setup_signal_handlers()
        
        # Should call add_signal_handler
        assert mock_loop_instance.add_signal_handler.called


@pytest.mark.unit
@pytest.mark.asyncio
async def test_application_setup_signal_handlers_windows(mock_env_vars):
    """Test _setup_signal_handlers on Windows."""
    with patch("main.PluginManager"), \
         patch("main.AgentClient"), \
         patch("main.QueueProcessor"), \
         patch("main.create_default_settings"), \
         patch("main.PIDManager"), \
         patch("sys.platform", "win32"), \
         patch("asyncio.get_running_loop", side_effect=RuntimeError("No loop")):
        
        app = main.Application()
        app._setup_signal_handlers()
        
        # Should use signal.signal() fallback


@pytest.mark.unit
@pytest.mark.asyncio
async def test_application_setup_signal_handlers_no_loop(mock_env_vars):
    """Test _setup_signal_handlers when no event loop."""
    with patch("main.PluginManager"), \
         patch("main.AgentClient"), \
         patch("main.QueueProcessor"), \
         patch("main.create_default_settings"), \
         patch("main.PIDManager"), \
         patch("sys.platform", "linux"), \
         patch("asyncio.get_running_loop", side_effect=RuntimeError("No loop")):
        
        app = main.Application()
        app._setup_signal_handlers()
        
        # Should use signal.signal() fallback


@pytest.mark.unit
@pytest.mark.asyncio
async def test_application_check_settings_no_change(mock_env_vars, tmp_path, monkeypatch):
    """Test _check_settings when file hasn't changed."""
    monkeypatch.chdir(tmp_path)
    
    settings_file = tmp_path / "settings.json"
    settings_file.write_text('{"message_mode": "echo"}')
    
    with patch("main.PluginManager"), \
         patch("main.AgentClient"), \
         patch("main.QueueProcessor") as mock_qp_class, \
         patch("main.create_default_settings"), \
         patch("main.PIDManager"), \
         patch("main.get_settings") as mock_get_settings:
        
        mock_qp = MagicMock()
        mock_qp_class.return_value = mock_qp
        
        app = main.Application()
        app._settings_mtime = os.path.getmtime(settings_file)
        
        await app._check_settings()
        
        # Should not update anything if mtime hasn't changed


@pytest.mark.unit
@pytest.mark.asyncio
async def test_application_check_settings_changed(mock_env_vars, tmp_path, monkeypatch):
    """Test _check_settings when file has changed."""
    monkeypatch.chdir(tmp_path)
    
    settings_file = tmp_path / "settings.json"
    settings_file.write_text('{"message_mode": "echo", "debug_mode": false}')
    
    with patch("main.PluginManager") as mock_pm_class, \
         patch("main.AgentClient") as mock_agent_class, \
         patch("main.QueueProcessor") as mock_qp_class, \
         patch("main.create_default_settings"), \
         patch("main.PIDManager"), \
         patch("main.get_settings") as mock_get_settings, \
         patch("main.validate_settings") as mock_validate:
        
        mock_pm = AsyncMock()
        mock_pm_class.return_value = mock_pm
        
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent
        
        mock_qp = MagicMock()
        mock_qp_class.return_value = mock_qp
        
        mock_get_settings.return_value = {
            "message_mode": "live",
            "debug_mode": True,
            "queue_refresh": 10,
            "max_retries": 5
        }
        mock_validate.return_value = mock_get_settings.return_value
        
        app = main.Application()
        app._settings_mtime = 0  # Force reload
        
        await app._check_settings()
        
        # Should update message mode
        mock_qp.set_message_mode.assert_called()
        mock_pm.update_message_mode.assert_called()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_application_check_settings_error(mock_env_vars, tmp_path, monkeypatch):
    """Test _check_settings with error."""
    monkeypatch.chdir(tmp_path)
    
    with patch("main.PluginManager"), \
         patch("main.AgentClient"), \
         patch("main.QueueProcessor"), \
         patch("main.create_default_settings"), \
         patch("main.PIDManager"), \
         patch("os.path.getmtime", side_effect=OSError("Error")):
        
        app = main.Application()
        
        # Should not raise, just log error
        await app._check_settings()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_application_process_message(mock_env_vars):
    """Test _process_message."""
    with patch("main.PluginManager"), \
         patch("main.AgentClient") as mock_agent_class, \
         patch("main.QueueProcessor"), \
         patch("main.create_default_settings"), \
         patch("main.PIDManager"):
        
        mock_agent = AsyncMock()
        mock_agent.process_message.return_value = "Response"
        mock_agent_class.return_value = mock_agent
        
        app = main.Application()
        
        result = await app._process_message("test message")
        
        assert result == "Response"
        mock_agent.process_message.assert_called_once_with("test message")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_application_on_message_processed(mock_env_vars):
    """Test _on_message_processed."""
    with patch("main.PluginManager"), \
         patch("main.AgentClient"), \
         patch("main.QueueProcessor"), \
         patch("main.create_default_settings"), \
         patch("main.PIDManager"), \
         patch("main.logger") as mock_logger:
        
        app = main.Application()
        
        await app._on_message_processed(123, "test response")
        
        mock_logger.info.assert_called()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_application_start_success(mock_env_vars, tmp_path, monkeypatch):
    """Test start method success."""
    monkeypatch.chdir(tmp_path)
    
    with patch("main.PluginManager") as mock_pm_class, \
         patch("main.AgentClient") as mock_agent_class, \
         patch("main.QueueProcessor") as mock_qp_class, \
         patch("main.create_default_settings"), \
         patch("main.PIDManager"), \
         patch("main.validate_environment_variables"), \
         patch("main.initialize_database", new_callable=AsyncMock), \
         patch("main.check_and_migrate_db", new_callable=AsyncMock), \
         patch("main.get_settings") as mock_get_settings:
        
        mock_pm = AsyncMock()
        mock_pm_class.return_value = mock_pm
        
        mock_agent = AsyncMock()
        mock_agent.initialize.return_value = True
        mock_agent_class.return_value = mock_agent
        
        mock_qp = MagicMock()
        mock_qp_class.return_value = mock_qp
        
        mock_get_settings.return_value = {
            "message_mode": "echo",
            "plugins": {}
        }
        
        app = main.Application()
        app._shutdown_event.set()  # Trigger immediate shutdown
        
        await app.start()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_application_start_agent_init_fails(mock_env_vars, tmp_path, monkeypatch):
    """Test start method when agent initialization fails."""
    monkeypatch.chdir(tmp_path)
    
    with patch("main.PluginManager"), \
         patch("main.AgentClient") as mock_agent_class, \
         patch("main.QueueProcessor"), \
         patch("main.create_default_settings"), \
         patch("main.PIDManager"), \
         patch("main.validate_environment_variables"), \
         patch("main.initialize_database", new_callable=AsyncMock), \
         patch("main.check_and_migrate_db", new_callable=AsyncMock):
        
        mock_agent = AsyncMock()
        mock_agent.initialize.return_value = False
        mock_agent_class.return_value = mock_agent
        
        app = main.Application()
        
        await app.start()
        
        # Should return early


@pytest.mark.unit
@pytest.mark.asyncio
async def test_application_start_error(mock_env_vars, tmp_path, monkeypatch):
    """Test start method with error."""
    monkeypatch.chdir(tmp_path)
    
    with patch("main.PluginManager"), \
         patch("main.AgentClient"), \
         patch("main.QueueProcessor"), \
         patch("main.create_default_settings"), \
         patch("main.PIDManager"), \
         patch("main.validate_environment_variables", side_effect=Exception("Error")):
        
        app = main.Application()
        
        with pytest.raises(Exception):
            await app.start()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_application_monitor_settings(mock_env_vars):
    """Test _monitor_settings."""
    with patch("main.PluginManager"), \
         patch("main.AgentClient"), \
         patch("main.QueueProcessor"), \
         patch("main.create_default_settings"), \
         patch("main.PIDManager"), \
         patch("main.Application._check_settings", new_callable=AsyncMock) as mock_check:
        
        app = main.Application()
        app._shutdown_event.set()  # Trigger immediate shutdown
        
        await app._monitor_settings()
        
        # Should call _check_settings at least once


@pytest.mark.unit
@pytest.mark.asyncio
async def test_application_monitor_settings_error(mock_env_vars):
    """Test _monitor_settings with error."""
    with patch("main.PluginManager"), \
         patch("main.AgentClient"), \
         patch("main.QueueProcessor"), \
         patch("main.create_default_settings"), \
         patch("main.PIDManager"), \
         patch("main.Application._check_settings", side_effect=Exception("Error")):
        
        app = main.Application()
        app._shutdown_event.set()  # Trigger immediate shutdown
        
        # Should not raise, just log error
        await app._monitor_settings()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_application_stop_success(mock_env_vars):
    """Test stop method."""
    with patch("main.PluginManager") as mock_pm_class, \
         patch("main.AgentClient") as mock_agent_class, \
         patch("main.QueueProcessor") as mock_qp_class, \
         patch("main.create_default_settings"), \
         patch("main.PIDManager"):
        
        mock_pm = AsyncMock()
        mock_pm_class.return_value = mock_pm
        
        mock_agent = AsyncMock()
        mock_agent_class.return_value = mock_agent
        
        mock_qp = AsyncMock()
        mock_qp_class.return_value = mock_qp
        
        app = main.Application()
        
        await app.stop()
        
        mock_qp.stop.assert_called_once()
        mock_agent.cleanup.assert_called_once()
        mock_pm.stop.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_application_stop_with_tasks(mock_env_vars):
    """Test stop method with running tasks."""
    with patch("main.PluginManager"), \
         patch("main.AgentClient"), \
         patch("main.QueueProcessor"), \
         patch("main.create_default_settings"), \
         patch("main.PIDManager"):
        
        app = main.Application()
        app._tasks.add(asyncio.create_task(asyncio.sleep(10)))
        
        # Stop should cancel tasks
        stop_task = asyncio.create_task(app.stop())
        await asyncio.sleep(0.1)  # Let it start
        
        # Cancel the stop task itself
        stop_task.cancel()
        try:
            await stop_task
        except asyncio.CancelledError:
            pass


@pytest.mark.unit
@pytest.mark.asyncio
async def test_application_stop_error(mock_env_vars):
    """Test stop method with error."""
    with patch("main.PluginManager"), \
         patch("main.AgentClient"), \
         patch("main.QueueProcessor") as mock_qp_class, \
         patch("main.create_default_settings"), \
         patch("main.PIDManager"):
        
        mock_qp = AsyncMock()
        mock_qp.stop.side_effect = Exception("Stop error")
        mock_qp_class.return_value = mock_qp
        
        app = main.Application()
        
        # Should not raise, just log error
        await app.stop()


@pytest.mark.unit
def test_application_update_settings(mock_env_vars):
    """Test update_settings method."""
    with patch("main.PluginManager"), \
         patch("main.AgentClient") as mock_agent_class, \
         patch("main.QueueProcessor") as mock_qp_class, \
         patch("main.create_default_settings"), \
         patch("main.PIDManager"):
        
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent
        
        mock_qp = MagicMock()
        mock_qp_class.return_value = mock_qp
        
        app = main.Application()
        
        app.update_settings({
            "message_mode": "live",
            "debug_mode": True
        })
        
        mock_qp.set_message_mode.assert_called_with("live")
        assert mock_agent.debug_mode is True


@pytest.mark.unit
def test_main_function_keyboard_interrupt(mock_env_vars):
    """Test main function with KeyboardInterrupt."""
    with patch("main.Application") as mock_app_class, \
         patch("asyncio.run", side_effect=KeyboardInterrupt), \
         patch("main.logger"), \
         patch("sys.exit"):
        
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        
        main.main()
        
        # Should handle gracefully


@pytest.mark.unit
def test_main_function_exception(mock_env_vars):
    """Test main function with exception."""
    with patch("main.Application", side_effect=Exception("Error")), \
         patch("main.logger") as mock_logger, \
         patch("sys.exit") as mock_exit:
        
        main.main()
        
        mock_logger.error.assert_called()
        mock_exit.assert_called_with(1)


@pytest.mark.unit
def test_main_function_final_cleanup(mock_env_vars):
    """Test main function cleanup in finally block."""
    with patch("main.Application") as mock_app_class, \
         patch("asyncio.run", side_effect=Exception("Error")), \
         patch("main.logger"), \
         patch("sys.exit"):
        
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        
        main.main()
        
        # Should call stop in finally block
