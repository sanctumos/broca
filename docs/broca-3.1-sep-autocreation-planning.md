# Broca 3.1 Planning: AI-Created SEP (Dynamic + Auto-Update)

Date: 2026-03-27  
Branch target: `broca-3.1`  
Status: Draft plan from live Athena block analysis

## Objective

Design a Broca capability to automatically create and maintain a Sanctum Engagement Protocol (SEP) memory block per agent, instead of relying on handcrafted manual edits.

The SEP should:
- be AI-generated from observed interaction patterns and trusted source context,
- attach/update in Letta core memory under a stable label,
- evolve safely over time with bounded, auditable changes.

## Baseline Findings (Athena, live)

From Athena's attached core-memory blocks:
- SEP block label: `protocols_sep`
- Current state: handcrafted long-form markdown (~4241 chars)
- Current sections include:
  - middleware-preface format notes
  - general framework
  - access/interaction rules
  - custom engagement approaches
  - final notes
  - Otto-specific section

Related companion blocks also present (`persona`, `human-primary`, `memory_rules`, etc.), which provide strong source signals for SEP generation.

## Product Requirements

1. **Auto-create**
   - If SEP block is missing, generate initial SEP and create/update it under configured label.

2. **Auto-update**
   - Periodically re-evaluate SEP based on recent interaction summaries + profile metadata.
   - Update only when meaningful deltas are detected.

3. **Safety**
   - Preserve identity-critical constraints.
   - Prevent destructive drift from noisy recent interactions.
   - Keep hard limits on size and change magnitude.

4. **Auditability**
   - Store generation metadata (version, source hashes, timestamp, model, diff summary).
   - Keep before/after snapshots and change logs.

## Architecture (3.1)

### A) SEP Manager (new core service)

Proposed module:
- `runtime/core/sep_manager.py`

Responsibilities:
- fetch current SEP block by label,
- collect source inputs,
- produce candidate SEP,
- run validation + policy checks,
- apply patch/update to Letta block,
- emit audit record.

### B) Source Inputs (ranked trust)

1. `persona` block (highest weight)  
2. `memory_rules` block  
3. `human-primary` block  
4. curated relationship metadata (known contacts + roles)  
5. recent interaction summaries (bounded window)  
6. explicit operator overrides (manual lock fields)

### C) SEP Schema (structured first, render second)

Use an internal JSON schema as canonical representation, then render markdown for Letta block.

Proposed schema fragments:
- `identity_constraints`
- `engagement_framework`
- `access_tiers`
- `relationship_overrides`
- `routing_notes` (middleware caveats)
- `agent_specific_sections` (example: Otto section)
- `meta` (version, generated_at, source_fingerprint)

Rationale:
- deterministic diffing,
- easier policy validation,
- stable markdown generation.

### D) Update Strategy

Trigger options (configurable):
- interval-based cron loop (default),
- on explicit admin tool call,
- on material profile change event.

Default algorithm:
1. read current SEP markdown and parse to internal schema (best-effort),
2. build candidate schema from sources,
3. semantic diff current vs candidate,
4. apply only if diff score > threshold and all policy checks pass,
5. patch Letta block with regenerated markdown.

## Policy Guardrails

1. **Protected fields**
   - hard-locked identity invariants (from persona/memory rules)
   - non-removable safety clauses configured by operator

2. **Bounded drift**
   - max changed percentage per update
   - cooldown between updates
   - no full rewrites unless forced

3. **Input filtering**
   - ignore low-confidence or adversarial interaction snippets
   - require repeated evidence before tier/policy movement

4. **Human override**
   - optional freeze mode for SEP updates
   - manual pinned lines/sections

## Config Surface

Proposed env/settings keys:
- `SEP_AUTOCREATE_ENABLED=true|false`
- `SEP_BLOCK_LABEL=protocols_sep`
- `SEP_UPDATE_MODE=off|manual|interval|event`
- `SEP_UPDATE_INTERVAL_SECONDS=21600` (6h default)
- `SEP_MAX_BLOCK_CHARS=12000`
- `SEP_MAX_CHANGE_RATIO=0.25`
- `SEP_COOLDOWN_SECONDS=3600`
- `SEP_DRY_RUN=true|false`
- `SEP_REQUIRE_APPROVAL=true|false` (optional gate)

## Letta API Operations

Required reads/writes:
- GET `/v1/agents/{agent_id}/core-memory/blocks/{label}`
- PATCH `/v1/agents/{agent_id}/core-memory/blocks/{label}`
- fallback create path when label missing (depends on available block-create endpoint in deployed Letta version)

Implementation note:
- if no direct create-by-label endpoint is available, create block then attach/label via current Letta APIs used in Broca.

## Rollout Plan

1. **Phase 1: Read-only analyzer**
   - ingest sources + generate candidate SEP + diff report only
   - no writes

2. **Phase 2: Dry-run writer**
   - full write path behind `SEP_DRY_RUN=true`, emit payload preview

3. **Phase 3: Controlled write**
   - enable writes for Athena only, with cooldown and change cap

4. **Phase 4: Generalize**
   - extend to additional agents with agent-specific templates

## Testing Plan

### Unit tests
- parse/render SEP schema roundtrip
- protected field preservation
- drift cap enforcement
- update trigger/cooldown logic

### Integration tests
- mock Letta block GET/PATCH
- missing block auto-create path
- diff gating (no-op update when below threshold)

### Scenario tests
- add new trusted contact -> tier change appears in candidate SEP
- adversarial conversation text -> ignored by filters

## Open Decisions

1. **Model for generation**
   - deterministic local templating + rules vs LLM synthesis pass

2. **Approval mode**
   - always auto-apply vs optional review queue per update

3. **Storage for SEP history**
   - database table vs file snapshots under agent runtime path

4. **Cross-agent defaults**
   - shared baseline template vs fully agent-specific profiles

## Initial Recommendation

For 3.1, ship a conservative system:
- structured SEP schema + deterministic renderer,
- interval updater with strict drift/cooldown caps,
- read-only + dry-run first,
- then controlled auto-apply for Athena.

This gets dynamic SEP maintenance without risking identity regression.

