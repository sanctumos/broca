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

import json
import os
from collections.abc import Callable
from typing import Any, Literal

from pydantic import Field, validator
from pydantic_settings import BaseSettings

_SETTINGS_CACHE = None
_TYPED_SETTINGS_CACHE = None


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

    @validator("queue_refresh")
    def validate_queue_refresh(cls, v):
        """Validate queue refresh interval."""
        if v < 1:
            raise ValueError("queue_refresh must be at least 1 second")
        if v > 300:
            raise ValueError("queue_refresh should not exceed 300 seconds")
        return v

    @validator("max_retries")
    def validate_max_retries(cls, v):
        """Validate max retries value."""
        if v < 0:
            raise ValueError("max_retries must be non-negative")
        if v > 10:
            raise ValueError("max_retries should not exceed 10")
        return v

    class Config:
        """Pydantic configuration."""

        env_prefix = "BROCA_"
        case_sensitive = False
        validate_assignment = True
        extra = "forbid"  # Prevent extra fields


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
            json.dump(settings, f)
        _SETTINGS_CACHE = settings
    except (OSError, PermissionError) as e:
        raise ValueError(f"Failed to save settings: {str(e)}") from e
    except Exception as e:
        raise ValueError(f"Failed to save settings: {str(e)}") from e
