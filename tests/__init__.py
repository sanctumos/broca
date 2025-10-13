"""
Broca2 Test Suite

This package contains comprehensive tests for the Broca2 system:
- Unit tests for individual components
- Integration tests for component interactions
- End-to-end tests for complete workflows
- Test utilities and fixtures
- Performance and error handling tests

Test Structure:
- tests/unit/: Unit tests for individual components
- tests/integration/: Integration tests for component interactions
- tests/e2e/: End-to-end tests for complete workflows
- tests/utils/: Test utilities and helpers
- tests/fixtures/: Reusable test fixtures

Usage:
    # Run all tests
    pytest

    # Run unit tests only
    pytest tests/unit/

    # Run integration tests only
    pytest tests/integration/

    # Run end-to-end tests only
    pytest tests/e2e/

    # Run with coverage
    pytest --cov=. --cov-report=html

    # Run specific test
    pytest tests/unit/runtime/test_core.py::TestQueueProcessor::test_queue_processor_start
"""

# Test configuration
import asyncio
import os
import sys
from pathlib import Path

import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set test environment variables
os.environ.setdefault("TESTING", "true")
os.environ.setdefault("DEBUG_MODE", "true")
os.environ.setdefault("MESSAGE_MODE", "echo")


# Configure asyncio for testing
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


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


__version__ = "1.0.0"
__author__ = "Sanctum OS"
__description__ = "Comprehensive test suite for Broca2 system"
