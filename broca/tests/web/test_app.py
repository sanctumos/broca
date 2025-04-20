"""Unit tests for web/app.py."""

import os
import json
import logging
import pytest
from unittest.mock import patch, Mock, MagicMock, mock_open
from flask import Flask
from web.app import create_app

@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    return {
        'debug_mode': False,
        'queue_refresh': 5,
        'max_retries': 3,
        'message_mode': 'echo'
    }

@pytest.fixture
def mock_stats():
    """Mock dashboard stats for testing."""
    return {
        'total_messages': 100,
        'active_users': 10,
        'queue_items': 5
    }

@pytest.fixture
def mock_db_functions():
    """Mock database functions."""
    with patch('database.operations.shared.get_dashboard_stats', return_value=Mock()), \
         patch('database.operations.users.get_all_users', return_value=Mock()), \
         patch('database.operations.messages.get_message_history', return_value=Mock()), \
         patch('database.operations.queue.get_all_queue_items', return_value=Mock()), \
         patch('database.operations.queue.update_queue_status', return_value=Mock()), \
         patch('database.operations.queue.flush_all_queue_items', return_value=True), \
         patch('database.operations.queue.delete_queue_item', return_value=True):
        yield

@pytest.fixture
def app_with_mocked_settings(mock_settings, mock_db_functions):
    """Create app instance with mocked settings."""
    with patch('web.app.get_settings', return_value=mock_settings):
        app = create_app()
        app.config['TESTING'] = True
        app.config['APPLICATION_ROOT'] = '/'
        return app

@pytest.fixture
def client(app_with_mocked_settings):
    """Create a test client."""
    return app_with_mocked_settings.test_client()

@pytest.fixture
def app_instance():
    """Create a mock app instance."""
    class MockAppInstance:
        def update_settings(self, settings):
            self.settings = settings
    
    return MockAppInstance()

def test_app_creation_logging_setup():
    """Test that logging is properly set up during app creation."""
    with patch('web.app.setup_logging') as mock_setup_logging, \
         patch('web.app.get_settings') as mock_get_settings, \
         patch('database.operations.shared.get_dashboard_stats', return_value=Mock()):
        mock_get_settings.return_value = {}
        create_app()
        mock_setup_logging.assert_called_once()

def test_app_creation_with_settings_file(mock_settings):
    """Test app creation with valid settings file."""
    with patch('web.app.get_settings', return_value=mock_settings) as mock_get_settings, \
         patch('database.operations.shared.get_dashboard_stats', return_value=Mock()):
        app = create_app()
        mock_get_settings.assert_called_once()
        assert app.config['SETTINGS'] == mock_settings

def test_app_creation_with_missing_settings():
    """Test app creation with missing settings file."""
    with patch('web.app.get_settings', side_effect=FileNotFoundError), \
         patch('database.operations.shared.get_dashboard_stats', return_value=Mock()):
        app = create_app()
        assert app.config['SETTINGS'] == {
            'debug_mode': False,
            'queue_refresh': 5,
            'max_retries': 3,
            'message_mode': 'echo'
        }

def test_app_creation_with_invalid_settings():
    """Test app creation with invalid settings file."""
    with patch('web.app.get_settings', side_effect=ValueError), \
         patch('database.operations.shared.get_dashboard_stats', return_value=Mock()):
        app = create_app()
        assert app.config['SETTINGS'] == {
            'debug_mode': False,
            'queue_refresh': 5,
            'max_retries': 3,
            'message_mode': 'echo'
        }

def test_settings_update(client, tmp_path):
    """Test settings update endpoint."""
    test_settings_file = tmp_path / "test_settings.json"
    
    with patch('web.app.settings_file', str(test_settings_file)):
        response = client.post('/settings/update', data={
            'debug_mode': 'on',
            'queue_refresh': '10',
            'max_retries': '5',
            'message_mode': 'live'
        })
        
        assert response.status_code == 302  # Redirect
        
        # Verify settings were saved
        with open(test_settings_file, 'r') as f:
            saved_settings = json.load(f)
            assert saved_settings['debug_mode'] is True
            assert saved_settings['queue_refresh'] == 10
            assert saved_settings['max_retries'] == 5
            assert saved_settings['message_mode'] == 'live'

def test_settings_update_error_handling(client):
    """Test error handling in settings update."""
    with patch('builtins.open', side_effect=PermissionError), \
         patch('jinja2.loaders.FileSystemLoader.get_source', return_value=('{% with messages = get_flashed_messages() %}{% if messages %}{% for message in messages %}{{ message }}{% endfor %}{% endif %}{% endwith %}', '', lambda: False)):
        response = client.post('/settings/update', data={
            'debug_mode': 'on',
            'queue_refresh': '10',
            'max_retries': '5',
            'message_mode': 'live'
        }, follow_redirects=True)
        
        assert b'Failed to save settings' in response.data

def test_logging_in_routes(client, caplog, mock_stats):
    """Test that routes properly log their actions."""
    with caplog.at_level(logging.DEBUG), \
         patch('database.operations.shared.get_dashboard_stats', return_value=mock_stats):
        client.get('/')
        assert "Fetching dashboard stats" in caplog.text
        
        client.get('/users')
        assert "Fetching all users" in caplog.text
        
        client.get('/conversations')
        assert "Fetching message history" in caplog.text
        
        client.get('/settings')
        assert "Rendering settings page" in caplog.text

def test_queue_operations_logging(client, caplog):
    """Test logging in queue operations."""
    with caplog.at_level(logging.INFO), \
         patch('web.app.update_queue_status', return_value=True) as mock_update_status, \
         patch('web.app.get_all_queue_items', return_value=[{'id': 1}]), \
         patch('web.app.db_delete_queue_item', return_value=True) as mock_delete_item, \
         patch('web.app.flush_all_queue_items', return_value=True) as mock_flush_all, \
         patch('flask.render_template', return_value=''):  # Mock template rendering
        
        # Test queue flush
        response = client.post('/queue/flush_all')
        assert response.status_code == 302  # Redirect
        assert "Flushing all queue items" in caplog.text
        mock_flush_all.assert_called_once_with('echo')  # Default mode is 'echo'
        
        # Test queue item retry
        response = client.post('/retry/1')
        assert response.status_code == 302  # Redirect
        assert "Retrying queue item 1" in caplog.text
        mock_update_status.assert_called_once_with(1, 'pending')
        
        # Test queue item deletion
        response = client.post('/queue/delete/1')
        assert response.status_code == 302  # Redirect
        assert "Deleting queue item 1" in caplog.text
        mock_delete_item.assert_called_once_with(1)
        
        # Test all queue items deletion
        response = client.post('/queue/delete_all')
        assert response.status_code == 302  # Redirect
        assert "Deleting all queue items" in caplog.text

def test_app_creation_with_app_instance():
    """Test app creation with an app instance."""
    mock_instance = Mock()
    with patch('web.app.get_settings') as mock_get_settings:
        mock_get_settings.return_value = {}
        app = create_app(app_instance=mock_instance)
        assert app.config['app_instance'] == mock_instance

def test_settings_update_with_invalid_values():
    """Test settings update with invalid values."""
    with patch('web.app.get_settings', return_value={}), \
         patch('jinja2.loaders.FileSystemLoader.get_source', return_value=('{% with messages = get_flashed_messages() %}{% if messages %}{% for message in messages %}{{ message }}{% endfor %}{% endif %}{% endwith %}', '', lambda: False)):
        app = create_app()
        client = app.test_client()
        
        # Test with invalid queue_refresh value
        response = client.post('/settings/update', data={
            'debug_mode': 'on',
            'queue_refresh': 'invalid',
            'max_retries': '5',
            'message_mode': 'live'
        }, follow_redirects=True)
        assert b'invalid literal for int() with base 10:' in response.data

def test_queue_operations_error_handling(client, caplog):
    """Test error handling in queue operations."""
    with caplog.at_level(logging.INFO), \
         patch('web.app.update_queue_status', side_effect=ValueError("Test error")), \
         patch('web.app.get_all_queue_items', return_value=[{'id': 1}]), \
         patch('web.app.db_delete_queue_item', side_effect=Exception("Delete error")), \
         patch('web.app.flush_all_queue_items', return_value=False), \
         patch('flask.render_template', return_value=''), \
         patch('web.app.flash') as mock_flash:  # Mock flash with correct import path
        
        # Test queue flush failure
        response = client.post('/queue/flush_all')
        assert response.status_code == 302
        assert "Cannot flush queue in listen mode" in caplog.text
        mock_flash.assert_called_with("Cannot flush queue in listen mode - switch to echo or live mode first", "warning")
        
        # Test queue item retry error
        caplog.clear()
        try:
            client.post('/retry/1')
        except ValueError as e:
            assert str(e) == "Test error"
            assert "Retrying queue item 1" in caplog.text
        
        # Test queue item deletion error
        caplog.clear()
        response = client.post('/queue/delete/1')
        assert response.status_code == 302
        assert "Error deleting queue item" in caplog.text
        mock_flash.assert_called_with("Error deleting queue item: Delete error", "error")
        
        # Test all queue items deletion error
        caplog.clear()
        response = client.post('/queue/delete_all')
        assert response.status_code == 302
        assert "Error deleting queue items" in caplog.text
        mock_flash.assert_called_with("Error deleting queue items: Delete error", "error")

def test_queue_delete_item_failure(client, caplog):
    """Test queue item deletion when the operation fails."""
    with caplog.at_level(logging.INFO), \
         patch('web.app.db_delete_queue_item', return_value=False), \
         patch('flask.render_template', return_value=''):
        
        response = client.post('/queue/delete/1')
        assert response.status_code == 302
        assert "Failed to delete queue item" in caplog.text

def test_queue_delete_all_with_empty_queue(client, caplog):
    """Test deleting all queue items when queue is empty."""
    with caplog.at_level(logging.INFO), \
         patch('web.app.get_all_queue_items', return_value=[]), \
         patch('flask.render_template', return_value=''):
        
        response = client.post('/queue/delete_all')
        assert response.status_code == 302
        assert "All queue items deleted successfully" in caplog.text

@patch('web.app.save_settings')
def test_settings_update_with_app_instance(mock_save_settings, client):
    """Test settings update with app instance."""
    settings = {
        'debug_mode': True,
        'queue_refresh': 10,
        'max_retries': 5,
        'message_mode': 'echo'
    }
    
    mock_app_instance = Mock()
    
    with client.application.app_context():
        client.application.config['app_instance'] = mock_app_instance
        with patch('web.app.settings_file', 'settings.json'):
            response = client.post('/settings/update', data=json.dumps(settings), content_type='application/json')
            assert response.status_code == 200
            assert response.json == {"status": "success"}
            
            mock_save_settings.assert_called_once_with(settings, 'settings.json')
            mock_app_instance.update_settings.assert_called_once_with(settings)

@patch('web.app.get_all_queue_items')
def test_queue_operations_with_asyncio_error(mock_get_items, client, caplog):
    """Test handling of asyncio errors in queue operations."""
    mock_get_items.side_effect = RuntimeError("Asyncio error")
    
    with caplog.at_level(logging.ERROR):
        response = client.get('/queue')
        assert response.status_code == 500
        assert "Error fetching queue items" in caplog.text

@patch('web.app.save_settings')
@patch('web.app.validate_settings')
def test_settings_update_validation_error(mock_validate_settings, mock_save_settings, client):
    """Test settings update when validation fails."""
    settings = {
        'debug_mode': 'invalid',  # Should be boolean
        'queue_refresh': 'invalid',  # Should be integer
        'max_retries': 'invalid',  # Should be integer
        'message_mode': 'invalid'  # Should be one of valid modes
    }
    
    mock_validate_settings.side_effect = ValueError("Invalid settings")
    mock_app_instance = Mock()
    
    with client.application.app_context():
        with patch.dict('flask.current_app.config', {'app_instance': mock_app_instance}):
            response = client.post('/settings/update', json=settings)
            assert response.status_code == 400
            assert response.json == {"status": "error", "message": "Invalid settings"}
            
            mock_validate_settings.assert_called_once_with(settings)
            mock_save_settings.assert_not_called()
            assert not mock_app_instance.update_settings.called 