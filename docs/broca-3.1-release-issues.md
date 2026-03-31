# Broca 3.1 Planning: GitHub Issues Scope

Date: 2026-03-28  
Branch target: `broca-3.1`  
Related: [outbound MCP](broca-3.1-outbound-mcp-planning.md), [SEP](broca-3.1-sep-autocreation-planning.md), [SMCP CLI plugins](broca-3.1-smcp-cli-plugins-planning.md), [streaming timeout continuation](broca-3.1-streaming-timeout-continuation-planning.md)

## Open issue inventory (sanctumos/broca)

As of triage: **72 open issues**, grouped as:

| Bucket | Approx. count | Notes |
|--------|---------------|--------|
| Product / bugs / features | 9 | #15, #44, #46–#54 |
| Audit (one finding per issue) | ~53 | #59–#120 |
| Informational | 1 | #121 positive finding |

## 3.1 release board (agreed scope)

### Implement in 3.1

| Issue | Title / intent |
|-------|----------------|
| [#54](https://github.com/sanctumos/broca/issues/54) | Treat invalid image URLs as non-retryable — avoids retry storms and circuit-breaker trips on tmpfiles/404-style failures. |
| [#46](https://github.com/sanctumos/broca/issues/46) | Telegram: split outbound messages over the 4 096 character limit. |
| [#50](https://github.com/sanctumos/broca/issues/50) | Make remaining timeout values environment-configurable (queue already has `MESSAGE_PROCESS_TIMEOUT`; audit codebase for others, wire to env / typed config, document). |

### Verify then fix or close

| Issue | Action |
|-------|--------|
| [#47](https://github.com/sanctumos/broca/issues/47) | Confirm Telegram markdown parity with `common.telegram_markdown`; fix if still wrong, else close with note. |
| [#48](https://github.com/sanctumos/broca/issues/48), [#49](https://github.com/sanctumos/broca/issues/49) | Multimodal/images largely shipped in Broca 3; verify against issue checklists, close or open small follow-ups for any gap. |

### Documentation slice (optional but aligned with other 3.1 docs)

| Issue | Action |
|-------|--------|
| [#15](https://github.com/sanctumos/broca/issues/15) | Do **not** block 3.1 on full OpenAPI/ADRs. Optional thin slice: fix CLI reference drift (`btool` vs actual `qtool`/`utool`/etc.) per [SMCP CLI plan](broca-3.1-smcp-cli-plugins-planning.md). |

### Explicitly out of scope for 3.1

| Issue | Reason |
|-------|--------|
| [#52](https://github.com/sanctumos/broca/issues/52) | Progress updates / long-running job UX — larger feature; target 3.2+ unless scope is deliberately cut. |
| [#44](https://github.com/sanctumos/broca/issues/44) | Metrics and monitoring — future bucket per issue text. |

## Audit issues #59–#120 — rollup, not per-issue release work

Do **not** close 3.1 against 53 separate audit tickets one-by-one. Use **one or two rollup PRs** and batch-close with references.

| Priority | Examples | Rollup work |
|----------|----------|-------------|
| Quick hygiene | [#118](https://github.com/sanctumos/broca/issues/118), [#119](https://github.com/sanctumos/broca/issues/119) (pin deps), [#120](https://github.com/sanctumos/broca/issues/120) (`SECURITY.md`) | Single PR; close linked issues. |
| Triage | [#59](https://github.com/sanctumos/broca/issues/59) (`.env.example` credential-like) | Confirm placeholders only; adjust copy if needed. |
| Live code review | [#113](https://github.com/sanctumos/broca/issues/113)–[#117](https://github.com/sanctumos/broca/issues/117) (querystring / URL construction in `letta_client`, `telegram_bot`) | One pass: no secrets in query strings; document intentional API URL patterns. |
| Test / disabled-plugin noise | [#60](https://github.com/sanctumos/broca/issues/60)–[#112](https://github.com/sanctumos/broca/issues/112), [#104](https://github.com/sanctumos/broca/issues/104)–[#110](https://github.com/sanctumos/broca/issues/110) | One PR: `example.com`, shared constants, or documented scanner exceptions; batch-close. |

### [#121](https://github.com/sanctumos/broca/issues/121)

Positive audit summary (“no obvious credential-file artifacts”). Close when rollup narrative is done.

## Milestone suggestion (GitHub)

Create milestone **Broca 3.1** and attach:

- **Must:** #54, #46, #50  
- **Should:** #47, #48, #49 verification  
- **Chore:** audit rollup (reference one meta-issue or the PR that closes the batch)

## Checklist before shipping 3.1

- [ ] #54 implemented and tested  
- [ ] #46 implemented and tested  
- [ ] #50 timeout audit complete + docs updated  
- [ ] #47 / #48 / #49 closed or spun to follow-ups  
- [ ] Audit rollup PR merged; batch-close or comment #59–#121 as appropriate  
- [ ] (Optional) CLI reference / #15 thin slice  
- [ ] [Streaming timeout / Letta continuation](broca-3.1-streaming-timeout-continuation-planning.md): spike tests → Plan B or Plan A implemented  
