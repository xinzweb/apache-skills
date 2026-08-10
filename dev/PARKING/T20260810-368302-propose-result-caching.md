---
status: Parked
estimation: 1w
priority: Low
source: conversation 2026-08-10 — user's 3-phase re-engagement plan, phase 3
description: Research query/results-caching prior art and propose a design for Apache Cloudberry, following the Apache Way
blocked-by: T20260810-177613
---

# T20260810-368302: Propose query results caching for Cloudberry

Phase 3 of 3, deliberately last and parked — the user wants a real track
record from phase 1-2 before spending community attention on a design
proposal. **When T20260810-177613 completes**: `git mv` this back to
`dev/TODO/`, set `status: Open`, drop this note.

## Confirmed as of 2026-08-10

No existing GitHub issue, GitHub Discussion, or `dev@` mailing-list thread
covers query/results caching for `apache/cloudberry` — checked via issue
search, Discussion search (not even in a Discussion title), a web search of
the mail archive, and the roadmap Discussion (#868) body. The closest
mentions found are unrelated: ORCA's internal plan cache, a PostGIS
memory-corruption bug, routine merge commits. This is a genuinely open
topic.

## Research targets (not started)

- [ ] PostgreSQL's `Memoize`/Result Cache executor node (PG14+) — most
      directly relevant since Cloudberry is PostgreSQL-based
- [ ] Apache Impala's Query Result Caching (TTL-based, coordinator-side)
- [ ] Other ASF-lineage OLAP engines — Doris, Kylin, Pinot, Drill — survey
      their result-cache approaches
- [ ] Any prior Greenplum-era caching discussion/design docs
- [ ] Existing Cloudberry infra that's cache-adjacent: `gp_matview_aux`
      (surfaced via issue #726 during earlier research)

## Deliverable

- [ ] 2-4 candidate designs tailored to Cloudberry's coordinator-segment
      architecture, with trade-offs (invalidation, staleness, memory
      pressure) — written up in `project/cloudberry/`
- [ ] Open as a GitHub Discussion (Proposal category) via `cloudberry-discuss`
      first, then cross-post `[DISCUSS]` to `dev@` via `cloudberry-mailing-list`
      once it has shape — **do not skip straight to a PR**, this is exactly
      the kind of design decision the Apache Way puts on-list first
