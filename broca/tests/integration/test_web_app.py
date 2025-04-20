"""Integration tests for web/app.py."""

import os
import json
import logging
import pytest
import tempfile
from unittest.mock import patch, Mock
from web.app import create_app, settings_file as app_settings_file

@pytest.fixture
def test_settings():
    """Create test settings."""
    return {
        'debug_mode': False,
        'queue_refresh': 5,
        'max_retries': 3,
        'message_mode': 'echo'
    }

@pytest.fixture
def mock_db_functions():
    """Mock database functions."""
    with patch('database.operations.shared.get_dashboard_stats', return_value={'total_messages': 100}), \
         patch('database.operations.users.get_all_users', return_value=[]), \
         patch('database.operations.messages.get_message_history', return_value=[]), \
         patch('database.operations.queue.get_all_queue_items', return_value=[]), \
         patch('database.operations.queue.update_queue_status', return_value=None), \
         patch('database.operations.queue.flush_all_queue_items', return_value=True), \
         patch('database.operations.queue.delete_queue_item', return_value=True):
        yield

@pytest.fixture
def temp_settings_file(test_settings):
    """Create a temporary settings file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(test_settings, f)
        f.flush()  # Ensure all data is written
        return f.name

@pytest.fixture
def app(temp_settings_file, mock_db_functions):
    """Create app instance with real settings file."""
    # Store original settings file path
    original_settings_file = app_settings_file
    
    try:
        # Use our test settings file
        import web.app
        web.app.settings_file = temp_settings_file
        
        app = create_app()
        app.config['TESTING'] = True
        
        yield app
    finally:
        # Restore original settings file path
        web.app.settings_file = original_settings_file
        
        # Clean up test settings file
        try:
            os.unlink(temp_settings_file)
        except OSError:
            pass

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

def test_app_loads_real_settings(app, test_settings):
    """Test that app loads settings from real file."""
    with app.app_context():
        # Reset the settings cache to force a reload
        from common.config import _reset_settings_cache
        _reset_settings_cache()
        
        # Reload settings
        app.config['SETTINGS'] = test_settings.copy()
        assert app.config['SETTINGS'] == test_settings

def test_settings_update_persists(client, temp_settings_file):
    """Test that settings updates are persisted to file."""
    new_settings = {
        'debug_mode': 'on',
        'queue_refresh': '10',
        'max_retries': '5',
        'message_mode': 'live'
    }
    
    response = client.post('/settings/update', data=new_settings)
    assert response.status_code == 302
    
    # Verify settings were saved to file
    with open(temp_settings_file, 'r') as f:
        saved_settings = json.load(f)
        assert saved_settings['debug_mode'] is True
        assert saved_settings['queue_refresh'] == 10
        assert saved_settings['max_retries'] == 5
        assert saved_settings['message_mode'] == 'live'
    
    # Verify settings are reflected in subsequent requests
    response = client.get('/settings')
    assert response.status_code == 200
    response_text = response.get_data(as_text=True)
    assert 'value="10"' in response_text  # queue_refresh value
    assert 'value="5"' in response_text   # max_retries value
    assert 'value="live" selected' in response_text  # message_mode value

def test_logging_to_file(app, tmp_path):
    """Test that logs are written to file when configured."""
    log_file = tmp_path / "test.log"
    
    # Configure logging to write to file
    logging.basicConfig(
        filename=str(log_file),
        level=logging.DEBUG,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True
    )
    
    # Create a new client and make some requests
    client = app.test_client()
    
    client.get('/')
    client.get('/settings')
    client.post('/queue/flush_all')
    
    # Flush any buffered log messages
    for handler in logging.root.handlers:
        handler.flush()
    
    # Check log file contents
    with open(log_file, 'r') as f:
        log_contents = f.read()
        assert "Fetching dashboard stats" in log_contents
        assert "Rendering settings page" in log_contents
        assert "Flushing all queue items" in log_contents

def test_settings_update_with_app_instance(app, client, temp_settings_file):
    """Test settings update with running app instance."""
    # Create a mock app instance
    class MockAppInstance:
        def update_settings(self, settings):
            self.settings = settings
    
    mock_instance = MockAppInstance()
    app.config['app_instance'] = mock_instance
    
    # Update settings
    new_settings = {
        'debug_mode': 'on',
        'queue_refresh': '10',
        'max_retries': '5',
        'message_mode': 'live'
    }
    
    response = client.post('/settings/update', data=new_settings)
    assert response.status_code == 302
    
    # Verify settings were updated in app instance
    assert mock_instance.settings['debug_mode'] is True
    assert mock_instance.settings['queue_refresh'] == 10
    assert mock_instance.settings['max_retries'] == 5
    assert mock_instance.settings['message_mode'] == 'live' 