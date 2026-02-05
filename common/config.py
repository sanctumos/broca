"""
Configuration management module.

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
import json
import logging
import os
from collections.abc import Callable
from typing import Any, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_SETTINGS_CACHE = None
_TYPED_SETTINGS_CACHE = None

logger = logging.getLogger(__name__)


class QueueProcessorConfig(BaseSettings):
    """Configuration for queue processor."""

    max_concurrent: int = Field(
        default=3,
        ge=1,
        le=50,
        description="Maximum concurrent messages to process (1-50)",
    )


class DatabasePoolConfig(BaseSettings):
    """Configuration for database connection pool."""

    pool_size: int = Field(
        default=5, ge=1, le=100, description="Number of connections in pool (1-100)"
    )
    max_overflow: int = Field(
        default=10,
        ge=0,
        le=50,
        description="Maximum overflow connections beyond pool_size (0-50)",
    )


class Settings(BaseSettings):
    """Type-safe application settings model."""

    debug_mode: bool = Field(
        default=False,
        description="Enable debug mode for additional logging and diagnostics",
    )
    queue_refresh: int = Field(
        default=5, ge=1, le=300, description="Queue refresh interval in seconds (1-300)"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts for failed operations (0-10)",
    )
    message_mode: Literal["echo", "listen", "live"] = Field(
        default="live",
        description="Message processing mode: echo (test), listen (monitor), live (process)",
    )
    plugins: dict | None = Field(
        default_factory=dict, description="Plugin-specific configuration settings"
    )
    queue_processor: QueueProcessorConfig | dict | None = Field(
        default_factory=dict,
        description="Queue processor configuration",
    )
    database: DatabasePoolConfig | dict | None = Field(
        default_factory=dict,
        description="Database connection pool configuration",
    )

    @field_validator("queue_refresh")
    @classmethod
    def validate_queue_refresh(cls, v):
        """Validate queue refresh interval."""
        if v < 1:
            raise ValueError("queue_refresh must be at least 1 second")
        if v > 300:
            raise ValueError("queue_refresh should not exceed 300 seconds")
        return v

    @field_validator("max_retries")
    @classmethod
    def validate_max_retries(cls, v):
        """Validate max retries value."""
        if v < 0:
            raise ValueError("max_retries must be non-negative")
        if v > 10:
            raise ValueError("max_retries should not exceed 10")
        return v

    @field_validator("queue_processor", mode="before")
    @classmethod
    def validate_queue_processor(cls, v):
        """Convert dict to QueueProcessorConfig if needed."""
        if isinstance(v, dict):
            return QueueProcessorConfig(**v)
        return v

    @field_validator("database", mode="before")
    @classmethod
    def validate_database(cls, v):
        """Convert dict to DatabasePoolConfig if needed."""
        if isinstance(v, dict):
            return DatabasePoolConfig(**v)
        return v

    model_config = SettingsConfigDict(
        env_prefix="BROCA_",
        case_sensitive=False,
        validate_assignment=True,
        extra="allow",  # Allow extra fields for plugins
    )


def get_env_var(
    name: str,
    default: Any = None,
    required: bool = False,
    cast_type: Callable | None = None,
) -> Any:
    """Get an environment variable with optional type casting.

    Args:
        name: Name of the environment variable.
        default: Default value if variable is not set.
        required: If True, raise EnvironmentError when variable is not set.
        cast_type: Optional function to cast the value to a specific type.

    Returns:
        The environment variable value.

    Raises:
        EnvironmentError: If required is True and variable is not set.
        ValueError: If cast_type is provided and casting fails.
    """
    value = os.environ.get(name)

    if value is None:
        if required:
            raise OSError(f"Required environment variable {name} is not set")
        return default

    if cast_type is not None:
        try:
            return cast_type(value)
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Failed to cast {name} to {cast_type.__name__}: {str(e)}"
            ) from e

    return value


def validate_environment_variables(production_mode: bool = True) -> None:
    """Validate environment variables to detect placeholder/test values.

    This function checks for placeholder values in critical environment variables
    that should not be used in production. It helps prevent accidental use of
    test credentials in production environments.

    Args:
        production_mode: If True, raise errors for placeholder values.
                        If False, only log warnings (for development).

    Raises:
        ValueError: If placeholder values are detected in production mode.
    """
    import logging

    logger = logging.getLogger(__name__)

    # Define critical environment variables and their placeholder patterns
    critical_vars = {
        "AGENT_API_KEY": [
            "your_letta_api_key_here",
            "your-api-key-here",
            "placeholder",
            "test",
            "123456",
            "changeme",
        ],
        "AGENT_ENDPOINT": [
            "your-endpoint-here",
            "placeholder",
            "example.com",
            "localhost",
        ],
        "TELEGRAM_API_HASH": [
            "your_telegram_api_hash_here",
            "placeholder",
            "123456",
            "test",
        ],
        "TELEGRAM_BOT_TOKEN": [
            "your_bot_token_here",
            "placeholder",
            "123456",
            "test",
        ],
    }

    # Patterns that indicate placeholder values
    placeholder_patterns = [
        "your_",
        "your-",
        "_here",
        "-here",
        "placeholder",
        "changeme",
        "example",
        "test_",
        "test-",
    ]

    errors = []
    warnings = []

    for var_name, known_placeholders in critical_vars.items():
        value = os.environ.get(var_name)

        if not value:
            # Missing required variable - only warn, don't error
            # (some may be optional depending on which plugins are enabled)
            warnings.append(f"Environment variable {var_name} is not set")
            continue

        value_lower = value.lower().strip()

        # Check against known placeholder values
        if value_lower in [p.lower() for p in known_placeholders]:
            msg = (
                f"Environment variable {var_name} appears to be a placeholder: "
                f"{value[:20]}..."
            )
            if production_mode:
                errors.append(msg)
            else:
                warnings.append(msg)
            continue

        # Check for placeholder patterns
        for pattern in placeholder_patterns:
            if pattern in value_lower:
                msg = (
                    f"Environment variable {var_name} may contain a placeholder "
                    f"pattern: {pattern}"
                )
                if production_mode:
                    errors.append(msg)
                else:
                    warnings.append(msg)
                break

    # Log warnings
    for warning in warnings:
        logger.warning(f"⚠️ {warning}")

    # Raise errors in production mode
    if errors:
        error_msg = (
            "Invalid environment variables detected. Please ensure all "
            "environment variables are set to production values, not placeholders.\n"
            + "\n".join(f"  - {e}" for e in errors)
        )
        if production_mode:
            raise ValueError(error_msg)
        else:
            logger.warning(f"⚠️ {error_msg}")


def get_typed_settings(
    settings_file: str = "settings.json", force_reload: bool = False
) -> Settings:
    """Get type-safe application settings from a JSON file.

    Args:
        settings_file: Path to the settings file.
        force_reload: If True, reload settings even if cached.

    Returns:
        Settings object with validated configuration.

    Raises:
        FileNotFoundError: If the settings file does not exist.
        ValueError: If the settings file is invalid JSON or validation fails.
    """
    global _TYPED_SETTINGS_CACHE

    if _TYPED_SETTINGS_CACHE is not None and not force_reload:
        return _TYPED_SETTINGS_CACHE

    # Load raw settings
    raw_settings = get_settings(settings_file, force_reload=force_reload)

    try:
        # Create Settings object with validation
        _TYPED_SETTINGS_CACHE = Settings(**raw_settings)
        return _TYPED_SETTINGS_CACHE
    except Exception as e:
        raise ValueError(f"Settings validation failed: {str(e)}") from e


def get_settings(
    settings_file: str = "settings.json", force_reload: bool = False
) -> dict:
    """Get application settings from a JSON file.

    Args:
        settings_file: Path to the settings file.
        force_reload: If True, reload settings even if cached.

    Returns:
        Dictionary containing the settings.

    Raises:
        FileNotFoundError: If the settings file does not exist.
        ValueError: If the settings file is invalid JSON or cannot be read.
    """
    global _SETTINGS_CACHE

    if _SETTINGS_CACHE is not None and not force_reload:
        return _SETTINGS_CACHE

    if not os.path.exists(settings_file):
        raise FileNotFoundError("Settings file not found")

    try:
        with open(settings_file) as f:
            content = f.read()
    except PermissionError as e:
        raise ValueError("Permission denied") from e
    except FileNotFoundError as e:
        raise FileNotFoundError("Settings file not found") from e
    except OSError as e:
        raise ValueError(f"Failed to read settings file: {str(e)}") from e

    try:
        _SETTINGS_CACHE = json.loads(content)
        return _SETTINGS_CACHE
    except json.JSONDecodeError as e:
        raise ValueError("Failed to parse settings file") from e
    except Exception as e:
        raise ValueError(f"Failed to parse settings file: {str(e)}") from e


# Reset the settings cache (for testing)
def _reset_settings_cache():
    """Reset the settings cache. Used for testing."""
    global _SETTINGS_CACHE, _TYPED_SETTINGS_CACHE
    _SETTINGS_CACHE = None
    _TYPED_SETTINGS_CACHE = None


def validate_settings(settings: dict) -> dict:
    """Validate application settings and return a validated copy.

    Args:
        settings: Dictionary containing the settings to validate

    Returns:
        Validated settings dictionary (immutable copy)

    Raises:
        ValueError: If the settings are invalid
    """
    # Create a copy to avoid mutating the original
    validated_settings = settings.copy()

    required_fields = {
        "debug_mode": bool,
        "queue_refresh": int,
        "max_retries": int,
        "message_mode": str,
    }

    # Check for required fields
    for field, field_type in required_fields.items():
        if field not in validated_settings:
            raise ValueError(f"Missing required setting: {field}")

        # Try to convert to correct type
        try:
            if field_type is bool:
                # Handle string 'on'/'off' or 'true'/'false'
                if isinstance(validated_settings[field], str):
                    validated_settings[field] = validated_settings[field].lower() in (
                        "on",
                        "true",
                        "1",
                    )
                else:
                    validated_settings[field] = bool(validated_settings[field])
            else:
                validated_settings[field] = field_type(validated_settings[field])
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Invalid value for {field}: {validated_settings[field]}"
            ) from e

    # Validate message_mode
    valid_modes = ["echo", "listen", "live"]
    if validated_settings["message_mode"] not in valid_modes:
        raise ValueError(
            f"Invalid message_mode. Must be one of: {', '.join(valid_modes)}"
        )

    # Validate numeric ranges
    if validated_settings["queue_refresh"] < 1:
        raise ValueError("queue_refresh must be at least 1")
    if validated_settings["max_retries"] < 0:
        raise ValueError("max_retries must be non-negative")

    return validated_settings


def save_settings(settings: dict, settings_file: str = "settings.json") -> None:
    """Save application settings to a JSON file.

    Args:
        settings: Dictionary containing the settings to save
        settings_file: Path to the settings file

    Raises:
        ValueError: If the settings cannot be saved
    """
    global _SETTINGS_CACHE

    try:
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)
        _SETTINGS_CACHE = settings
    except (OSError, PermissionError) as e:
        raise ValueError(f"Failed to save settings: {str(e)}") from e
    except Exception as e:
        raise ValueError(f"Failed to save settings: {str(e)}") from e


class ConfigurationManager:
    """Unified configuration management system with hot-reloading and change notifications."""

    def __init__(self, settings_file: str = "settings.json"):
        """Initialize the configuration manager.

        Args:
            settings_file: Path to the settings JSON file
        """
        self.settings_file = settings_file
        self._settings: Settings | None = None
        self._callbacks: dict[str, list[Callable[[Any, Any], None]]] = {}
        self._last_mtime = 0
        self._monitoring = False
        self._stop_event: asyncio.Event | None = (
            None  # Set in start_monitoring() when loop is running
        )

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation.

        Args:
            key: Configuration key (supports dot notation, e.g., 'queue_processor.max_concurrent')
            default: Default value if key is not found

        Returns:
            Configuration value or default

        Examples:
            >>> config.get('message_mode')
            'live'
            >>> config.get('queue_processor.max_concurrent')
            3
            >>> config.get('plugins.telegram_bot.enabled', False)
            False
        """
        if self._settings is None:
            self._load_settings()

        # Support dot notation for nested keys
        keys = key.split(".")
        value = self._settings.model_dump()

        try:
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    value = getattr(value, k, None)
                if value is None:
                    return default
            return value
        except (AttributeError, KeyError, TypeError):
            return default

    def get_typed(self, force_reload: bool = False) -> Settings:
        """Get fully validated Pydantic Settings object.

        Args:
            force_reload: If True, reload settings even if cached

        Returns:
            Validated Settings object
        """
        if self._settings is None or force_reload:
            self._load_settings(force_reload=force_reload)
        return self._settings

    def subscribe(self, key: str, callback: Callable[[Any, Any], None]) -> None:
        """Subscribe to configuration changes for a specific key.

        Args:
            key: Configuration key to monitor (supports dot notation)
            callback: Function to call when the key changes (old_value, new_value)

        Examples:
            >>> def on_mode_change(old, new):
            ...     print(f"Mode changed from {old} to {new}")
            >>> config.subscribe('message_mode', on_mode_change)
        """
        if key not in self._callbacks:
            self._callbacks[key] = []
        self._callbacks[key].append(callback)
        logger.debug(f"Subscribed to config changes for key: {key}")

    def unsubscribe(self, key: str, callback: Callable[[Any, Any], None]) -> None:
        """Unsubscribe from configuration changes.

        Args:
            key: Configuration key
            callback: Callback function to remove
        """
        if key in self._callbacks:
            try:
                self._callbacks[key].remove(callback)
                if not self._callbacks[key]:
                    del self._callbacks[key]
            except ValueError:
                pass

    def _load_settings(self, force_reload: bool = False) -> None:
        """Load and validate settings from file."""
        raw_settings = get_settings(self.settings_file, force_reload=force_reload)
        old_settings = self._settings

        try:
            self._settings = Settings(**raw_settings)
            logger.debug("Settings loaded and validated successfully")

            # Notify subscribers of changes
            if old_settings is not None:
                self._notify_changes(old_settings, self._settings)
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            if old_settings is None:
                raise
            # Keep old settings if reload fails
            logger.warning("Keeping previous settings due to validation error")

    def _notify_changes(self, old_settings: Settings, new_settings: Settings) -> None:
        """Notify subscribers of configuration changes."""
        old_dict = old_settings.model_dump()
        new_dict = new_settings.model_dump()

        # Check all subscribed keys
        for key in list(self._callbacks.keys()):
            old_value = self._get_nested_value(old_dict, key)
            new_value = self._get_nested_value(new_dict, key)

            if old_value != new_value:
                for callback in self._callbacks[key]:
                    try:
                        callback(old_value, new_value)
                    except Exception as e:
                        logger.error(f"Error in config change callback for {key}: {e}")

    def _get_nested_value(self, data: dict, key: str) -> Any:
        """Get nested value from dict using dot notation."""
        keys = key.split(".")
        value = data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None
            if value is None:
                return None
        return value

    async def start_monitoring(self, check_interval: float = 1.0) -> None:
        """Start monitoring settings file for changes.

        Args:
            check_interval: How often to check for changes (seconds)
        """
        if self._monitoring:
            logger.warning("Configuration monitoring already started")
            return

        self._monitoring = True
        self._stop_event = asyncio.Event()
        self._stop_event.clear()

        # Get initial mtime
        if os.path.exists(self.settings_file):
            self._last_mtime = os.path.getmtime(self.settings_file)

        logger.info(f"Started monitoring configuration file: {self.settings_file}")

        try:
            while not self._stop_event.is_set():
                await asyncio.sleep(check_interval)

                if not os.path.exists(self.settings_file):
                    continue

                current_mtime = os.path.getmtime(self.settings_file)
                if current_mtime > self._last_mtime:
                    logger.info("Configuration file modified, reloading...")
                    self._load_settings(force_reload=True)
                    self._last_mtime = current_mtime

        except asyncio.CancelledError:
            logger.info("Configuration monitoring cancelled")
        finally:
            self._monitoring = False
            logger.info("Configuration monitoring stopped")

    def stop_monitoring(self) -> None:
        """Stop monitoring settings file for changes."""
        if self._stop_event is not None:
            self._stop_event.set()
        self._monitoring = False

    def reload(self) -> None:
        """Manually reload configuration from file."""
        logger.info("Manually reloading configuration...")
        self._load_settings(force_reload=True)
        if os.path.exists(self.settings_file):
            self._last_mtime = os.path.getmtime(self.settings_file)


# Global configuration manager instance
_config_manager: ConfigurationManager | None = None


def get_config_manager(
    settings_file: str = "settings.json",
) -> ConfigurationManager:
    """Get or create the global configuration manager instance.

    Args:
        settings_file: Path to settings file

    Returns:
        ConfigurationManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager(settings_file)
    return _config_manager
