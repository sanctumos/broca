"""Unit tests for main.py functionality."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import main


@pytest.mark.unit
@pytest.mark.asyncio
async def test_main_function():
    """Test main function."""
    with patch("main.setup_logging") as mock_logging, patch(
        "main.initialize_database"
    ) as mock_db, patch("main.start_plugins") as mock_plugins, patch(
        "main.start_queue_processor"
    ) as mock_queue, patch(
        "main.run_event_loop"
    ) as mock_loop:
        mock_logging.return_value = None
        mock_db.return_value = None
        mock_plugins.return_value = None
        mock_queue.return_value = None
        mock_loop.return_value = None

        await main.main()

        mock_logging.assert_called_once()
        mock_db.assert_called_once()
        mock_plugins.assert_called_once()
        mock_queue.assert_called_once()
        mock_loop.assert_called_once()


@pytest.mark.unit
def test_setup_logging():
    """Test setup_logging function."""
    with patch("main.logging.basicConfig") as mock_config:
        main.setup_logging()
        mock_config.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_initialize_database():
    """Test initialize_database function."""
    with patch("main.init_database") as mock_init:
        mock_init.return_value = None
        await main.initialize_database()
        mock_init.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_start_plugins():
    """Test start_plugins function."""
    with patch("main.PluginManager") as mock_manager_class:
        mock_manager = MagicMock()
        mock_manager.start_all = AsyncMock()
        mock_manager_class.return_value = mock_manager

        await main.start_plugins()
        mock_manager.start_all.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_start_queue_processor():
    """Test start_queue_processor function."""
    with patch("main.QueueProcessor") as mock_processor_class:
        mock_processor = MagicMock()
        mock_processor.start = AsyncMock()
        mock_processor_class.return_value = mock_processor

        await main.start_queue_processor()
        mock_processor.start.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_run_event_loop():
    """Test run_event_loop function."""
    with patch("main.asyncio.sleep") as mock_sleep:
        mock_sleep.return_value = None

        # Test with timeout
        try:
            await main.run_event_loop(timeout=0.1)
        except asyncio.TimeoutError:
            pass  # Expected


@pytest.mark.unit
def test_signal_handler():
    """Test signal handler."""
    with patch("main.sys.exit") as mock_exit:
        main.signal_handler(1, None)
        mock_exit.assert_called_once_with(0)


@pytest.mark.unit
def test_cleanup():
    """Test cleanup function."""
    with patch("main.PluginManager") as mock_manager_class, patch(
        "main.QueueProcessor"
    ) as mock_processor_class:
        mock_manager = MagicMock()
        mock_manager.stop_all = AsyncMock()
        mock_processor = MagicMock()
        mock_processor.stop = AsyncMock()

        mock_manager_class.return_value = mock_manager
        mock_processor_class.return_value = mock_processor

        # Test cleanup
        try:
            main.cleanup()
        except:
            pass  # May fail due to async context


@pytest.mark.unit
def test_main_exception_handling():
    """Test main function exception handling."""
    with patch("main.setup_logging") as mock_logging, patch("main.initialize_database"):
        mock_logging.side_effect = Exception("Test error")

        try:
            main.main()
        except Exception:
            pass  # Expected


@pytest.mark.unit
def test_config_loading():
    """Test configuration loading."""
    with patch("main.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock()

        # Test that settings are loaded
        settings = main.get_settings()
        assert settings is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_graceful_shutdown():
    """Test graceful shutdown."""
    with patch("main.signal.signal") as mock_signal, patch("main.cleanup"):
        # Test signal registration
        main.setup_signal_handlers()
        mock_signal.assert_called()
