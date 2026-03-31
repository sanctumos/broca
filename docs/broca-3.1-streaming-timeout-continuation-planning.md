# Broca 3.1 Planning: Streaming Timeout, Requeue, and Letta Continuation

Date: 2026-03-28 (expanded)  
Branch target: `broca-3.1`  
Status: Draft — product intent + behavioral detail; API feasibility TBD via tests

## Problem statement

When **`asyncio.wait_for`** (or equivalent) **times out** while Broca is driving a **streaming / long-running** Letta turn, the queue path **atomically dequeues** the item and may **requeue** or **re-send** what is effectively the **same user message**.

On the Letta side, a **new** user message can **interrupt** work already in progress or cause the agent to **restart** a multi-step task instead of **continuing** the prior run.

Operators need Broca to **avoid duplicate “fresh” user turns** when the failure mode is timeout/retry, not new user intent.

## Goal (minor 3.1 improvement)

Choose behavior via **spike tests**, then implement **one** of:

- **Plan B (preferred):** If we can observe that Letta (and the underlying model run) is **still constructing** the assistant response, **stay on the same Broca queue item** and treat it as **the same logical message** — **do not** complete the item as failed, **do not** enqueue a duplicate user turn, and **do not** present a second copy of the inbound text to the agent. Extend local wait via **poll / follow-up read** on Letta’s APIs until the turn **completes**, **fails terminally**, or hits a **separate** operator-configurable cap.
- **Plan A (fallback):** If Plan B is **not** supported or is **unreliable**, keep dequeue/requeue semantics but **annotate** the retried payload so the agent knows it is a **continuation**, e.g.  
  `[Broca: retry 2/5 — continue the prior task; do not restart from scratch.] `  
  plus the original text — or equivalent structured prefix agreed in tests.

If the retried body is **identical** to the previous attempt, the agent should treat it as **continuation of the same task**, not a new assignment.

## Plan B — intended semantics (“meat on the bone”)

When local streaming **times out** but Letta still shows an **in-flight** assistant response or run:

1. **Same queue row** — Keep processing **this** `queue_item` (and its `message_id`). Do not transition to “failed → `requeue_failed_item`” solely because the **local** `wait_for` fired.
2. **Same user message** — Do **not** call `agents.messages.create` again with the same user content. The agent already has the user turn; Broca is waiting for the **outstanding** assistant completion.
3. **Poll / attach** — Use Letta’s HTTP/SDK surface (conversations, messages, runs — **exact endpoint TBD by spike**) to read status until:
   - assistant message is **complete** → then run the normal **response routing** path with the fetched text, mark queue **completed**, etc.; or
   - run enters a **terminal error** → then apply existing **retry / backoff** (may still feed **Plan A** annotation if we choose to resend).
4. **Concurrency** — Still respect **single-flight** semaphore semantics: this item stays “the one” holding the slot until it truly finishes or is abandoned per policy.
5. **Startup / crash** — Distinguish “Broca died mid-poll” from “Letta still running”: `requeue_stale_processing_items` (or successor) may need a flag or timestamp so we don’t **double-submit** after restart; details in implementation once spike clarifies Letta’s idempotency.

Plan B succeeds only if spike tests show a **stable, documented** signal that “response still being built.”

## Non-goals

- Redesigning the entire queue state machine in 3.1 beyond continuation + stale-item clarity.
- Guaranteeing Letta will always obey Plan A hints without model cooperation (Plan A is best-effort framing).

## Investigation / spike tests (blocking decision)

### Primary spike method: send + parallel conversation observation

Long-running turns are **hard to reproduce on demand** (model latency varies, tools may finish quickly). Do **not** rely only on forcing a 30-minute job.

**Recommended procedure:**

1. Use a **minimal blank Letta agent** (or dev-only agent) plus normal API credentials (`LETTA_BASE_URL`, `LETTA_API_KEY`, `LETTA_SPIKE_AGENT_ID`).
2. **Start sending** a user message to the agent (non-streaming or streaming — match what Broca uses in production for the hypothesis under test).
3. **Simultaneously**, on another asyncio task / thread, **poll the conversation/messages endpoint** (exact path per deployed Letta version) on a short interval — e.g. **100–500 ms** — from the moment send begins until the turn is clearly finished.
4. **Log or assert** each snapshot: look for any **in-flight** signal (partial assistant payload, `pending` / `in_progress` run state, message status other than terminal, etc.) **before** the final assistant message is present.

If **any** intermediate state appears reliably, Plan B may be feasible even when the turn completes in a few seconds. If the API only ever shows **terminal** rows (no “still generating” visible from the conversation list), document that gap — Plan B may require a **run-level** or **streaming** API instead of message list alone.

**Optional complement:** After establishing visibility with short turns, repeat with a **deliberately slow** prompt or tool-backed agent to confirm behavior under load; that validates timeout-retry integration but is not the only proof.

### API questions

1. **In-flight detection** — Given `agent_id` + conversation / run id from the initial stream, can we list messages or runs and see **pending / incomplete** assistant output or **`in_progress`**?
2. **Race window** — Right after local timeout, does one GET distinguish “still streaming” vs “failed silently” vs “completed between polls”?
3. **Correlation** — If we **never** resend the user message, can we still attach the **final** assistant text to the **same** Broca `message_id` and `queue_item`?
4. **Double-submit on restart** — After Broca restart, can we reconcile “queue said processing” with Letta’s truth without sending a duplicate user message?

### Test environment (recommended)

- Provision a **minimal blank Letta agent** used only for these experiments (no production traffic).  
  *Example deployment context:* Sanctum stack on the host where Letta already runs (e.g. operator-maintained agent instance); exact host and agent id stay in **env / secrets**, not in this doc.
- **Spike tests** can live under `tests/integration/` or `tests/spike/` with `pytest.mark.integration` and env vars `LETTA_SPIKE_AGENT_ID`, `LETTA_API_KEY`, `LETTA_BASE_URL`.

### Test cases (concrete)

| # | Case | Pass criterion |
|---|------|----------------|
| S0 | **Parallel poll** while sending one normal message (may complete quickly) | Logs show whether conversation endpoint exposes **any in-flight** state; documents API shape for Plan B go/no-go. |
| S1 | Send one user message; local `wait_for` timeout fires; poll Letta | We can **observe** in-flight state (if API supports it) and later **fetch** completed assistant text without a second user message. |
| S2 | Same as S1; Letta completes **between** timeout and first poll | We detect **completed** and map to single assistant reply; no duplicate user turn. |
| S3 | Letta fails run | We detect **terminal failure**; Broca applies existing failure path (no infinite poll). |
| S4 | (If applicable) Restart Broca mid-poll | Stale processing recovery does **not** create a duplicate user message in Letta for the same logical item (or documents accepted limitation). |

Document spike outcomes in PR description or a short `docs/dev-notes/letta-continuation-spike.md` if needed.

## Implementation steps (after spike)

1. Record **Go / No-go** for Plan B at the bottom of this doc (date + signer).
2. If **Plan B go:**
   - Add **continuation poll loop** (with backoff + max wall time) in the timeout branch of `QueueProcessor` / `AgentClient`.
   - Ensure queue status transitions: **processing → completed** only after verified assistant text or terminal error.
   - Wire config: e.g. `BROCA_STREAM_LOCAL_TIMEOUT_SEC`, `BROCA_LETTA_CONTINUATION_POLL_MAX_SEC`, `BROCA_LETTA_CONTINUATION_INTERVAL_SEC`.
3. If **Plan B no-go:** implement Plan A — retry counter on queue item or message metadata, continuation prefix, cap max retries.
4. Operator docs: behavior under timeout; what agents see for Plan A.

## Related code (reference)

- `runtime/core/queue.py` — `asyncio.wait_for` around `_process_with_core_block`, `requeue_failed_item`, `requeue_stale_processing_items`.
- `runtime/core/agent.py` — streaming consumption, run/message/conversation ids.

## Open questions

- Exact Letta **v1** endpoints / fields for “still generating.”
- Where to persist **retry index** for Plan A (queue row vs message metadata JSON).
- Plan A prefix: **English-only** vs configurable template.
- Interaction with **circuit breaker** and **image addendum retry** (avoid double annotation).

## Plan B decision record

| Date | Outcome | Notes |
|------|---------|--------|
| _TBD_ | Go / No-go | Fill after spike **S0**–S4 (S0 = parallel observation). |

## Milestone alignment

Track alongside [release issues](broca-3.1-release-issues.md); may warrant its own GitHub issue once Plan B/A is chosen.
