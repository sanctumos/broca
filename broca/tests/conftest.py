"""Test configuration and shared fixtures."""

import os
import sys
import pytest

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@pytest.fixture
def mock_letta_client():
    """Mock Letta client for testing."""
    class MockLettaClient:
        async def send_message(self, *args, **kwargs):
            return {"status": "success"}
        
        async def get_response(self, *args, **kwargs):
            return {"response": "test response"}
    
    return MockLettaClient()

@pytest.fixture
def test_db():
    """Create a test database."""
    return {} 