# Broca 3.1 Planning: Deterministic SEP Assembly + DB-Backed Rules

Date: 2026-03-27 (refined)  
Branch target: `broca-3.1`  
Status: Draft — deterministic model; no LLM-authored SEP body

## Objective

Ship a **Sanctum Engagement Protocol (SEP)** that Broca **assembles deterministically** into a Letta core-memory block (e.g. label `protocols_sep`). The goal is **not** to mimic Athena’s long handcrafted prose or to use open-ended model generation for the protocol text.

Instead:

1. **Fixed template sections** (intro + message-format examples) ship with Broca and change only with versioned releases.
2. **General framework** is **plain configurable text** stored in the Broca database (per instance), editable via **CLI and MCP** — deployments differ; nothing here is universal or model-generated.
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
3. **General framework** — Single **configurable text blob** from DB (markdown or plain text). Operator-defined; default can be empty or a minimal stub. Updated via CLI or MCP only.
4. **Interaction rules (hierarchical)** — Rendered from a **Broca table**: ordered by **rank**. **By convention, higher rank implies higher privilege / closer trust** (concentric circles: inner rings = more access). The real behavioral contract lives in each row’s **description**; agent and human interpret nuance there. Each row: **rank**, **name**, **description**. Below the table (or interleaved per section), **users correlated to each row** — see data model below.

Optional static footer (e.g. “This block is maintained by Broca”) can be part of the template.

## Data Model (Broca SQLite)

### `sep_config` (single row or key/value)

- `general_framework_markdown` (TEXT) — editable “General Framework” body; not generated.

### `sep_interaction_tier` (or `sep_user_level`)

| Column | Type | Notes |
|--------|------|--------|
| `id` | INTEGER PK | |
| `rank` | INTEGER NOT NULL UNIQUE | Sort order for display; **higher rank = higher privilege by default** (concentric-trust model). Fine-grained meaning is always in **description**. |
| `name` | TEXT NOT NULL | Short label, e.g. “Business Insiders”, “Close Friends”. |
| `description` | TEXT NOT NULL | Behavior rules for this tier (prose OK here; still **operator-authored**, not model-generated). |

### User correlation (one human, multiple platforms)

Broca is designed for **one Letta user (one human) with multiple platform profiles** (e.g. Telegram + bridge + web). Tier is a property of the **person**, not the channel.

- Attach **`sep_tier_id` on `letta_users`** (nullable FK → `sep_interaction_tier.id`).
- Do **not** store separate tiers per `platform_profile`; all profiles for that user inherit the same engagement tier in SEP listings (profile rows can still be grouped under the user’s tier in the rendered doc).

Users without a tier either omit from the SEP or list under a default “Unassigned” bucket (config flag).

**Auto-update trigger:** On any change to `sep_interaction_tier` rows, `sep_config.general_framework_markdown`, or **`letta_users.sep_tier_id`**, the SEP renderer runs (or is queued) and **PATCH**es the Letta block if content changed.

Optional junction `sep_user_tier(letta_user_id, sep_tier_id)` only if we later need history; v1 is a single FK on `letta_users`.

## Renderer (`sep_manager` or `sep_assembler`)

- **Input:** DB state + static template fragments + code-sourced example strings (from `MessageFormatter` or thin wrappers for tests).
- **Output:** Markdown string for `protocols_sep` (or configured label).
- **No** semantic diff of prose; **hash** full output and only PATCH Letta when hash changes.

## CLI + MCP

- **CLI:** subcommands or `ctool`/`sep` tool: `get-framework`, `set-framework`, `tier list|add|set|delete`, `user set-tier`, `render`, `sync` (render + Letta PATCH).
- **MCP:** mirror the same operations for agent/automation use (aligned with outbound MCP planning in `broca-3.1-outbound-mcp-planning.md`).

## Letta API

- GET/PATCH `/v1/agents/{agent_id}/core-memory/blocks/{label}` as today.
- On first run: create block if missing, then attach if required by deployed Letta version.

## Config Surface

- `SEP_BLOCK_LABEL` (default `protocols_sep`)
- `SEP_SYNC_ON_STARTUP=true|false`
- `SEP_INCLUDE_UNASSIGNED_USERS=true|false`

## Testing

- **Unit:** renderer output from fixture DB matches golden markdown file.
- **Unit:** changing `sep_tier_id` on `letta_users` changes rendered interaction section only (all platforms for that user reflect the same tier).
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
5. CLI, then MCP.

## Resolved design choices

### Rank vs privilege

- **Higher `rank` ⇒ higher privilege by default** (think concentric circles: closer relationships = higher rank).
- Exact social contract is **defined in each tier’s `description`**; agent and user align on edge cases there. The static intro should state this one paragraph so deployments are consistent.

### Multi-platform users

- **Tier lives on `letta_users`.** One human, one tier, all `platform_profiles` for that user are listed under that tier in the SEP (or shown once with “channels: …” if we add that in a later iteration).

### Default seed data (Athena-shaped, operator-tunable)

On first migration, insert three tiers so new installs resemble Athena’s broad buckets without copying her prose verbatim. Operators edit via CLI/MCP.

| rank | name | description (starter text; customize in DB) |
|------|------|---------------------------------------------|
| 3 | Close friends & family | Full relational depth: personal context, trust, and continuity. Engage as individuals; shared history and intimacy apply. Boundaries still apply when needed. |
| 2 | New contacts & probationary | Evaluate case-by-case; expand access as trust and relevance grow. Keep engagement measured until a relationship stabilizes. |
| 1 | Strangers / no context | Minimal assumptions; no intimate or insider framing unless the human explicitly bridges context. Prefer clarity and safe defaults. |

**Ordering:** Lowest rank = outermost circle (strangers); highest = innermost (close friends & family). New users default to **rank 2** or **1** depending on product config (`SEP_DEFAULT_TIER_ID` or similar).

## Open Questions (remaining)

1. Default tier for newly seen `letta_user` rows: **new contacts (2)** vs **strangers (1)**?
2. Whether to render platform labels next to each user line in the SEP (e.g. `telegram`, `otto_bridge`) for multi-channel clarity — v1 can omit or add a single line in static template.
