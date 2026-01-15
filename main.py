"""
Main application entry point.

Copyright (C) 2024 Sanctum OS

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import asyncio
import atexit
import json
import logging
import os
import signal
import sys
from pathlib import Path

import psutil
from dotenv import load_dotenv

from common.config import (
    get_config_manager,
    get_env_var,
    get_settings,
    validate_environment_variables,
)
from common.logging import setup_logging
from database.operations.shared import check_and_migrate_db, initialize_database
from runtime.core.agent import AgentClient
from runtime.core.plugin import PluginManager
from runtime.core.queue import QueueProcessor

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def create_default_settings() -> None:
    """Create default settings file if it doesn't exist or is invalid.

    This function handles the following cases:
    1. File doesn't exist - create with defaults
    2. File exists but is empty - recreate with defaults
    3. File exists but contains invalid JSON - recreate with defaults
    4. File exists and is valid JSON - leave it alone
    """
    settings_path = Path("settings.json")
    default_settings = {
        "debug_mode": False,
        "queue_refresh": 5,
        "max_retries": 3,
        "message_mode": "live",
    }

    should_create = False

    if not settings_path.exists():
        should_create = True
        logger.info("Settings file does not exist, creating default...")
    else:
        # File exists, check if it's valid JSON
        try:
            content = settings_path.read_text().strip()
            if not content:
                # Empty file
                should_create = True
                logger.warning("Settings file is empty, recreating with defaults...")
            else:
                # Try to parse as JSON
                json.loads(content)
                # If we get here, file is valid JSON - don't recreate
        except json.JSONDecodeError:
            should_create = True
            logger.warning(
                "Settings file contains invalid JSON, recreating with defaults..."
            )
        except Exception as e:
            should_create = True
            logger.warning(
                f"Failed to read settings file ({e}), recreating with defaults..."
            )

    if should_create:
        with open(settings_path, "w") as f:
            json.dump(default_settings, f, indent=4)
        logger.info("Created default settings.json file")


class PIDManager:
    """Manages PID file creation and cleanup with proper signal handling."""

    def __init__(self, instance_dir: str | None = None):
        """Initialize PID manager.

        Args:
            instance_dir: Directory for PID files. If None, uses 'run' directory in project root.
        """
        if instance_dir is None:
            instance_dir = os.path.join(os.getcwd(), "run")

        self.pid_file = os.path.join(instance_dir, "broca.pid")
        self.lock_file = os.path.join(instance_dir, "broca.lock")
        self.pid = os.getpid()
        self._cleanup_registered = False

    def create_pid_file(self) -> None:
        """Create PID file and register cleanup handlers."""
        # Create run directory if it doesn't exist
        os.makedirs(os.path.dirname(self.pid_file), exist_ok=True)

        # Check if PID file exists and if process is still running
        if os.path.exists(self.pid_file):
            if self.is_process_running(self.pid_file):
                raise RuntimeError(
                    f"Another instance is already running (PID file exists: {self.pid_file})"
                )
            else:
                # Stale PID file - remove it
                logger.warning(f"Removing stale PID file: {self.pid_file}")
                try:
                    os.remove(self.pid_file)
                except OSError:
                    pass

        # Write PID file
        with open(self.pid_file, "w") as f:
            f.write(str(self.pid))

        logger.debug(f"Created PID file: {self.pid_file} (PID: {self.pid})")

        # Register cleanup handlers (only once)
        if not self._cleanup_registered:
            atexit.register(self.cleanup)
            self._cleanup_registered = True

    def cleanup(self) -> None:
        """Clean up PID and lock files."""
        try:
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
                logger.debug(f"Removed PID file: {self.pid_file}")
            if os.path.exists(self.lock_file):
                os.remove(self.lock_file)
                logger.debug(f"Removed lock file: {self.lock_file}")
        except OSError as e:
            logger.warning(f"Failed to remove PID/lock files: {e}")

    @staticmethod
    def is_process_running(pid_file: str) -> bool:
        """Check if the process in PID file is still running.

        Args:
            pid_file: Path to PID file

        Returns:
            True if process is running, False otherwise
        """
        if not os.path.exists(pid_file):
            return False

        try:
            with open(pid_file) as f:
                pid = int(f.read().strip())
            return psutil.pid_exists(pid)
        except (ValueError, OSError, psutil.NoSuchProcess):
            return False


class Application:
    """Main application class that coordinates all components."""

    def __init__(self):
        """Initialize the application components."""
        # Initialize plugin manager first
        self.plugin_manager = PluginManager()

        # Initialize other components
        self.agent = AgentClient()

        # Initialize queue processor with plugin manager
        self.queue_processor = QueueProcessor(
            message_processor=self._process_message, plugin_manager=self.plugin_manager
        )

        self._settings_file = "settings.json"
        self._settings_mtime = 0
        self._shutdown_event = asyncio.Event()
        self._tasks = set()

        # Initialize unified configuration manager
        self.config_manager = get_config_manager(self._settings_file)

        # Subscribe to configuration changes
        self.config_manager.subscribe("message_mode", self._on_message_mode_change)
        self.config_manager.subscribe("debug_mode", self._on_debug_mode_change)
        self.config_manager.subscribe(
            "queue_processor.max_concurrent", self._on_max_concurrent_change
        )

        # Create default settings if needed
        create_default_settings()

        # Initialize PID manager
        self.pid_manager = PIDManager()
        try:
            self.pid_manager.create_pid_file()
        except RuntimeError as e:
            logger.error(f"❌ {e}")
            raise

        # Signal handlers will be set up in start() after event loop is running

    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown.

        This must be called after the event loop is running.
        Uses async signal handlers on Unix-like systems for better
        integration with asyncio, with fallback to signal.signal().
        """

        def signal_handler(signum=None):
            """Handle shutdown signals."""
            logger.info(
                f"Received signal {signum or 'SIGINT/SIGTERM'}, initiating graceful shutdown..."
            )
            # Clean up PID file on signal
            if hasattr(self, "pid_manager"):
                self.pid_manager.cleanup()
            self._shutdown_event.set()

        # Get the running event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No event loop running, fall back to signal.signal()
            if sys.platform != "win32":
                signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s))
                signal.signal(signal.SIGINT, lambda s, f: signal_handler(s))
            else:
                signal.signal(signal.SIGINT, lambda s, f: signal_handler(s))
            return

        # Use async signal handlers on Unix-like systems
        if sys.platform != "win32":
            try:
                loop.add_signal_handler(signal.SIGTERM, signal_handler, signal.SIGTERM)
                loop.add_signal_handler(signal.SIGINT, signal_handler, signal.SIGINT)
                logger.debug("Registered async signal handlers for SIGTERM and SIGINT")
            except NotImplementedError:
                # Fallback if add_signal_handler is not available
                signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s))
                signal.signal(signal.SIGINT, lambda s, f: signal_handler(s))
                logger.debug("Fell back to signal.signal() for signal handlers")
        else:
            # Windows: use signal.signal() for SIGINT only (SIGTERM not available)
            signal.signal(signal.SIGINT, lambda s, f: signal_handler(s))
            logger.debug("Registered signal handler for SIGINT on Windows")

    def _on_message_mode_change(self, old_value, new_value) -> None:
        """Handle message mode configuration changes."""
        logger.info(f"Updating message mode from {old_value} to {new_value}")
        if self.queue_processor:
            self.queue_processor.set_message_mode(new_value)
            logger.info(f"🔵 Message processing mode changed to: {new_value.upper()}")
        # Note: Plugin updates handled asynchronously in _monitor_settings

    def _on_debug_mode_change(self, old_value, new_value) -> None:
        """Handle debug mode configuration changes."""
        if hasattr(self, "agent") and self.agent:
            self.agent.debug_mode = new_value
            logger.info(f"Debug mode {'enabled' if new_value else 'disabled'}")

    def _on_max_concurrent_change(self, old_value, new_value) -> None:
        """Handle max concurrent configuration changes."""
        logger.info(
            f"Queue processor max_concurrent changed from {old_value} to {new_value}. "
            "Note: This requires queue processor restart to take effect."
        )

    async def _check_settings(self):
        """Check if settings file has been modified (legacy method, now uses config_manager)."""
        # ConfigurationManager handles reloading automatically
        # This method is kept for backward compatibility
        try:
            current_mtime = os.path.getmtime(self._settings_file)
            if current_mtime > self._settings_mtime:
                logger.info(
                    "Settings file modified, reloading via ConfigurationManager..."
                )
                self.config_manager.reload()

                # Update plugins that support message mode changes
                settings = self.config_manager.get_typed()
                if self.plugin_manager:
                    await self.plugin_manager.update_message_mode(settings.message_mode)
                    logger.info(
                        f"🔵 Plugin message modes updated to: {settings.message_mode.upper()}"
                    )

                self._settings_mtime = current_mtime
                logger.info("Settings reloaded successfully")
        except Exception as e:
            logger.error(f"Failed to reload settings: {str(e)}")

    async def _process_message(self, message: str) -> str | None:
        """Process a message through the agent.

        Args:
            message: The message to process

        Returns:
            The agent's response or None if processing failed
        """
        # Check if background processing is enabled
        use_background = get_env_var(
            "USE_BACKGROUND_PROCESSING", default="true", cast_type=lambda x: x.lower() == "true"
        )
        
        if use_background:
            # Use async streaming method for long-running tasks
            return await self.agent.process_message_async(message)
        else:
            # Use synchronous method (backward compatibility)
            return await self.agent.process_message(message)

    async def _on_message_processed(self, user_id: int, response: str) -> None:
        """Handle processed messages.

        Args:
            user_id: The user ID
            response: The processed response message
        """
        # Let the plugin manager handle message sending
        # This will be handled by individual plugins
        logger.info(f"Message processed for user {user_id}: {response}")

    async def start(self) -> None:
        """Start all application components."""
        try:
            # Validate environment variables (only in production mode)
            settings = get_settings()
            debug_mode = settings.get("debug_mode", False)
            if not debug_mode:
                try:
                    validate_environment_variables(production_mode=True)
                    logger.info("✅ Environment variables validated")
                except ValueError as e:
                    logger.error(f"❌ Environment variable validation failed: {e}")
                    logger.error(
                        "Please check your .env file and ensure all values are set correctly"
                    )
                    raise

            # Initialize and migrate the database safely (before pool, uses direct connection)
            await initialize_database()
            await check_and_migrate_db()

            # Initialize database connection pool after database is ready
            await self.db_pool.initialize()

            # Initialize the agent
            logger.info("🔄 Initializing agent API connection...")
            if not await self.agent.initialize():
                logger.error("❌ Failed to initialize agent. Exiting...")
                return

            # Load configuration
            logger.info("📋 Loading configuration...")
            settings = get_settings()

            # Discover and load plugins
            logger.info("🔄 Discovering plugins...")
            await self.plugin_manager.discover_plugins(
                config=settings.get("plugins", {})
            )

            # Start plugin manager
            logger.info("🔄 Starting plugin manager...")
            await self.plugin_manager.start()

            # Initialize queue processor
            logger.info("📋 Initializing message queue processor...")
            self.queue_processor = QueueProcessor(
                message_processor=self._process_message,
                plugin_manager=self.plugin_manager,
            )

            # Set initial message mode from unified config
            initial_mode = self.config_manager.get("message_mode", "echo")
            self.queue_processor.set_message_mode(initial_mode)

            # Start queue processor
            asyncio.create_task(self.queue_processor.start())

            logger.info("✅ Application started successfully!")

            # Start unified configuration manager monitoring
            asyncio.create_task(self.config_manager.start_monitoring())

            # Start legacy settings monitor task (for plugin updates)
            asyncio.create_task(self._monitor_settings())

            # Set up signal handlers after event loop is running
            self._setup_signal_handlers()

            # Keep application running until shutdown signal
            await self._shutdown_event.wait()

        except Exception as e:
            logger.error(f"❌ Error during startup: {str(e)}")
            raise
        finally:
            # Always ensure cleanup happens
            await self.stop()

    async def _monitor_settings(self):
        """Monitor settings file for changes."""
        while not self._shutdown_event.is_set():
            try:
                await self._check_settings()
                await asyncio.sleep(1)  # Check every second
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error monitoring settings: {e}")
                await asyncio.sleep(5)  # Wait longer on error

    async def stop(self) -> None:
        """Stop all application components."""
        try:
            logger.info("🛑 Initiating graceful shutdown...")

            # Cancel all running tasks
            if self._tasks:
                logger.info("🛑 Cancelling running tasks...")
                for task in self._tasks:
                    task.cancel()

                # Wait for tasks to complete cancellation
                if self._tasks:
                    await asyncio.gather(*self._tasks, return_exceptions=True)

            # Stop components in reverse order
            if self.queue_processor:
                logger.info("🛑 Stopping queue processor...")
                await self.queue_processor.stop()

            # Clean up agent
            logger.info("🛑 Cleaning up agent...")
            await self.agent.cleanup()

            # Stop plugin manager last
            logger.info("🛑 Stopping plugin manager...")
            await self.plugin_manager.stop()

            # Close database connection pool
            if hasattr(self, "db_pool"):
                logger.info("🛑 Closing database connection pool...")
                await self.db_pool.close()

            logger.info("✅ Application stopped successfully")

        except Exception as e:
            logger.error(f"❌ Error during shutdown: {str(e)}")
        finally:
            # Always remove PID file, even if other cleanup fails
            if hasattr(self, "pid_manager"):
                self.pid_manager.cleanup()
                logger.info("🗑️ PID file removed")

    def update_settings(self, settings: dict) -> None:
        """Update application settings.

        Args:
            settings: Dictionary containing the new settings
        """
        if "message_mode" in settings:
            new_mode = settings["message_mode"]
            logger.info(f"Updating message mode to: {new_mode}")
            if self.queue_processor:
                self.queue_processor.set_message_mode(new_mode)
        if "debug_mode" in settings:
            self.agent.debug_mode = settings["debug_mode"]


def main() -> None:
    """Application entry point."""
    app = None
    try:
        logger.info("🚀 Starting application...")
        app = Application()
        asyncio.run(app.start())
    except KeyboardInterrupt:
        logger.warning("⚠️ Shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        sys.exit(1)
    finally:
        # Ensure cleanup happens even if main() exits unexpectedly
        if app:
            try:
                asyncio.run(app.stop())
            except Exception as e:
                logger.error(f"❌ Error during final cleanup: {str(e)}")
        sys.exit(0)


if __name__ == "__main__":
    main()
