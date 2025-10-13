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

"""Configuration management module."""

import json
import os
from collections.abc import Callable
from typing import Any

_SETTINGS_CACHE = None


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
            raise ValueError(f"Failed to cast {name} to {cast_type.__name__}: {str(e)}")

    return value


def get_settings(settings_file: str = "settings.json") -> dict:
    """Get application settings from a JSON file.

    Args:
        settings_file: Path to the settings file.

    Returns:
        Dictionary containing the settings.

    Raises:
        FileNotFoundError: If the settings file does not exist.
        ValueError: If the settings file is invalid JSON or cannot be read.
    """
    global _SETTINGS_CACHE

    if _SETTINGS_CACHE is not None:
        return _SETTINGS_CACHE

    if not os.path.exists(settings_file):
        raise FileNotFoundError("Settings file not found")

    try:
        with open(settings_file) as f:
            content = f.read()
    except PermissionError:
        raise ValueError("Permission denied")
    except FileNotFoundError:
        raise FileNotFoundError("Settings file not found")
    except OSError as e:
        raise ValueError(f"Failed to read settings file: {str(e)}")

    try:
        _SETTINGS_CACHE = json.loads(content)
        return _SETTINGS_CACHE
    except json.JSONDecodeError:
        raise ValueError("Failed to parse settings file")
    except Exception as e:
        raise ValueError(f"Failed to parse settings file: {str(e)}")


# Reset the settings cache (for testing)
def _reset_settings_cache():
    """Reset the settings cache. Used for testing."""
    global _SETTINGS_CACHE
    _SETTINGS_CACHE = None


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
        raise ValueError(f"Failed to save settings: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to save settings: {str(e)}")


def validate_settings(settings: dict) -> None:
    """Validate application settings.

    Args:
        settings: Dictionary containing the settings to validate

    Raises:
        ValueError: If the settings are invalid
    """
    required_fields = {
        "debug_mode": bool,
        "queue_refresh": int,
        "max_retries": int,
        "message_mode": str,
    }

    # Check for required fields
    for field, field_type in required_fields.items():
        if field not in settings:
            raise ValueError(f"Missing required setting: {field}")

        # Try to convert to correct type
        try:
            if field_type == bool:
                # Handle string 'on'/'off' or 'true'/'false'
                if isinstance(settings[field], str):
                    settings[field] = settings[field].lower() in ("on", "true", "1")
                else:
                    settings[field] = bool(settings[field])
            else:
                settings[field] = field_type(settings[field])
        except (ValueError, TypeError):
            raise ValueError(f"Invalid value for {field}: {settings[field]}")

    # Validate message_mode
    valid_modes = ["echo", "listen", "live"]
    if settings["message_mode"] not in valid_modes:
        raise ValueError(
            f"Invalid message_mode. Must be one of: {', '.join(valid_modes)}"
        )

    # Validate numeric ranges
    if settings["queue_refresh"] < 1:
        raise ValueError("queue_refresh must be at least 1")
    if settings["max_retries"] < 0:
        raise ValueError("max_retries must be non-negative")
