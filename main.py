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

from common.config import get_settings, validate_settings, validate_environment_variables
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
            logger.warning("Settings file contains invalid JSON, recreating with defaults...")
        except Exception as e:
            should_create = True
            logger.warning(f"Failed to read settings file ({e}), recreating with defaults...")

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
            with open(pid_file, "r") as f:
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

        # Create default settings if needed
        create_default_settings()

        # Initialize PID manager
        self.pid_manager = PIDManager()
        try:
            self.pid_manager.create_pid_file()
        except RuntimeError as e:
            logger.error(f"❌ {e}")
            raise

        # Set up signal handlers for graceful shutdown
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""

        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            # Clean up PID file on signal
            if hasattr(self, "pid_manager"):
                self.pid_manager.cleanup()
            self._shutdown_event.set()

        # Handle SIGTERM and SIGINT (only on non-Windows platforms)
        if sys.platform != "win32":
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)

    async def _check_settings(self):
        """Check if settings file has been modified."""
        try:
            current_mtime = os.path.getmtime(self._settings_file)
            if current_mtime > self._settings_mtime:
                logger.info("Settings file modified, reloading...")
                settings = get_settings()
                validate_settings(settings)

                # Update message mode in queue processor and plugins
                if "message_mode" in settings:
                    new_mode = settings["message_mode"]
                    logger.info(f"Updating message mode to: {new_mode}")

                    # Update queue processor if it exists
                    if self.queue_processor:
                        self.queue_processor.set_message_mode(new_mode)
                        logger.info(
                            f"🔵 Message processing mode changed to: {new_mode.upper()}"
                        )

                    # Update all plugins that support message mode changes
                    if self.plugin_manager:
                        await self.plugin_manager.update_message_mode(new_mode)
                        logger.info(
                            f"🔵 Plugin message modes updated to: {new_mode.upper()}"
                        )

                # Update debug mode
                if "debug_mode" in settings:
                    self.agent.debug_mode = settings["debug_mode"]
                    logger.info(
                        f"Debug mode {'enabled' if settings['debug_mode'] else 'disabled'}"
                    )

                # Update queue refresh interval
                if "queue_refresh" in settings and self.queue_processor:
                    self.queue_processor.refresh_interval = settings["queue_refresh"]
                    logger.info(
                        f"Queue refresh interval set to {settings['queue_refresh']} seconds"
                    )

                # Update max retries
                if "max_retries" in settings and self.queue_processor:
                    self.queue_processor.max_retries = settings["max_retries"]
                    logger.info(f"Max retries set to {settings['max_retries']}")

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
                    logger.error("Please check your .env file and ensure all values are set correctly")
                    raise
            
            # Initialize and migrate the database safely
            await initialize_database()
            await check_and_migrate_db()

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

            # Set initial message mode from settings
            settings = get_settings()
            initial_mode = settings.get("message_mode", "echo")
            self.queue_processor.set_message_mode(initial_mode)

            # Start queue processor
            asyncio.create_task(self.queue_processor.start())

            logger.info("✅ Application started successfully!")

            # Start settings monitor task
            asyncio.create_task(self._monitor_settings())

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
