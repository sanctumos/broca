# Broca 3.1 Planning: Outbound Messaging via SMCP (not a Broca MCP server)

Date: 2026-03-27 (revised)  
Branch target: `broca-3.1`  
Status: Draft — SMCP plugin surface; Broca owns logic + stable invoke contract

## Objective

Enable **outbound** messages to any Broca user on a chosen **platform** (loaded plugin), without a full inbound queue turn.

**Exposure:** MCP tools live in **Sanctum Letta MCP (SMCP)** as **plugins**, not as a dedicated MCP server inside Broca.

**Broca owns:** deterministic routing, DB, audit row, plugin handler invocation.

## Why SMCP instead of a full Broca MCP server

- SMCP already provides MCP transport (however the host runs it: stdio, SSE, etc.) and plugin discovery.
- Avoids a **second** MCP stack, port, and lifecycle inside Broca.
- Keeps Broca **CLI-first / scriptable**; SMCP remains the standard “agent tool” boundary for Letta-shaped runtimes.
- One new **SMCP plugin** (or small plugin repo) can wrap Broca without forking core networking.

## Broca-side deliverables (3.1)

### 1) Database

- `get_platform_profile_for_user_platform(letta_user_id: int, platform: str) -> PlatformProfile | None`

### 2) Outbound service

- Module: `runtime/core/outbound.py`
- `send_outbound_message(...)` — validate, resolve profile + handler, persist audit message, optional `dry_run`, call `PluginManager` platform handler.

### 3) Stable invoke contract (pick one primary; document the other if deferred)

**Preferred for v1:** **CLI** under `cli/` (e.g. `python -m cli.outbound` or extend `btool`) with JSON on stdout / exit codes, so SMCP plugin = thin subprocess wrapper (matches Broca’s existing MCP’able CLI story).

**Optional later:** minimal local HTTP or Unix socket on Broca process — only if subprocess proves too heavy for multi-tenant hosts.

Broca does **not** ship its own MCP stdio/SSE server for outbound in 3.1.

## SMCP-side deliverables

- **Broca repo `smcp/broca`:** SMCP plugin registers tools mirroring the CLI (e.g. `send_outbound`):
  - `broca_send_outbound` (same arguments/semantics as below)
- Plugin config: path to Broca instance / venv, or `BROCA_ROOT`, `BROCA_PYTHON`, etc.
- Transport (stdio vs SSE) is **SMCP’s** concern, not Broca’s.

## Tool semantics (unchanged)

Tool name (as seen by agents via SMCP): `broca_send_outbound`

Arguments:

- `letta_user_id` (int, required)
- `platform` (str, required) — must match a loaded plugin platform on that Broca instance
- `message` (str, required)
- `dry_run` (bool, optional, default `false`)
- `idempotency_key` (str, optional)

Return payload (JSON):

- `success`, `message_id`, `routed_to_platform`, `platform_user_id`, `delivery_status`, `error`

## Routing semantics

1. Validate arguments.  
2. Resolve `(letta_user_id, platform)` → `PlatformProfile`.  
3. `PluginManager.get_platform_handler(platform)`.  
4. Persist outbound audit row.  
5. If `dry_run`, skip handler.  
6. Else `await handler(message, profile, message_id)`.  
7. Return structured result.

## Safety and guardrails

- Feature gate in Broca (e.g. `ENABLE_OUTBOUND_TOOL=true`) so headless sends are opt-in.
- Same error taxonomy: `profile_not_found`, `platform_not_loaded`, `handler_failed`, etc.
- SMCP plugin should not embed secrets; read from env or Broca `.env` on the host.

## Testing

**Broca:** unit + integration tests for `outbound.py` and CLI (mock handler).

**SMCP plugin:** smoke test that invokes CLI against a fixture Broca or mocked subprocess.

## Rollout

1. Broca: DB helper + `outbound.py` + CLI + tests + docs.  
2. SMCP: new plugin + README + example config.  
3. Enable per environment (`ENABLE_OUTBOUND_TOOL`, SMCP plugin install).

## Non-goals (3.1)

- Broca-embedded MCP server (stdio/SSE) for outbound.  
- Cross-instance fanout, bulk send, new plugin handler signatures.

## Open questions

- CLI vs local socket as the **only** v1 contract (recommend CLI first).  
- Outbound DB role: `assistant` vs `system_outbound`.  
- `idempotency_key` persistence on message row now vs later.  
- Max message length: global vs per-platform.

## Related

- SEP framework/tier editing via MCP in `broca-3.1-sep-autocreation-planning.md` can follow the **same pattern**: Broca CLI + **SMCP plugin** tools, not a Broca MCP server.
