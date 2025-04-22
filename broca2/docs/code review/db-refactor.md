# 📦 **Database Operations Refactor Gameplan**

## 🧭 Goal

Split the bloated `database/operations.py` into three focused modules:

- `users.py`
- `messages.py`
- `queue.py`

...and move any shared logic into `shared.py`.

This lays the foundation for cleaner architecture, fewer circular dependencies, and eventual plugin support.

---

## 📂 Target Structure

```bash
database/
├── operations/
│   ├── __init__.py
│   ├── users.py
│   ├── messages.py
│   ├── queue.py
│   └── shared.py
```
 
---

## 🚨 Rules for the Swarm

### 1. **DO NOT REWRITE LOGIC. JUST MOVE IT.**
   - If it works now, it should work after the move.
   - No refactoring. No renaming. No optimizations.

### 2. **USE THESE FOLDER ASSIGNMENTS**

| Function Pattern                     | New File       |
|-------------------------------------|----------------|
| `get_or_create_*`, user lookups     | `users.py`     |
| `insert_message`, message updates   | `messages.py`  |
| `enqueue_*`, queue status, retries  | `queue.py`     |
| Used by multiple of the above       | `shared.py`    |

### 3. **UPDATE `__init__.py` TO RE-EXPORT**

At the end of `database/operations/__init__.py`, add:
```python
from .users import *
from .messages import *
from .queue import *
from .shared import *
```

### 4. **NO LOGIC DEPENDS ON THE ORIGINAL `operations.py` AFTER THIS**
   - Delete `operations.py` when done.
   - Ensure all imports across the codebase work via `from database.operations import ...`

---

## ✅ Revised 📋 Implementation Checklist (Locktight Version)

### 1. Setup Phase
- [x] Create `database/operations/` directory (if not already present)
- [x] Inside `operations/`, create:
  - [x] `__init__.py`
  - [x] `users.py`
  - [x] `messages.py`
  - [x] `queue.py`
  - [x] `shared.py`

### 2. Function Review & Categorization
- [x] Open `operations.py` and:
  - [x] Identify all `get_or_create_*`, user metadata, and platform lookup → `users.py`
  - [x] Identify all message insert/update/get → `messages.py`
  - [x] Identify all queue insert, dequeue, retry, and status functions → `queue.py`
  - [x] Any helper used in more than one category → `shared.py`

### 3. Function Migration
- [x] Move functions from `operations.py` to new module files:
  - [x] Copy-paste without changes
  - [x] Preserve original comments and docstrings
  - [x] Keep imports local to each file (even if duplicated)
  - [x] Keep function order the same within each file

### 4. Init Import Handling
- [x] In `operations/__init__.py`, re-export everything:
  ```python
  from .users import *
  from .messages import *
  from .queue import *
  from .shared import *
  ```
- [x] Add a module-level docstring explaining structure
- [x] Do **not** import things not defined in those modules

### 5. Module Sanity Testing
- [x] Run Python interpreter:
  ```bash
  python -i
  >>> from database.operations import get_or_create_user
  >>> help(get_or_create_user)
  ```
- [x] Confirm no import or circular errors

### 6. Integration Validation
- [x] Run the full app (or script) and verify:
  - [x] `main.py` executes without import errors
  - [x] `core/queue.py` runs and calls DB functions
  - [x] `core/agent.py` can access message/store calls
  - [x] `telegram/handlers.py` can access user functions

### 7. Cleanup
- [x] Once validated:
  - [x] Delete `operations.py`
  - [x] Search codebase for `from database.operations import ...` to confirm no stale direct references
  - [x] Run `grep -r 'operations.py'` or equivalent to confirm full removal

### 8. Documentation
- [x] Update `README.md` if it mentions `operations.py`
- [x] Add quick note in `docs/refactor/` explaining the new split
- [x] Add short docstring at top of each file like:
  ```python
  """User-related database operations (get_or_create_user, platform lookup, etc)."""
  ```

---
## ✅ Verification Checklist

- [x] All functions from `operations.py` accounted for and relocated.
- [x] No circular imports added during the move.
- [x] `main.py`, `queue.py`, `agent.py`, and `handlers.py` still work and import from `database.operations`.
- [x] All modules have valid `__init__.py`.
- [x] No code is importing `operations.py` directly anymore.
- [x] Tests (if any) still pass or load without import errors.