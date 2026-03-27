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
4. **Interaction rules (hierarchical)** — Rendered from a **Broca table**: ordered by **rank** (lower = higher precedence or “stricter tier” — exact semantics documented in one line in the static intro). Each row: **rank**, **name**, **description**. Below the table (or interleaved per section), **users correlated to each row** — see data model below.

Optional static footer (e.g. “This block is maintained by Broca”) can be part of the template.

## Data Model (Broca SQLite)

### `sep_config` (single row or key/value)

- `general_framework_markdown` (TEXT) — editable “General Framework” body; not generated.

### `sep_interaction_tier` (or `sep_user_level`)

| Column | Type | Notes |
|--------|------|--------|
| `id` | INTEGER PK | |
| `rank` | INTEGER NOT NULL UNIQUE | Sort order for display and hierarchy (lower first = higher tier, or the inverse — pick one convention and document in static intro). |
| `name` | TEXT NOT NULL | Short label, e.g. “Business Insiders”, “Close Friends”. |
| `description` | TEXT NOT NULL | Behavior rules for this tier (prose OK here; still **operator-authored**, not model-generated). |

### User correlation

**`platform_profiles` or `letta_users`** gains a nullable FK:

- `sep_tier_id` → `sep_interaction_tier.id`

Users without a tier either omit from the SEP or list under a default “Unassigned” bucket (config flag).

**Auto-update trigger:** On any change to `sep_interaction_tier` rows, `sep_config.general_framework_markdown`, or user `sep_tier_id` assignments, the SEP renderer runs (or is queued) and **PATCH**es the Letta block if content changed.

Alternative if you prefer not to FK from profile: junction table `sep_user_tier(letta_user_id, sep_tier_id)` with unique constraint on `letta_user_id`. Same semantics.

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
- **Unit:** changing `sep_tier_id` on a user changes rendered interaction section only.
- **Integration:** mock Letta PATCH; assert called when tier assignment changes.

## Non-goals (3.1)

- LLM-generated SEP sections.
- “Persona swap” style long-form narrative maintenance inside Broca.
- Semantic drift scoring or model-based diff between SEP versions.

## Rollout

1. Migration: `sep_config`, `sep_interaction_tier`, `sep_tier_id` (or junction table).
2. Static template + examples wired to formatter.
3. Renderer + hash + Letta sync.
4. CLI, then MCP.

## Open Questions

1. **Rank semantics:** Does lower `rank` mean higher privilege in the table, or only display order? (Must be one sentence in static intro.)
2. **Multi-platform user:** One user, multiple profiles — tier on `letta_user` vs per `platform_profile`?
3. **Initial seed data:** Empty tiers vs one default tier for all existing users?
