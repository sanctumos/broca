# Broca 3.1 Planning: Outbound MCP Messaging

Date: 2026-03-27  
Branch target: `broca-3.1`  
Status: Draft plan approved for implementation planning

## Objective

Add a simple MCP tool in Broca core that can send outbound messages to:

1. any known Broca user (`letta_user_id`), and  
2. any registered delivery channel (`platform`) backed by a loaded plugin.

This enables operator/agent-initiated outbound delivery without running a full inbound message flow.

## Why

Broca already has robust inbound queueing and response routing. What is missing is a direct, auditable outbound API that can target users across platforms from automation tooling.

Desired outcome:
- one tool call,
- explicit recipient,
- explicit channel,
- routed through existing plugin handlers.

## Existing Architecture Constraints

- `PluginManager` already maps `platform -> async handler(response, profile, message_id)`.
- Queue response routing already calls plugin handlers with `(response, profile, message_id)`.
- Platform profiles are stored in `platform_profiles` and tied to `letta_user_id`.
- Current user lookup helpers are not sufficient for `(letta_user_id, platform)` direct resolution in a single call.

## Proposed v1 Scope (3.1)

### Transport choice

Support **both MCP stdio and MCP SSE** in 3.1, configurable at runtime.

Rationale:
- stdio is ideal for local tooling and tightly-coupled agent processes,
- SSE is ideal for remote clients and long-lived external integrations,
- both should share one outbound service implementation so transport does not change routing logic.

Proposed config:
- `OUTBOUND_MCP_ENABLED=true|false`
- `OUTBOUND_MCP_TRANSPORT=stdio|sse|both` (default: `stdio`)
- `OUTBOUND_MCP_SSE_HOST` (default: `127.0.0.1`)
- `OUTBOUND_MCP_SSE_PORT` (default: `8765`)
- `OUTBOUND_MCP_SSE_PATH` (default: `/mcp`)

### MCP Tool

Tool name: `broca_send_outbound`

Arguments:
- `letta_user_id` (int, required)
- `platform` (str, required) - must match a loaded plugin platform
- `message` (str, required)
- `dry_run` (bool, optional, default `false`)
- `idempotency_key` (str, optional, default empty/null)

Return payload:
- `success` (bool)
- `message_id` (int | null)
- `routed_to_platform` (str)
- `platform_user_id` (str | null)
- `delivery_status` (`sent` | `dry_run` | `failed`)
- `error` (str | null)

## Routing Semantics

1. Validate input arguments.
2. Resolve recipient profile by `(letta_user_id, platform)`.
3. Resolve runtime handler via `PluginManager.get_platform_handler(platform)`.
4. Persist outbound message row for auditability.
5. If `dry_run=true`, return without calling handler.
6. Otherwise call plugin handler: `await handler(message, profile, message_id)`.
7. Return structured result.

## Data/Service Additions

### 1) Database operation

Add helper:
- `get_platform_profile_for_user_platform(letta_user_id: int, platform: str) -> PlatformProfile | None`

Purpose:
- deterministic recipient resolution for outbound targeting.

### 2) Outbound service layer

Add module:
- `runtime/core/outbound.py`

Primary function:
- `send_outbound_message(...)`

Responsibilities:
- validation,
- profile lookup,
- platform handler resolution,
- outbound message persistence,
- handler invocation,
- structured errors/results.

### 3) MCP transport entrypoints

Add MCP entrypoints in core that expose `broca_send_outbound` and use the same outbound service:
- stdio server entrypoint
- SSE server entrypoint

Transport adapter behavior:
- `stdio`: process-local command transport
- `sse`: HTTP/SSE listener for remote MCP clients
- `both`: run stdio + SSE concurrently (shared tool registry and service layer)

## Safety and Guardrails

- Feature gate via env var (proposed: `ENABLE_OUTBOUND_MCP=true`).
- Reject empty message payloads.
- Enforce platform must be loaded and routable.
- Return explicit error codes/messages:
  - `profile_not_found`
  - `platform_not_loaded`
  - `handler_not_available`
  - `validation_error`
  - `handler_failed`
- Optional idempotency passthrough for future dedupe/audit behavior.

## Testing Plan

### Unit tests
- profile resolution success/failure
- platform handler lookup failure
- dry-run behavior
- successful delivery path
- handler exception path

### Integration tests
- mocked plugin handler receives expected args
- outbound write is persisted and includes expected identifiers
- transport coverage:
  - stdio tool invoke smoke test
  - SSE tool invoke smoke test

## Rollout Plan

1. Add DB helper + tests.
2. Add outbound core service + tests.
3. Add shared MCP tool registry for outbound tool.
4. Add stdio and SSE transport wrappers + tests.
5. Add docs/examples.
6. Release behind feature flag, then enable per environment.

## Non-goals for 3.1 v1

- Cross-instance/brokered outbound fanout.
- Bulk sends.
- Rich media outbound abstraction beyond existing plugin capabilities.
- New plugin handler contract changes.

## Open Questions (to resolve before coding)

- Outbound DB role value: use `assistant` vs introduce `system_outbound`?
- Should `idempotency_key` be stored in message metadata now or deferred?
- Max message length policy: global cap vs per-platform cap?
- Permission model beyond env flag (operator allowlist, scoped auth, etc.)?
- If `OUTBOUND_MCP_TRANSPORT=both`, should SSE startup failure fail whole process or degrade to stdio-only?

