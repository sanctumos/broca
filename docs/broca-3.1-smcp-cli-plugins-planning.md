# Broca 3.1 Planning: SMCP Plugins for Core CLI Tools

Date: 2026-03-28  
Branch target: `broca-3.1`  
Status: Draft — inventory + rollout plan

## Goal

Expose **every core Broca CLI capability** to Letta-shaped agents via **SMCP plugins**, using the same pattern as [outbound messaging](broca-3.1-outbound-mcp-planning.md): **Broca owns CLIs and logic**; **SMCP owns MCP tool registration and transport** (stdio/SSE as configured on the SMCP host).

## Inventory: Core CLI modules (`cli/`)

The repo ships **five** executable CLI modules (plus a sample `cli/settings.json`, not a tool).

| Module | `python -m` | Purpose | Commands / subcommands | `--json` | Notes |
|--------|-------------|---------|------------------------|----------|--------|
| **qtool** | `cli.qtool` | Queue | `list`; `flush --all \| --id`; `delete --all \| --id` | Yes | Mutating; `flush`/`delete --all` are high impact. |
| **utool** | `cli.utool` | Users (Letta users / profile summary) | `list`; `get <id>`; `update <id> active\|inactive` | Yes | `update` mutates DB. |
| **ctool** | `cli.ctool` | **Conversations** (message history view) | `list`; `get <letta_user_id> <platform_profile_id> [--limit]` | Yes | Name is historical; not “config tool.” Read-only. |
| **settings** | `cli.settings` | `settings.json` (legacy flat keys) | `get`; `mode echo\|listen\|live`; `debug --enable\|--disable`; `refresh <seconds>`; `retries <n>`; `reload` | Yes | Mutates file; may diverge from Pydantic `common.config` in some installs — document dual source of truth risk. |
| **btool** | `cli.btool` | Telegram **bot ignore list** (`telegram_ignore_list.json`) | `add <identifier> [--id]`; `remove <identifier>`; `list` | **No** | File-local to CWD; not DB. |

### Documentation drift (fix in 3.1 docs pass)

`docs/cli_reference.md` describes **`btool` as a unified hub** (queue, users, status, plugins). **That does not match the current codebase** — `btool` is only the ignore-list tool. Queue/users/settings are separate modules. Planning SMCP plugins should follow **actual modules**, and README/cli_reference should be corrected so operators are not misled.

## Design: SMCP plugin layout

### Option A — One plugin repo (recommended for v1)

**Single SMCP plugin** shipped **in this repository** under **`smcp/broca/`** (set `MCP_PLUGINS_DIR` to **`smcp/`**). Older drafts referred to `sanctumos/smcp/plugins/…`; **Broca** owns the plugin tree now. It registers **namespaced tools**:

- `broca_queue_list`, `broca_queue_flush`, `broca_queue_delete`
- `broca_user_list`, `broca_user_get`, `broca_user_set_status`
- `broca_conversation_list`, `broca_conversation_get`
- `broca_settings_get`, `broca_settings_set_mode`, … (one tool per mutating subcommand or grouped with a `command` enum)
- `broca_telegram_ignore_add`, `broca_telegram_ignore_remove`, `broca_telegram_ignore_list`

**Pros:** one install, one config block (`BROCA_ROOT`, `BROCA_PYTHON`, working directory).  
**Cons:** large tool surface; needs clear descriptions and danger tags for destructive ops.

### Option B — One plugin per CLI module

Five thin plugins (`smcp-broca-qtool`, …) each wrapping one `python -m cli.*`.

**Pros:** optional installs, blast radius.  
**Cons:** duplicated config, version skew, more repos to maintain.

**Recommendation:** **Option A** for 3.1; split later only if install size or security policy demands it.

## Invocation contract

Each SMCP tool implementation:

1. Sets `cwd` to the **target Broca agent instance** (directory with `sanctum.db`, `.env`, `settings.json` as applicable).
2. Runs:  
   `"{BROCA_PYTHON}" -m cli.<module> ... --json`  
   (always request JSON when the CLI supports it).
3. Parses stdout as JSON **or** captures structured exit codes + stderr on failure.
4. Returns MCP content as JSON text for the agent.

**Config (SMCP plugin env):**

- `BROCA_ROOT` — default working directory for the instance  
- `BROCA_PYTHON` — interpreter (venv) that has Broca deps  
- Optional: `BROCA_INSTANCE_DIR` override per tool call for multi-agent hosts

## Broca-side hardening (before or with plugins)

1. **`btool`: add `--json`**  
   - Today output is plain text only; SMCP and scripts need machine-readable list/add/remove results.

2. **Unified exit codes**  
   - Document: `0` success, `1` user error, `2` system/DB error (align with outbound CLI when added).

3. **Destructive guard (optional)**  
   - Env `BROCA_CLI_ALLOW_DESTRUCTIVE=1` required for `qtool flush/delete --all` when stdin is not a TTY — reduces accidental agent wipes. SMCP sets this only on explicit operator-enabled profiles.

4. **Doc fix**  
   - Update `docs/cli_reference.md` to match real `qtool` / `utool` / `ctool` / `settings` / `btool` split.

## Tool ↔ CLI mapping (concrete)

| SMCP tool (proposed) | CLI equivalent |
|---------------------|----------------|
| `broca_queue_list` | `python -m cli.qtool list --json` |
| `broca_queue_flush` | `python -m cli.qtool flush --id N` or `--all` |
| `broca_queue_delete` | `python -m cli.qtool delete --id N` or `--all` |
| `broca_user_list` | `python -m cli.utool list --json` |
| `broca_user_get` | `python -m cli.utool get ID --json` |
| `broca_user_set_status` | `python -m cli.utool update ID active\|inactive --json` |
| `broca_conversation_list` | `python -m cli.ctool list --json` |
| `broca_conversation_get` | `python -m cli.ctool get USER_ID PLATFORM_ID --limit N --json` |
| `broca_settings_get` | `python -m cli.settings get --json` |
| `broca_settings_set_message_mode` | `python -m cli.settings mode live` (+ `--json`) |
| `broca_settings_set_debug` | `python -m cli.settings debug --enable` / `--disable` |
| `broca_settings_set_queue_refresh` | `python -m cli.settings refresh SECONDS` |
| `broca_settings_set_max_retries` | `python -m cli.settings retries N` |
| `broca_settings_reload` | `python -m cli.settings reload --json` |
| `broca_telegram_ignore_list` | `python -m cli.btool list` (add `--json` first) |
| `broca_telegram_ignore_add` | `python -m cli.btool add …` |
| `broca_telegram_ignore_remove` | `python -m cli.btool remove …` |

**Future (same plugin family):** tools for [outbound send](broca-3.1-outbound-mcp-planning.md) and [SEP](broca-3.1-sep-autocreation-planning.md) once those CLIs exist.

## Safety tiers for MCP tool metadata

Tag tools in plugin manifest / descriptions:

- **read_only** — list/get  
- **mutating** — update status, settings, ignore list  
- **destructive** — queue flush/delete, especially `--all`

Optionally split into two SMCP plugin entrypoints (read vs write) so hosts can enable read-only for untrusted agents.

## Testing

| Layer | What |
|-------|------|
| Broca | Existing CLI unit tests; add `btool --json` tests. |
| SMCP plugin | Integration tests with mocked `subprocess.run` and golden argv/env. |
| E2E | Optional: Docker compose Broca + SMCP, single tool smoke. |

## Rollout order

1. Broca: `btool --json`, doc fix, optional destructive env gate.  
2. **Broca repo `smcp/broca`:** publish read-only tools first; point `MCP_PLUGINS_DIR` at `smcp/`.  
3. Enable mutating tools on operator hosts.  
4. Enable destructive tools only with explicit config.  
5. Add outbound + SEP tools when those CLIs land.

## Non-goals (3.1)

- Reimplementing CLI logic inside SMCP (no duplicate DB access from the plugin).  
- Embedding MCP server in Broca (see outbound plan).  
- Remote Broca over SSH from SMCP (separate “remote instance” story; v1 is local path + python).

## Open questions

1. Should `settings.py` be merged long-term into `ctool` rename vs keep as-is (naming confusion)?  
2. Single `BROCA_ROOT` vs per-agent tool parameter for multi-instance on one host?  
3. Whether `ctool get` should accept logical user keys (username) instead of raw `platform_profile_id` for agent ergonomics — would require Broca CLI enhancement.
