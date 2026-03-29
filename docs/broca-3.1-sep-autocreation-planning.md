# Broca 3.1 Planning: Deterministic SEP Assembly + DB-Backed Rules

Date: 2026-03-27 (refined)  
Branch target: `broca-3.1`  
Status: Draft — deterministic model; no LLM-authored SEP body

## Objective

Ship a **Sanctum Engagement Protocol (SEP)** that Broca **assembles deterministically** into a Letta core-memory block (e.g. label `protocols_sep`). The goal is **not** to mimic Athena’s long handcrafted prose or to use open-ended model generation for the protocol text.

Instead:

1. **Fixed template sections** (intro + message-format examples) ship with Broca and change only with versioned releases.
2. **General framework** is **plain configurable text** stored in the Broca database (per instance), editable via **CLI** and optionally **SMCP plugin tools** — deployments differ; nothing here is universal or model-generated.
3. **Interaction rules** are a **structured, hierarchical table** in Broca (rank, name, description). Rows **correlate to users** in the Broca DB; the SEP section that lists engagement behavior **auto-updates** when users or their tier assignments change — tight and predictable, not freewheeling.

## What We Learned From Athena (reference only)

Athena’s live `protocols_sep` block is useful as a **UX reference** for how behavior rules read in practice (sections, bullets, clarity). The **implementation** for Broca 3.1 intentionally avoids copying that level of bespoke narrative generation. Only the **shape** of “rules that read well” informs the rendered layout of the interaction table + framework block.

## Design Principles

| Principle | Meaning |
|-----------|---------|
| Deterministic | Same DB state + same Broca version ⇒ same rendered SEP markdown (byte-stable aside from timestamps if we include them). |
| No LLM for SEP body | Assembly is template + DB rows + optional fixed examples from `MessageFormatter`; no “rewrite SEP with GPT.” |
| Separation of concerns | Static template ≠ configurable framework text ≠ user-correlated tier table. |
| Auto-update where it matters | Re-render and PATCH Letta when **tier assignments or tier definitions or framework text** change — not continuous “creative” refresh. |

## SEP Document Structure (render order)

Rendered output is a **fixed pipeline** (order must not vary between runs except for explicit versioning):

1. **Static intro block** — Versioned markdown (or template file) in repo: what SEP is, scope, that middleware routes replies, etc. No DB.
2. **Message format** — Static section documenting how Broca formats inbound messages. Include **one or two concrete examples** taken from the real code path (e.g. `MessageFormatter.format_message` / Telegram vs generic platform label) so the agent sees the exact prefix pattern it will receive. Examples must stay in sync with code in the same release (tests can assert substrings or snapshot).
3. **General framework** — Single **configurable text blob** from DB (markdown or plain text). Operator-defined; default can be empty or a minimal stub. Updated via CLI or SMCP plugin only.
4. **Interaction rules (hierarchical)** — Rendered from a **Broca table**: ordered by **rank**. **Higher rank = closer relationship tier** (inner concentric circle: more trust, more access, warmer default engagement). Nuance and edge cases live in each row’s **description**. Each row: **rank**, **name**, **description**. Below the table (or interleaved per section), **users correlated to each row** — see data model below. **SEP does not name or branch on platform** — if the message reached the agent through Broca, delivery is Broca-handled; platform is an implementation detail outside SEP.

Optional static footer (e.g. “This block is maintained by Broca”) can be part of the template.

## Data Model (Broca SQLite)

### `sep_config` (single row or key/value)

- `general_framework_markdown` (TEXT) — editable “General Framework” body; not generated.

### `sep_interaction_tier` (or `sep_user_level`)

| Column | Type | Notes |
|--------|------|--------|
| `id` | INTEGER PK | |
| `rank` | INTEGER NOT NULL UNIQUE | Sort order for display; **higher rank = closer tier** (inner circle). Fine-grained meaning is always in **description**. |
| `name` | TEXT NOT NULL | Short label, e.g. “Business Insiders”, “Close Friends”. |
| `description` | TEXT NOT NULL | Behavior rules for this tier (prose OK here; still **operator-authored**, not model-generated). |

### User correlation (one human; platform out of SEP)

Broca may attach multiple `platform_profiles` to one `letta_user`; tier is still a property of the **person**.

- **`sep_tier_id` on `letta_users`** (nullable FK → `sep_interaction_tier.id`). Not per `platform_profile`.
- **SEP rendering lists people under tiers only** — no platform labels, no per-channel breakdown. Broca is the boundary; how the user reached Broca does not belong in SEP.

Users without a tier either omit from the SEP or list under a default “Unassigned” bucket (config flag).

**Auto-update trigger:** On any change to `sep_interaction_tier` rows, `sep_config.general_framework_markdown`, or **`letta_users.sep_tier_id`**, the SEP renderer runs (or is queued) and **PATCH**es the Letta block if content changed.

Optional junction `sep_user_tier(letta_user_id, sep_tier_id)` only if we later need history; v1 is a single FK on `letta_users`.

## Renderer (`sep_manager` or `sep_assembler`)

- **Input:** DB state + static template fragments + code-sourced example strings (from `MessageFormatter` or thin wrappers for tests).
- **Output:** Markdown string for `protocols_sep` (or configured label).
- **No** semantic diff of prose; **hash** full output and only PATCH Letta when hash changes.

## CLI + SMCP plugins

- **CLI:** subcommands or `ctool`/`sep` tool: `get-framework`, `set-framework`, `tier list|add|set|delete`, `user set-tier`, `render`, `sync` (render + Letta PATCH).
- **Agent/automation surface:** same operations exposed as **SMCP plugin tools** (not a separate MCP server inside Broca). See `broca-3.1-outbound-mcp-planning.md` for the same pattern.

## Letta API

- GET/PATCH `/v1/agents/{agent_id}/core-memory/blocks/{label}` as today.
- On first run: create block if missing, then attach if required by deployed Letta version.

## Config Surface

- `SEP_BLOCK_LABEL` (default `protocols_sep`)
- `SEP_SYNC_ON_STARTUP=true|false`
- `SEP_INCLUDE_UNASSIGNED_USERS=true|false`
- Default tier for new `letta_users`: **strangers** (seed tier with lowest rank); no separate env required unless we add override later (`SEP_DEFAULT_TIER_ID`).

## Testing

- **Unit:** renderer output from fixture DB matches golden markdown file.
- **Unit:** changing `sep_tier_id` on `letta_users` changes rendered interaction section only (user moves between tiers; SEP has no platform dimension).
- **Integration:** mock Letta PATCH; assert called when tier assignment changes.

## Non-goals (3.1)

- LLM-generated SEP sections.
- “Persona swap” style long-form narrative maintenance inside Broca.
- Semantic drift scoring or model-based diff between SEP versions.

## Rollout

1. Migration: `sep_config`, `sep_interaction_tier`, nullable `letta_users.sep_tier_id` → `sep_interaction_tier.id`.
2. Seed tiers (below) + optional `general_framework_markdown` empty string.
3. Static template + examples wired to formatter.
4. Renderer + hash + Letta sync.
5. CLI, then SMCP plugin (optional companion repo under `sanctumos/smcp` plugins).

## Resolved design choices

### Rank vs closeness

- **Higher `rank` ⇒ closer tier** (inner concentric circle: more trust and intimacy by default, not “abstract privilege”).
- Edge cases are **defined in each tier’s `description`**; agent and human align there. The static intro should state rank = closeness in one short paragraph.

### Platform

- **Not represented in SEP.** Tier is on `letta_users`; rendered lists are person-centric only.

### Default seed data (Athena-shaped, operator-tunable)

On first migration, insert three tiers so new installs resemble Athena’s broad buckets without copying her prose verbatim. Operators edit via CLI or SMCP plugin.

| rank | name | description (starter text; customize in DB) |
|------|------|---------------------------------------------|
| 3 | Close friends & family | Full relational depth: personal context, trust, and continuity. Engage as individuals; shared history and intimacy apply. Boundaries still apply when needed. |
| 2 | New contacts & probationary | Evaluate case-by-case; expand access as trust and relevance grow. Keep engagement measured until a relationship stabilizes. |
| 1 | Strangers / no context | Minimal assumptions; no intimate or insider framing unless the human explicitly bridges context. Prefer clarity and safe defaults. |

**Ordering:** Lowest rank = outermost circle (**strangers**); highest = innermost (**close friends & family**).

**Newly seen `letta_user`:** default **`sep_tier_id` = strangers tier** (rank **1** in the seed above). Operators promote users via CLI or SMCP plugin when trust grows.
