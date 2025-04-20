"""Flask web application for the dashboard."""
import os
import json
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database.operations.shared import initialize_database, check_and_migrate_db, get_dashboard_stats
from database.operations.users import get_or_create_letta_user, get_or_create_platform_profile, update_letta_user, get_all_users
from database.operations.messages import insert_message, get_message_text, update_message_with_response, get_message_history
from database.operations.queue import add_to_queue, get_pending_queue_item, update_queue_status, get_all_queue_items, flush_all_queue_items, delete_queue_item as db_delete_queue_item
from common.logging import setup_logging
from common.config import (
    get_settings,
    validate_settings,
    save_settings,
)

# Get the project root directory and settings file path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
settings_file = os.path.join(project_root, 'settings.json')

def create_app(app_instance=None) -> Flask:
    """Create and configure the Flask application.
    
    Args:
        app_instance: The main application instance
        
    Returns:
        The configured Flask application
    """
    # Set up logging first
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Creating Flask application")
    
    app = Flask(__name__)
    
    # Set a secret key for session management
    app.secret_key = os.urandom(24)  # Generate a random secret key
    logger.debug("Generated secret key")
    
    # Store the application instance
    if app_instance:
        app.config['app_instance'] = app_instance
        logger.debug("Stored application instance")
    
    # Configure static files and templates with absolute paths
    app.static_folder = os.path.join(project_root, 'static')
    app.template_folder = os.path.join(project_root, 'templates')
    logger.debug(f"Set static folder to {app.static_folder}")
    logger.debug(f"Set template folder to {app.template_folder}")
    
    # Load settings using common module
    try:
        app.config['SETTINGS'] = get_settings(settings_file)
        logger.info("Loaded settings from file")
    except (FileNotFoundError, ValueError):
        logger.warning("Settings file not found or invalid, using defaults")
        app.config['SETTINGS'] = {
            'debug_mode': False,
            'queue_refresh': 5,
            'max_retries': 3,
            'message_mode': 'echo'  # Can be 'echo', 'listen', or 'live'
        }
    
    @app.route('/')
    def dashboard():
        """Render the main dashboard page."""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            logger.debug("Fetching dashboard stats")
            stats = loop.run_until_complete(get_dashboard_stats())
            return render_template('dashboard.html', stats=stats)
        finally:
            loop.close()
    
    @app.route('/users')
    def users():
        """Render the users page."""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            logger.debug("Fetching all users")
            users = loop.run_until_complete(get_all_users())
            return render_template('users.html', users=users)
        finally:
            loop.close()
    
    @app.route('/conversations')
    def conversations():
        """Render the conversations page."""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            logger.debug("Fetching message history")
            messages = loop.run_until_complete(get_message_history())
            return render_template('conversations.html', messages=messages)
        finally:
            loop.close()
    
    @app.route('/settings')
    def settings():
        """Render the settings page."""
        logger.debug("Rendering settings page")
        return render_template('settings.html', settings=app.config['SETTINGS'])
    
    @app.route('/settings/update', methods=['POST'])
    def update_settings():
        """Update application settings."""
        try:
            if request.is_json:
                settings = request.get_json()
            else:
                # Convert form data to appropriate types
                settings = {
                    'debug_mode': request.form.get('debug_mode', 'off') == 'on',
                    'queue_refresh': int(request.form.get('queue_refresh', '5')),
                    'max_retries': int(request.form.get('max_retries', '3')),
                    'message_mode': request.form.get('message_mode', 'echo')
                }
            
            # Update app config before validation to ensure proper types
            app.config['SETTINGS'].update(settings)
            
            # Validate and save settings
            validate_settings(settings)
            save_settings(settings, settings_file)
            
            app_instance = app.config.get('app_instance')
            if app_instance and hasattr(app_instance, 'update_settings'):
                app_instance.update_settings(settings)
            
            if request.is_json:
                return jsonify({"status": "success"}), 200
            else:
                flash('Settings updated successfully', 'success')
                return redirect(url_for('settings'))
        except ValueError as e:
            if request.is_json:
                return jsonify({"status": "error", "message": str(e)}), 400
            else:
                flash(str(e), 'error')
                return redirect(url_for('settings'))
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            if request.is_json:
                return jsonify({"status": "error", "message": "Internal server error"}), 500
            else:
                flash('An error occurred while updating settings', 'error')
                return redirect(url_for('settings'))
    
    @app.route('/queue')
    def queue():
        """Render the queue page."""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            logger.debug("Fetching all queue items")
            queue_items = loop.run_until_complete(get_all_queue_items())
            return render_template('queue.html', queue=queue_items)
        except Exception as e:
            logger.error(f"Error fetching queue items: {e}")
            return jsonify({"status": "error", "message": "Internal server error"}), 500
        finally:
            loop.close()
    
    @app.route('/retry/<int:queue_id>', methods=['POST'])
    def retry_queue_item(queue_id):
        """Retry processing a failed queue item."""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            logger.info(f"Retrying queue item {queue_id}")
            loop.run_until_complete(update_queue_status(queue_id, 'pending'))
            return redirect(url_for('queue'))
        finally:
            loop.close()
    
    @app.route('/queue/flush_all', methods=['POST'])
    def flush_all_queue():
        """Reset all pending and processing queue items to pending status."""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            current_mode = app.config['SETTINGS'].get('message_mode', 'echo')
            logger.info(f"Flushing all queue items in {current_mode} mode")
            success = loop.run_until_complete(flush_all_queue_items(current_mode))
            if not success:
                logger.warning("Cannot flush queue in listen mode")
                flash("Cannot flush queue in listen mode - switch to echo or live mode first", "warning")
            else:
                logger.info("Queue flushed successfully")
                flash("Queue flushed successfully", "success")
            return redirect(url_for('queue'))
        finally:
            loop.close()
    
    @app.route('/queue/delete/<int:queue_id>', methods=['POST'])
    def delete_queue_item_route(queue_id):
        """Delete a specific queue item."""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            logger.info(f"Deleting queue item {queue_id}")
            # Run the async operation
            success = loop.run_until_complete(db_delete_queue_item(queue_id))
            
            if success:
                logger.info(f"Queue item {queue_id} deleted successfully")
                flash('Queue item deleted successfully', 'success')
            else:
                logger.error(f"Failed to delete queue item {queue_id}")
                flash('Failed to delete queue item', 'error')
        except Exception as e:
            logger.error(f"Error deleting queue item {queue_id}: {str(e)}")
            flash(f'Error deleting queue item: {str(e)}', 'error')
        finally:
            loop.close()
        
        return redirect(url_for('queue'))
    
    @app.route('/queue/delete_all', methods=['POST'])
    def delete_all_queue_items():
        """Delete all queue items."""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            logger.info("Deleting all queue items")
            # Get all queue items
            queue_items = loop.run_until_complete(get_all_queue_items())
            
            # Delete each item
            for item in queue_items:
                logger.debug(f"Deleting queue item {item['id']}")
                loop.run_until_complete(db_delete_queue_item(item['id']))
            
            logger.info("All queue items deleted successfully")
            flash('All queue items deleted successfully', 'success')
        except Exception as e:
            logger.error(f"Error deleting queue items: {str(e)}")
            flash(f'Error deleting queue items: {str(e)}', 'error')
        finally:
            loop.close()
        
        return redirect(url_for('queue'))
    
    logger.info("Flask application created successfully")
    return app

# Create the Flask application instance
app = create_app() 