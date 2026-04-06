# Broca 3.1 Planning: Streaming Timeout, Requeue, and Letta Continuation

| Field | Value |
|--------|--------|
| **Status** | **Adopted — canonical implementation plan** (engineering design locked; code to follow on `broca-3.1`) |
| **Branch target** | `broca-3.1` |
| **Last updated** | 2026-04-06 |

**Changelog (high level):** 2026-03-28 expanded problem/goals; 2026-03-31 conversation-first-on-timeout + spike script; 2026-04-06 DNS/long-task spike validated `agents.messages.list` + `run_id` / `otid` correlation — **Plan B go**; this document now **is** the build spec.

---

## Problem statement

When **`asyncio.wait_for`** (or equivalent) **times out** while Broca is driving a **streaming / long-running** Letta turn, Broca today falls through to **`_fallback_to_async`**, which calls **`agents.messages.create_async`** with the **same user text again**.

On the Letta side that is a **second user turn** while the first run may still be executing (reasoning, tools, partial assistant). The agent can **restart** work, **interleave**, or behave inconsistently.

Operators need Broca to treat **local stream read timeout** as **“stop reading SSE, not abandon the turn”** and to **observe the same run** via HTTP until there is a **terminal assistant message** or **terminal failure**, without duplicating the user payload.

---

## Spike outcomes (why this plan)

Interactive spike: `scripts/letta_stream_timeout_conversation_poll_spike.py`.

Findings on live Sanctum Letta (e.g. `sanctum.zero1.network:8443`, Ada-class agent):

1. **`conversation_id` may stay `null` on stream events** even while the run is healthy.
2. **`agents.messages.list`** still shows **actionable progress**: `reasoning_message`, `tool_call_message`, `tool_return_message`, each with **`run_id`** (and user rows with **`otid`**).
3. **Polling that list on an interval** after a **forced local stream timeout** shows the run **advancing** without sending a second user message.

**Implication:** Implementation must **not** depend on `conversation_id` alone. **`run_id` + `otid`** correlation is the portable spine; `conversations.messages.list` remains the fast path when `conversation_id` exists.

---

## Canonical plan (adopted) — `AgentClient` / queue behavior

### A. One stable `otid` per Broca turn

- Generate **`otid` once** at the start of `process_message_async` (or equivalent single entrypoint for a queue item).
- Pass it into **`_user_message_list`** so the same value is sent to Letta and **logged** (debug).
- After any timeout or stream error, use this **`otid`** to find the **`user_message`** row in **`agents.messages.list`** and read its **`run_id`** if the stream did not already capture `run_id`.

### B. Hoisted stream state (survives `wait_for` cancellation)

`asyncio.wait_for` **cancels** the inner coroutine; **locals** inside `_process_with_streaming` are unreliable after cancel.

- Allocate a **mutable dict** in the outer scope, e.g. `stream_state = {"run_id": None, "conversation_id": None, "message_id": None, "last_assistant_content": None}`, updated **on every stream event** inside the consumer loop.
- Extend extraction to capture **`run_id`** from `event.run.id` (and any SDK-shaped equivalents on tool/reasoning events), mirroring existing `conversation_id` extraction.

### C. Continuation phase — **before** `_fallback_to_async` on timeout

On **`asyncio.TimeoutError`** from the outer wait (and optionally on stream read errors **if** `stream_state` already shows a `run_id`):

1. **Resolve `run_id`:** `stream_state["run_id"]`, else scan **`agents.messages.list`** (sufficient `limit`, e.g. 80–100) for a **`user_message`** whose **`otid`** matches this turn, then use that row’s **`run_id`**.
2. **If `conversation_id` is known:** call **`conversations.messages.list`** as today; prefer assistant content for the active turn when unambiguous.
3. **Poll loop** (bounded wall time — see env below):
   - **`runs.retrieve(run_id)`** when it exposes terminal status useful for stopping.
   - **`agents.messages.list`**, filter rows with **`run_id` == ours**, newest first; detect a new **`assistant_message`** / **`assistant`** with extractable content → **success** (reuse `_extract_content`).
   - Sleep **backoff interval** between polls (e.g. 2–5 s).
4. **Stop** on success, Letta-reported terminal failure, or **max continuation wall**.

### D. Deprecate default “timeout → duplicate user message”

- **Do not** call **`_fallback_to_async`** (second `create_async` with same text) when:
  - `stream_state` has **`run_id`**, or
  - a **`user_message`** with this turn’s **`otid`** appears in **`agents.messages.list`** (run admitted).
- **Only** when there is **no** evidence the first turn was admitted (no matching `otid`, no `run_id`, `runs` empty / 404 as appropriate) may Broca fall back to **`create_async`**, **Plan A** annotated resend, or hard failure — product decision per env flag.

### E. Optional: split stream-read budget vs total turn budget

- **`BROCA_STREAM_READ_MAX_SEC`** (optional): stop **reading** the SSE iterator and enter **continuation poll** early (models that “think” long before emitting much).
- **`LONG_TASK_MAX_WAIT`** (existing): cap **end-to-end** wall time for stream read + continuation **together**, or define **`BROCA_LETTA_CONTINUATION_POLL_MAX_SEC`** as additional cap after stream phase — pick one scheme and document in `docs/configuration.md`.

Minimum viable: keep **one** outer `LONG_TASK_MAX_WAIT` but **restructure** so continuation counts inside it (no second user send in the middle).

### F. Queue layer (`runtime/core/queue.py`)

- The queue’s **`asyncio.wait_for`** around message processing must be **≥** the agent client’s **total** budget (stream + continuation), or the worker will be killed mid-poll.
- Derive queue timeout from the same env knobs or document **ordering**: queue timeout must dominate.

### G. Tests

- **Unit:** continuation helper with mocked `agents.messages.list` / `runs.retrieve` returning progressive rows (reasoning → tool → assistant).
- **Integration / spike parity:** short stream read + multi-step tool prompt; assert **no second `create_async`** and **single** `assistant_message` for the `otid`.

### H. Configuration (names — finalize in implementation PR)

| Variable | Intent |
|----------|--------|
| `LONG_TASK_MAX_WAIT` | Existing outer cap (align queue + agent). |
| `BROCA_LETTA_CONTINUATION_INTERVAL_SEC` | Sleep between continuation polls. |
| `BROCA_LETTA_CONTINUATION_POLL_MAX_SEC` | Max wall time for continuation-only phase (if split from stream). |
| `BROCA_STREAM_READ_MAX_SEC` | Optional: stop SSE read early, then continue polling. |
| `BROCA_ALLOW_CREATE_ASYNC_ON_TIMEOUT` | Default **false** when `run_id` or `otid` match exists; escape hatch for broken Letta behavior. |

---

## Plan A (fallback — only if Plan B cannot complete)

If continuation polling **cannot** produce an assistant message and **`runs.retrieve` / message history** show terminal failure (or cap exceeded):

- Keep dequeue/requeue semantics if product requires, but **annotate** retried payload so the agent knows it is a **continuation**, e.g.  
  `[Broca: retry 2/5 — continue the prior task; do not restart from scratch.] `  
  plus the original text — or equivalent structured prefix agreed in tests.

Plan A is **best-effort**; prefer **not** to hit it when `run_id` correlation works.

---

## Conversation-first ordering (operator analogy)

On timeout, **poll Letta HTTP surfaces before** treating the turn as failed or resending user text:

1. **`conversations.messages.list`** if `conversation_id` known.
2. **`runs.retrieve(run_id)`** + **`agents.messages.list`** filtered by `run_id`.
3. **Resolve `run_id` via `otid`** on the user message if stream never yielded ids.

This mirrors **polling Broca outbox / queue** when Ada or Athena are slow: check **what the system already has** before assuming **nothing is running**.

**Spike tooling:** `scripts/letta_stream_timeout_conversation_poll_spike.py` — REPL or `-m`; `--follow-up-polls` for repeated `agents.messages.list` snapshots.

---

## Non-goals (unchanged)

- Full queue state-machine redesign beyond continuation + stale-item clarity.
- Proof that models always obey Plan A hints.

---

## Legacy investigation notes

Parallel stream + poll experiments (S0–S4) informed design; **DNS / long-tool spike (2026-04-06)** satisfied **go** for Plan B on current Letta deployment.

| # | Case | Pass criterion |
|---|------|----------------|
| S0 | Parallel poll while sending | Expose in-flight shape in API. |
| S1 | Timeout then poll | Observe in-flight; later assistant without second user message. |
| S2 | Complete between timeout and poll | Single assistant reply. |
| S3 | Letta fails run | Terminal failure path; no infinite poll. |
| S4 | Restart mid-poll | No duplicate user message for same logical item (or document limitation). |

---

## Plan B decision record

| Date | Outcome | Notes |
|------|---------|--------|
| **2026-04-06** | **Go** | DNS / multi-tool Ada run under forced local stream timeout; **`agents.messages.list`** showed monotonic progress by **`run_id`**; **`otid`** correlates user turn. Implement continuation phase in `runtime/core/agent.py` + align `queue.py` timeouts. |

---

## Related code (implementation targets)

- `runtime/core/agent.py` — `process_message_async`, `_process_with_streaming`, `_fallback_to_async`; add **`_continuation_poll_after_stream_timeout`** (name TBD) and hoisted **`stream_state`** + per-turn **`otid`**.
- `runtime/core/queue.py` — `asyncio.wait_for` timeout vs `LONG_TASK_MAX_WAIT` / continuation caps.

---

## Open questions (smaller)

- Exact **Letta v1** field stability for `run_id` on all message types (monitor across upgrades).
- Where to persist **Plan A retry index** (queue row vs metadata JSON).
- Plan A prefix: **English-only** vs configurable template.
- Interaction with **circuit breaker** and **image addendum retry** (avoid double annotation).

---

## Milestone alignment

Track alongside [release issues](broca-3.1-release-issues.md); implementation PR should reference this doc and close or update any dedicated GitHub issue for streaming continuation.
