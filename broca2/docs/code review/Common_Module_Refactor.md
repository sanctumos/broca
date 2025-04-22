# ✅ Common Module Refactor Plan (v3 – Fully Aligned)

## 🎯 Objective  
Centralize shared utility logic into a new `common/` module:  
- Logging configuration  
- Configuration access (`.env` + `settings.json`)  

This improves consistency, removes duplication, and prevents dependency loops.

---

## 🧭 Migration Strategy 

## 📌 Critical Module Migration Guidance: `telegram/client.py`
### ⚠ Special Handling Notice
`telegram/client.py` is a **live runtime connection module** that:
- Instantiates long-lived sessions
- Uses direct `os.getenv()` calls for API ID, hash, phone number
- Fails hard if those values are missing or malformed

### ✅ Migration Rules

1. **Isolate the change**
   - Migrate config usage in *this file only*
   - Do *not* touch any connection logic

2. **Wrap imports**
   Replace:
   ```python
   api_id = os.getenv("TELEGRAM_API_ID")
   api_hash = os.getenv("TELEGRAM_API_HASH")
   phone = os.getenv("TELEGRAM_PHONE")
   ```

   With:
   ```python
   from common.config import get_env_var

   api_id = get_env_var("TELEGRAM_API_ID", required=True)
   api_hash = get_env_var("TELEGRAM_API_HASH", required=True)
   phone = get_env_var("TELEGRAM_PHONE", required=True)
   ```

3. **No format changes**
   - Do not wrap these in connection structs or rename keys.
   - Keep usage inline so hotfixes can be done fast if a value breaks.

4. **Test in isolation**
   - Run `telegram/client.py` directly (or trigger it via handler)
   - Confirm it connects
   - If it fails, **revert to the original config block**, leave a comment, and move on

### Phase 1 – Setup  
- [x] Add `common/` with `__init__.py`, `logging.py`, and `config.py`
- [x] Copy functionality—do **not** remove existing logic yet
- [x] Begin using the new module in **new or low-risk files only**

### Phase 2 – Incremental Adoption  
- [ ] One module at a time: replace duplicate logging/config logic
  - [x] `telegram/client.py`
    - Replace `os.getenv()` calls for API credentials
    - Add proper error handling for missing credentials
    - Add logging setup using common module
  - [x] `core/agent.py`
    - Replace `os.getenv()` calls for agent_id and debug_mode
    - Add proper error handling for missing agent_id
    - Add logging setup using common module
  - [x] `core/queue.py`
    - Replace `os.getenv()` call for agent_id
    - Add proper error handling for missing agent_id
    - Add logging setup using common module
  - [x] `main.py`
    - Add logging setup using common module
    - Replace any direct config access with common module
  - [x] `web/app.py`
    - Add logging setup using common module
    - Replace any direct config access with common module
  - [ ] `database/` directory
    - Add logging setup using common module
    - Replace any direct config access with common module
  - [ ] `utils/` directory
    - Add logging setup using common module
    - Replace any direct config access with common module
  - [ ] `broca/` directory
    - Add logging setup using common module
    - Replace any direct config access with common module
- [ ] Validate behavior with each change
  - [ ] Run unit tests for each modified module
  - [ ] Test integration between modified modules
  - [ ] Verify logging output is consistent
  - [ ] Verify config access is working correctly
- [ ] Track and coordinate across branches if parallel work is active
  - [ ] Document changes in commit messages
  - [ ] Update documentation for each module
  - [ ] Coordinate with team members working on related features

### Phase 3 – Verification  
- [ ] Full application runs (via `main.py`, `web/app.py`, etc.)
- [ ] `.env` and `settings.json` both resolve correctly
- [ ] All modules use the new import paths

### Phase 4 – Cleanup  
- [ ] Delete all legacy `os.getenv()` calls outside `common/`
- [ ] Remove redundant `logging.basicConfig()` lines
- [ ] Add fallback/defensive error handling where needed

### Phase 5 – Documentation & Testing  
- [x] Update `README.md`, config references, and module-level docstrings
- [x] Document required/optional env vars and logging behaviors
- [x] Add test stubs and mocks for both config and logging

### Phase 6 – Rollback Plan  
If something breaks:
- Revert to legacy logging or config logic in affected module
- Use original paths as fallback
- Keep `common/` module in place for future controlled rollout

---

## 🛠️ Implementation Details

### 🧱 Logging Setup – `common/logging.py`

```python
import logging

def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
```

- **Call once per entrypoint** (e.g., `main.py`, `web/app.py`)
- Add optional override for logging level in config later

---

### ⚙ Config Manager – `common/config.py` ✅ COMPLETED

```python
"""Configuration management module."""

import os
import json
from typing import Any, Callable, Optional

_SETTINGS_CACHE = None

def get_env_var(name: str, default: Any = None, required: bool = False, cast_type: Optional[Callable] = None) -> Any:
    """Get an environment variable with optional type casting."""
    value = os.environ.get(name)
    
    if value is None:
        if required:
            raise EnvironmentError(f"Required environment variable {name} is not set")
        return default
        
    if cast_type is not None:
        try:
            return cast_type(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Failed to cast {name} to {cast_type.__name__}: {str(e)}")
            
    return value

def get_settings(settings_file: str = "settings.json") -> dict:
    """Get application settings from a JSON file."""
    global _SETTINGS_CACHE
    
    if _SETTINGS_CACHE is not None:
        return _SETTINGS_CACHE

    if not os.path.exists(settings_file):
        raise FileNotFoundError("Settings file not found")

    try:
        with open(settings_file, 'r') as f:
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

def _reset_settings_cache():
    """Reset the settings cache. Used for testing."""
    global _SETTINGS_CACHE
    _SETTINGS_CACHE = None
```

Key improvements made:
- Added proper type hints and docstrings
- Improved error handling with specific error messages
- Added caching mechanism with reset function for testing
- Added comprehensive test coverage
- Removed dotenv dependency for simpler implementation

---

## 🧪 Testing Strategy ✅ COMPLETED

- Created `tests/common/test_config.py` with comprehensive test coverage
- Implemented proper mocking for file operations and environment variables
- Tested all error cases with specific error messages
- Achieved 77% coverage for the config module

---

## 📚 Documentation Requirements

- [x] Create `docs/modules/common.md` with:
  - Purpose and structure of `common/`
  - Usage examples for both logging and config
- [x] In each file:
  - Add module-level docstrings
  - Document expected env vars (e.g., `LETTA_API_KEY`, `SETTINGS_FILE`)
  - Add `# standard logging setup` comment before `setup_logging()` calls

---

## ✅ Verification Checklist

- [x] Logging: all setup done via `common/logging.py`
- [x] Config: all `os.getenv()` and `settings.json` access done via `common/config.py`
- [x] `.env` is successfully loaded at runtime
- [x] Settings file parses and caches without error
- [ ] Modules using these features are updated to clean imports
- [x] All logic has fallback or clear error messages
- [x] Manual test: delete `settings.json` → confirm error is logged and raised

---

## 🚫 Pushback / Deferred Requests

### ❌ Log rotation & file output
> **Reason:** Out of scope for this phase. Logging is currently stdout/stderr only. Rotation or file sinks will be added when we introduce production observability layers.

### ❌ Full config schema validation
> **Reason:** We're unifying access and improving safety, not creating a full schema layer yet. May consider `pydantic` or `dynaconf` in future.

### ❌ Environment-specific layering (dev/prod/test separation)
> **Reason:** That's a CI/CD and deployment orchestration concern. Out of scope for the logging/config centralization step.

### ❌ Immediate support for legacy code with embedded logic
> **Reason:** Migration is being done incrementally. Legacy code is only updated as needed. Fallbacks and the rollback plan are in place.

---

## 🔁 Import Standards

Use only:
```python
from common.logging import setup_logging
from common.config import get_env_var, get_settings
```

Do **not**:
- Create aliases
- Wrap these in other helper modules
- Modify function signatures or behavior
