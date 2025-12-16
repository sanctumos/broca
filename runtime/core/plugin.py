"""
Plugin management system for broca2.

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

import importlib.util
import inspect
import logging
import os
import sys
from collections.abc import Callable
from pathlib import Path

from common.exceptions import PluginError
from plugins import Event, EventType, Plugin

logger = logging.getLogger(__name__)


class PluginManager:
    """Manages plugin lifecycles and event routing."""

    def __init__(self):
        """Initialize the plugin manager."""
        self._plugins: dict[str, Plugin] = {}
        self._event_handlers: dict[EventType, list[Callable[[Event], None]]] = {}
        self._platform_handlers: dict[str, Callable] = {}
        self._running = False

    def _get_module_name_from_path(self, plugin_path: str) -> str:
        """Get a unique module name from plugin path to prevent collisions.
        
        Uses full package path instead of just filename to ensure uniqueness.
        
        Args:
            plugin_path: Full path to plugin file
            
        Returns:
            Unique module name based on package path
        """
        path = Path(plugin_path)
        # Get relative path from current working directory
        try:
            rel_path = path.relative_to(Path.cwd())
        except ValueError:
            # If not relative to cwd, use absolute path
            rel_path = path
        
        # Convert to module name: replace separators with dots, remove .py
        module_name = str(rel_path).replace(os.sep, ".").replace(os.altsep or os.sep, ".")
        if module_name.endswith(".py"):
            module_name = module_name[:-3]
        
        # Ensure it starts with a valid module name
        if not module_name or module_name.startswith("."):
            # Fallback to filename if path resolution fails
            module_name = path.stem
        
        return module_name

    def _validate_handler_signature(self, handler: Callable) -> bool:
        """Validate that handler has correct signature for message handling.
        
        Expected signature: async def handler(response: str, profile: Any, message_id: int) -> None
        
        Args:
            handler: The handler callable to validate
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not callable(handler):
            return False
        
        # Check if async function
        if not inspect.iscoroutinefunction(handler):
            return False
        
        # Get signature
        try:
            sig = inspect.signature(handler)
            params = list(sig.parameters.values())
        except (ValueError, TypeError):
            return False
        
        # Should have exactly 3 parameters: response, profile, message_id
        if len(params) != 3:
            return False
        
        # Parameter names should match expected (flexible on order)
        param_names = [p.name for p in params]
        if "response" not in param_names or "profile" not in param_names or "message_id" not in param_names:
            return False
        
        return True

    async def load_plugin(self, plugin_path: str) -> None:
        """Load a plugin from the given path.

        Args:
            plugin_path: Path to the plugin module

        Raises:
            PluginError: If plugin loading fails
        """
        try:
            # Convert path to module name using package path to prevent collisions
            module_name = self._get_module_name_from_path(plugin_path)
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if spec is None:
                raise PluginError(f"Could not load plugin from {plugin_path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find and instantiate the plugin class
            for _name, obj in module.__dict__.items():
                if isinstance(obj, type) and issubclass(obj, Plugin) and obj != Plugin:
                    plugin = obj()
                    plugin_name = plugin.get_name()

                    if plugin_name in self._plugins:
                        raise PluginError(f"Plugin {plugin_name} already loaded")

                    # Register platform handler if plugin provides one
                    platform = plugin.get_platform()
                    if platform:
                        handler = plugin.get_message_handler()
                        if handler:
                            # Validate handler signature before registering
                            if not self._validate_handler_signature(handler):
                                raise PluginError(
                                    f"Plugin {plugin_name} handler has invalid signature. "
                                    f"Expected: async def handler(response: str, profile: Any, message_id: int) -> None"
                                )
                            self._platform_handlers[platform] = handler
                            logger.info(
                                f"Registered message handler for platform: {platform}"
                            )

                    self._plugins[plugin_name] = plugin
                    logger.info(f"Loaded plugin: {plugin_name}")
                    return

            raise PluginError(f"No plugin class found in {plugin_path}")

        except Exception as e:
            raise PluginError(
                f"Failed to load plugin from {plugin_path}: {str(e)}"
            ) from e

    async def unload_plugin(self, plugin_name: str) -> None:
        """Unload a plugin.

        Args:
            plugin_name: Name of the plugin to unload

        Raises:
            PluginError: If plugin unloading fails
        """
        if plugin_name not in self._plugins:
            raise PluginError(f"Plugin {plugin_name} not loaded")

        plugin = self._plugins[plugin_name]

        # Unregister platform handler if this plugin provided one
        platform = plugin.get_platform()
        if platform and platform in self._platform_handlers:
            del self._platform_handlers[platform]
            logger.info(f"Unregistered message handler for platform: {platform}")

        try:
            await plugin.stop()
            del self._plugins[plugin_name]
            logger.info(f"Unloaded plugin: {plugin_name}")
        except Exception as e:
            raise PluginError(f"Failed to unload plugin {plugin_name}: {str(e)}") from e

    async def start_plugin(self, plugin_name: str) -> None:
        """Start a plugin.

        Args:
            plugin_name: Name of the plugin to start

        Raises:
            PluginError: If plugin start fails
        """
        if plugin_name not in self._plugins:
            raise PluginError(f"Plugin {plugin_name} not loaded")

        plugin = self._plugins[plugin_name]
        try:
            await plugin.start()
            logger.info(f"Started plugin: {plugin_name}")
        except Exception as e:
            raise PluginError(f"Failed to start plugin {plugin_name}: {str(e)}") from e

    async def stop_plugin(self, plugin_name: str) -> None:
        """Stop a plugin.

        Args:
            plugin_name: Name of the plugin to stop

        Raises:
            PluginError: If plugin stop fails
        """
        if plugin_name not in self._plugins:
            raise PluginError(f"Plugin {plugin_name} not loaded")

        plugin = self._plugins[plugin_name]
        try:
            await plugin.stop()
            logger.info(f"Stopped plugin: {plugin_name}")
        except Exception as e:
            raise PluginError(f"Failed to stop plugin {plugin_name}: {str(e)}") from e

    def register_event_handler(
        self, event_type: EventType, handler: Callable[[Event], None]
    ) -> None:
        """Register an event handler.

        Args:
            event_type: Type of event to handle
            handler: Function to call when event occurs
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    def unregister_event_handler(
        self, event_type: EventType, handler: Callable[[Event], None]
    ) -> None:
        """Unregister an event handler.

        Args:
            event_type: Type of event to unregister
            handler: Handler to remove
        """
        if event_type in self._event_handlers:
            self._event_handlers[event_type].remove(handler)

    def emit_event(self, event: Event) -> None:
        """Emit an event to all registered handlers.

        Args:
            event: Event to emit
        """
        if event.type in self._event_handlers:
            for handler in self._event_handlers[event.type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler: {str(e)}")

    def get_platform_handler(self, platform: str) -> Callable | None:
        """Get the message handler for a platform.

        Args:
            platform: Platform name to get handler for

        Returns:
            Optional[Callable]: Message handler if registered, None otherwise
        """
        return self._platform_handlers.get(platform)

    async def discover_plugins(
        self, plugins_dir: str = "plugins", config: dict = None
    ) -> None:
        """Discover and load all plugins in the plugins directory with dynamic settings.

        Args:
            plugins_dir: Path to plugins directory (relative to current directory)
            config: Optional configuration dict for plugin settings
        """
        plugins_path = Path(plugins_dir)
        if not plugins_path.exists():
            logger.warning(f"Plugins directory {plugins_dir} does not exist")
            return

        for plugin_dir in plugins_path.iterdir():
            if not plugin_dir.is_dir() or plugin_dir.name.startswith("_"):
                continue

            plugin_file = plugin_dir / "plugin.py"
            if plugin_file.exists():
                plugin_name = plugin_dir.name
                logger.info(f"Attempting to load plugin: {plugin_name}")

                try:
                    # Load the plugin
                    await self.load_plugin(str(plugin_file))

                    # Get the loaded plugin instance
                    plugin = self._plugins.get(plugin_name)

                    if plugin is None:
                        logger.error(
                            f"Failed to load plugin {plugin_name} - plugin not found after loading"
                        )
                        continue

                    # Get plugin settings schema
                    (plugin.get_settings() if hasattr(plugin, "get_settings") else {})

                    # Load plugin-specific config if available
                    plugin_config = {}
                    if config and plugin_name in config:
                        plugin_config = config[plugin_name]

                    # Apply settings to plugin
                    if hasattr(plugin, "apply_settings"):
                        plugin.apply_settings(plugin_config)
                        logger.info(f"Applied settings to plugin: {plugin_name}")
                    elif hasattr(
                        plugin, "validate_settings"
                    ) and plugin.validate_settings(plugin_config):
                        # Fallback for backward compatibility
                        logger.warning(
                            f"Plugin {plugin_name} should implement apply_settings()"
                        )
                    else:
                        logger.info(f"Plugin {plugin_name} loaded without settings")

                    logger.info(f"✅ Successfully loaded plugin: {plugin_name}")

                except PluginError as e:
                    logger.warning(
                        f"⚠️ Skipping plugin {plugin_name} - configuration error: {e}"
                    )
                    continue
                except Exception as e:
                    logger.warning(
                        f"⚠️ Skipping plugin {plugin_name} - unexpected error: {e}"
                    )
                    continue

    async def start(self) -> None:
        """Start all loaded plugins."""
        if self._running:
            return

        self._running = True
        for plugin_name in list(self._plugins.keys()):
            try:
                await self.start_plugin(plugin_name)
            except PluginError as e:
                logger.error(f"Failed to start plugin {plugin_name}: {str(e)}")

    async def stop(self) -> None:
        """Stop all loaded plugins."""
        if not self._running:
            return

        self._running = False
        for plugin_name in list(self._plugins.keys()):
            try:
                await self.stop_plugin(plugin_name)
            except PluginError as e:
                logger.error(f"Failed to stop plugin {plugin_name}: {str(e)}")

    def get_plugin(self, plugin_name: str) -> Plugin | None:
        """Get a loaded plugin by name.

        Args:
            plugin_name: Name of the plugin to get

        Returns:
            Optional[Plugin]: The plugin if loaded, None otherwise
        """
        return self._plugins.get(plugin_name)

    def get_loaded_plugins(self) -> list[str]:
        """Get names of all loaded plugins.

        Returns:
            List[str]: List of loaded plugin names
        """
        return list(self._plugins.keys())

    def is_running(self) -> bool:
        """Check if the plugin manager is running.

        Returns:
            bool: True if running, False otherwise
        """
        return self._running

    async def update_message_mode(self, new_mode: str) -> None:
        """Update message mode for all plugins that support it.

        Args:
            new_mode: The new message mode ('echo', 'listen', or 'live')
        """
        for plugin_name, plugin in self._plugins.items():
            try:
                if hasattr(plugin, "set_message_mode"):
                    plugin.set_message_mode(new_mode)
                    logger.info(
                        f"Updated message mode to {new_mode} for plugin: {plugin_name}"
                    )
                elif hasattr(plugin, "update_message_mode"):
                    plugin.update_message_mode(new_mode)
                    logger.info(
                        f"Updated message mode to {new_mode} for plugin: {plugin_name}"
                    )
            except Exception as e:
                logger.warning(
                    f"Failed to update message mode for plugin {plugin_name}: {str(e)}"
                )
