# Broca 3.1 Planning: Streaming Timeout, Requeue, and Letta Continuation

Date: 2026-03-28  
Branch target: `broca-3.1`  
Status: Draft — product intent recorded; API feasibility TBD via tests

## Problem statement

When **`asyncio.wait_for`** (or equivalent) **times out** while Broca is driving a **streaming / long-running** Letta turn, the queue path **atomically dequeues** the item and may **requeue** or **re-send** what is effectively the **same user message**.

On the Letta side, a **new** user message can **interrupt** work already in progress or cause the agent to **restart** a multi-step task instead of **continuing** the prior run.

Operators need Broca to **avoid duplicate “fresh” user turns** when the failure mode is timeout/retry, not new user intent.

## Goal (minor 3.1 improvement)

Choose behavior via **spike tests**, then implement **one** of:

- **Plan B (preferred):** Before re-sending the user message, use Letta’s **conversation / messages** APIs to detect whether an **in-flight assistant response or run** still exists. If yes, **do not** submit a duplicate user message; **poll or attach** to completion (exact mechanics depend on API capabilities).
- **Plan A (fallback):** If Plan B is **not** supported or is **unreliable**, keep dequeue/requeue semantics but **annotate** the retried payload so the agent knows it is a **continuation**, e.g.  
  `[Broca: retry 2/5 — continue the prior task; do not restart from scratch.] `  
  plus the original text — or equivalent structured prefix agreed in tests.

If the retried body is **identical** to the previous attempt, the agent should treat it as **continuation of the same task**, not a new assignment.

## Non-goals

- Redesigning the entire queue state machine in 3.1 beyond what is needed for timeout continuation.
- Guaranteeing Letta will always obey continuation hints without model cooperation (Plan A is best-effort framing).

## Investigation / spike tests (blocking decision)

1. **Conversation messages API** — Given `agent_id` + conversation id (from stream or follow-up fetch), can we list messages and see:
   - pending / incomplete assistant message,
   - run status (`in_progress`, etc.),
   - or another stable signal that work is still ongoing?

2. **Race window** — Timeout fires while Letta is still writing; does a **single** poll distinguish “still streaming” vs “failed silently”?

3. **Idempotency** — If we **skip** re-sending the user message, how do we **correlate** the eventual assistant reply with the **same** `message_id` / queue row in Broca?

Document results in this folder or in `tests/` with `pytest.mark.integration` as appropriate.

## Implementation steps (after spike)

1. Record **Go / No-go** for Plan B in this doc.
2. If **Plan B go:** implement poll-or-wait path in `QueueProcessor` / `AgentClient` timeout branch; minimal new config (`LETTA_CONTINUATION_POLL_*` or similar).
3. If **Plan B no-go:** implement Plan A — **retry counter** on queue item or message metadata, format continuation prefix, cap max retries (existing backoff may apply).
4. Update operator docs: what agents should assume when they see the continuation tag.

## Related code (reference)

- `runtime/core/queue.py` — `asyncio.wait_for` around `_process_with_core_block`, requeue on timeout/failure.
- `runtime/core/agent.py` — streaming consumption, run/message ids.

## Open questions

- Where to persist **retry index** (queue row vs message metadata JSON).
- Whether continuation note should be **English-only** or configurable.
- Interaction with **circuit breaker** and **image addendum retry** (avoid double annotation).

## Milestone alignment

Track alongside [release issues](broca-3.1-release-issues.md); may warrant its own issue once Plan B/A is chosen.
