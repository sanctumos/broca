"""
Global pytest configuration and fixtures for the Broca2 test suite.

This module provides shared fixtures and configuration for all test types:
- Unit tests
- Integration tests
- End-to-end tests

Key features:
- Async test support with proper cleanup
- Database isolation for each test
- Mock external dependencies
- Test data factories
- Environment variable management
"""

import asyncio
import os

# Add the project root to Python path
import sys
import tempfile
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from pytest_mock import MockerFixture

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import project modules
from database.operations.shared import initialize_database


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def temp_db() -> AsyncGenerator[str, None]:
    """Create a temporary database for testing with proper cleanup."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name

    # Set the database path for the test
    original_db_path = os.environ.get("TEST_DB_PATH")
    os.environ["TEST_DB_PATH"] = db_path

    try:
        # Initialize the test database
        await initialize_database()
        yield db_path
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
        if original_db_path:
            os.environ["TEST_DB_PATH"] = original_db_path
        elif "TEST_DB_PATH" in os.environ:
            del os.environ["TEST_DB_PATH"]


@pytest.fixture
def mock_env_vars(mocker: MockerFixture) -> dict[str, str]:
    """Mock environment variables for testing."""
    env_vars = {
        "AGENT_ID": "test-agent-123",
        "LETTA_API_ENDPOINT": "http://localhost:8000",
        "LETTA_API_KEY": "test-api-key",
        "TELEGRAM_API_ID": "12345",
        "TELEGRAM_API_HASH": "test-hash",
        "TELEGRAM_PHONE": "+1234567890",
        "DEBUG_MODE": "true",
        "MESSAGE_MODE": "echo",
        "QUEUE_REFRESH": "5",
        "MAX_RETRIES": "3",
    }

    for key, value in env_vars.items():
        mocker.patch.dict(os.environ, {key: value})

    return env_vars


@pytest.fixture
def mock_letta_client(mocker: MockerFixture) -> MagicMock:
    """Mock the Letta client for testing."""
    mock_client = MagicMock()
    mock_client.send_message = AsyncMock(return_value={"id": "test-response-123"})
    mock_client.create_core_block = AsyncMock(return_value={"id": "test-block-123"})
    mock_client.delete_core_block = AsyncMock(return_value={"success": True})

    # Mock the get_letta_client function
    mocker.patch("runtime.core.letta_client.get_letta_client", return_value=mock_client)

    return mock_client


@pytest.fixture
def mock_telegram_client(mocker: MockerFixture) -> MagicMock:
    """Mock the Telegram client for testing."""
    mock_client = MagicMock()
    mock_client.send_message = AsyncMock()
    mock_client.send_typing_action = AsyncMock()
    mock_client.get_me = AsyncMock(return_value={"id": 12345, "username": "testbot"})

    return mock_client


@pytest.fixture
def mock_plugin_manager(mocker: MockerFixture) -> MagicMock:
    """Mock the plugin manager for testing."""
    mock_manager = MagicMock()
    mock_manager.load_plugin = AsyncMock()
    mock_manager.start_plugin = AsyncMock()
    mock_manager.stop_plugin = AsyncMock()
    mock_manager.get_plugin = MagicMock(return_value=None)
    mock_manager.get_all_plugins = MagicMock(return_value=[])

    return mock_manager


@pytest.fixture
def sample_message_data() -> dict[str, Any]:
    """Sample message data for testing."""
    return {
        "letta_user_id": 1,
        "platform_profile_id": 1,
        "role": "user",
        "message": "Hello, this is a test message",
        "timestamp": "2024-01-01T12:00:00Z",
        "platform": "telegram",
        "platform_user_id": "12345",
        "username": "testuser",
        "display_name": "Test User",
    }


@pytest.fixture
def sample_queue_item() -> dict[str, Any]:
    """Sample queue item data for testing."""
    return {
        "id": 1,
        "letta_user_id": 1,
        "message_id": 1,
        "status": "PENDING",
        "attempts": 0,
        "timestamp": "2024-01-01T12:00:00Z",
    }


@pytest.fixture
def sample_user_data() -> dict[str, Any]:
    """Sample user data for testing."""
    return {
        "letta_user_id": 1,
        "username": "testuser",
        "display_name": "Test User",
        "platform": "telegram",
        "platform_user_id": "12345",
        "created_at": "2024-01-01T12:00:00Z",
        "last_active": "2024-01-01T12:00:00Z",
        "is_active": True,
    }


@pytest.fixture
def async_timeout() -> int:
    """Default timeout for async operations in tests."""
    return 30


@pytest.fixture(autouse=True)
def setup_test_logging():
    """Setup test logging to avoid noise during testing."""
    import logging

    logging.getLogger().setLevel(logging.WARNING)


@pytest.fixture
def mock_file_system(mocker: MockerFixture) -> MagicMock:
    """Mock file system operations for testing."""
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.is_file.return_value = True
    mock_path.read_text.return_value = '{"test": "data"}'
    mock_path.write_text.return_value = None

    mocker.patch("pathlib.Path", return_value=mock_path)
    return mock_path


# Plugin testing utilities
@pytest.fixture
def mock_plugin_base():
    """Mock base plugin class for testing."""
    from plugins import Plugin

    class MockPlugin(Plugin):
        def __init__(self):
            self.is_running = False
            self.name = "mock_plugin"
            self.platform = "mock_platform"

        async def start(self) -> None:
            self.is_running = True

        async def stop(self) -> None:
            self.is_running = False

        def get_name(self) -> str:
            return self.name

        def get_platform(self) -> str:
            return self.platform

        def get_message_handler(self):
            return None

    return MockPlugin


# CLI testing utilities
@pytest.fixture
def mock_cli_args():
    """Mock CLI arguments for testing."""
    return {
        "command": "test",
        "json": False,
        "verbose": False,
    }


@pytest.fixture
def capture_cli_output(capsys):
    """Capture CLI output for testing."""

    def _capture():
        captured = capsys.readouterr()
        return captured.out, captured.err

    return _capture


# Database testing utilities
@pytest.fixture
async def clean_database(temp_db: str):
    """Ensure database is clean before each test."""
    # This fixture will be used to clean the database before each test
    # The actual cleanup is handled by the temp_db fixture
    yield temp_db


# Integration testing utilities
@pytest.fixture
def mock_external_apis(mocker: MockerFixture):
    """Mock external API calls for integration tests."""
    # Mock HTTP requests
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}
    mock_response.text = '{"success": true}'

    mocker.patch("httpx.AsyncClient.get", return_value=mock_response)
    mocker.patch("httpx.AsyncClient.post", return_value=mock_response)

    return mock_response


# E2E testing utilities
@pytest.fixture
def test_config():
    """Test configuration for E2E tests."""
    return {
        "message_mode": "echo",
        "debug_mode": True,
        "queue_refresh": 1,
        "max_retries": 1,
        "test_timeout": 60,
    }


@pytest.fixture
async def test_application():
    """Create a test application instance for E2E testing."""
    # This will be implemented when we scaffold the E2E tests
    # For now, return a mock
    return MagicMock()


# Test data factories
class TestDataFactory:
    """Factory for creating test data."""

    @staticmethod
    def create_user(**kwargs) -> dict[str, Any]:
        """Create a test user with default values."""
        defaults = {
            "username": "testuser",
            "display_name": "Test User",
            "platform": "telegram",
            "platform_user_id": "12345",
            "is_active": True,
        }
        defaults.update(kwargs)
        return defaults

    @staticmethod
    def create_message(**kwargs) -> dict[str, Any]:
        """Create a test message with default values."""
        defaults = {
            "role": "user",
            "message": "Test message",
            "timestamp": "2024-01-01T12:00:00Z",
            "processed": False,
        }
        defaults.update(kwargs)
        return defaults

    @staticmethod
    def create_queue_item(**kwargs) -> dict[str, Any]:
        """Create a test queue item with default values."""
        defaults = {
            "status": "PENDING",
            "attempts": 0,
            "timestamp": "2024-01-01T12:00:00Z",
        }
        defaults.update(kwargs)
        return defaults


@pytest.fixture
def test_data_factory():
    """Provide access to test data factory."""
    return TestDataFactory


# Async test utilities
@pytest_asyncio.fixture
async def async_test_context():
    """Provide async test context with proper cleanup."""
    # Setup
    context = {"setup": True}
    yield context

    # Cleanup
    context["setup"] = False


# Performance testing utilities
@pytest.fixture
def performance_timer():
    """Timer for performance testing."""
    import time

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = time.time()

        def stop(self):
            self.end_time = time.time()

        @property
        def elapsed(self) -> float:
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return 0.0

    return Timer()


# Test markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "e2e: mark test as an end-to-end test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "async: mark test as async")
    config.addinivalue_line("markers", "database: mark test as requiring database")
    config.addinivalue_line(
        "markers", "external: mark test as requiring external services"
    )
