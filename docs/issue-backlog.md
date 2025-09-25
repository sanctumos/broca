Sanctum: Broca 2 – Backlog of Issues

This document tracks proposed GitHub issues while repository Issues are disabled. Once Issues are enabled, use the helper script in `scripts/create_issues.sh` to open them automatically.

Top recommendations (high priority)

1) Fix settings hot-reload: add force_reload to get_settings() and use in watcher
- Problem: settings hot-reload never re-reads due to global cache in `common/config.py:get_settings`.
- Evidence: see lines 72-79, 90-96 of `common/config.py`.
- Proposed fix:
  - Add parameter `force_reload: bool=False` to bypass cache
  - Update settings watcher in `main.Application._check_settings` to force reload
  - Consider pydantic model for typed settings and validation
- Acceptance criteria:
  - Editing `settings.json` updates running app without restart
  - Unit tests cover reload path and validation errors

2) Standardize database layer paths and backend
- Problem: Mixed use of `sanctum.db` (aiosqlite) and `broca.db` (SQLAlchemy), causing confusion and potential split writes.
- Evidence: `database/session.py` vs `database/operations/*` DB_PATHs.
- Proposed fix:
  - Choose async aiosqlite (current) or migrate to SQLAlchemy AsyncEngine
  - Centralize DB path via env var and one module
  - Remove unused sync SQLAlchemy session if not used
- Acceptance criteria: Single configured DB path used across all modules, tests pass.

3) Mark messages as processed when storing agent responses
- Problem: `processed` flag remains 0, breaking history queries.
- Evidence: `update_message_with_response()` does not set `processed = 1`; history query filters `processed = 1`.
- Proposed fix: Set `processed = 1` there or always call `update_message_status()` in queue.
- Acceptance criteria: After response, message appears in history; tests added.

4) Add a "processing" queue state to prevent duplicate work
- Problem: Items are read as `pending` without atomically transitioning to `processing`.
- Evidence: `get_pending_queue_item()` selects pending; queue loop tracks in-memory only.
- Proposed fix: Transition to `processing` on dequeue in the same transaction; increment attempts.
- Acceptance criteria: No duplicate processing under concurrency; tests simulate concurrency.

5) Add aiosqlite and pin dependency versions
- Problem: `aiosqlite` used but missing from requirements; versions unpinned.
- Proposed fix: Add `aiosqlite==<version>`; pin all deps; add dev requirements.
- Acceptance criteria: Clean install with pinned versions; CI lock updated.

6) Centralize logging and remove sensitive data from logs
- Problem: Multiple modules call `setup_logging()`; API key prefix logged.
- Evidence: `runtime/core/letta_client.py` logs API key prefix.
- Proposed fix: Configure logging in `main.py` only; remove API key logging; consider structured logging.
- Acceptance criteria: Single logger setup; no secret leakage; tests for logger init once.

7) Graceful shutdown and task management
- Problem: Inner KeyboardInterrupt swallows cleanup path; tasks may continue.
- Proposed fix: Ensure Ctrl-C leads to `await app.stop()`; cancel background tasks; remove PID file reliably.
- Acceptance criteria: Clean shutdown under Ctrl-C; tasks stopped; PID removed.

8) Typed configuration with pydantic
- Problem: Ad-hoc coercion in `validate_settings()`; mutations of dict.
- Proposed fix: Introduce `Settings` model; parse and validate; support `force_reload` path.
- Acceptance criteria: Type-safe config; unit tests for coercion and validation.

9) Harden plugin discovery and handler contracts
- Problem: Import by file stem may collide; handler signature not enforced.
- Proposed fix: Import by package path; validate handler signature at load.
- Acceptance criteria: Loading prevents collisions; invalid handlers rejected with clear errors.

10) Align docs and repo artifacts
- Problem: Docs reference `.env.example`, structured/rotating logs; not present.
- Proposed fix: Add `.env.example`; document actual logging or implement structured/rotation.
- Acceptance criteria: Docs match implementation; onboarding verified.

Additional improvements (medium/low priority)

- CI/CD pipeline
  - Add GitHub Actions for lint (ruff/flake8), type-check (mypy), tests (pytest)
  - Require checks on PRs

- Code style & quality
  - Add ruff + black; pre-commit hooks; mypy strict in `runtime/core` and `common`

- Retry/backoff logic
  - Add exponential backoff for Letta API and queue retries

- Metrics and health
  - Add queue depth/throughput metrics; optional health endpoint or logs

- PID file hygiene
  - Write under `run/` and ensure removal via finally/atexit

- Security and paths
  - Move runtime artifacts (`settings.json`, `sanctum.db`, `telegram_ignore_list.json`) under per-instance directories
  - Update `.gitignore` accordingly

- Batch queue improvements
  - Support batch dequeue for throughput under load

Usage note

- When repository Issues are enabled, run `scripts/create_issues.sh` to open all items automatically with titles, bodies, and labels.

