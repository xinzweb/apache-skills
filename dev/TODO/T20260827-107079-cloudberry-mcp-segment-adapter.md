---
status: Done
scheduled: 2026-08-24
estimation: 4h
source: T20260827-203753 (MCP server survey) — follow-up feature seeded by its recommendation
related: T20260827-203753
priority: Medium — routine backlog feature, no deadline pressure
description: Thin Cloudberry-aware MCP adapter for segment health, distribution keys, and skew
claimed_by:
---

# T20260827-107079: Build a thin Cloudberry-aware MCP adapter for segment/distribution visibility

## TLDR

- **Type**: feature
- **Problem**: no MCP server (generic or specialized) exposes Cloudberry's
  MPP-specific operational surface — segment health, distribution-key
  correctness, skew-aware plan interpretation.
- **Solution**: a small standalone Python MCP server, 4 tools, thin SQL
  wrappers around `gp_segment_configuration`/`gp_distribution_policy` and a
  `Motion`-line filter over `EXPLAIN` output — no live Cloudberry cluster
  available here, so verified by unit tests against a mocked DB cursor;
  live-cluster verification is an explicit unverified Done-criteria item.
- **Location decision** (maintainer, 2026-08-27): new directory in this
  repo, `mcp-servers/cloudberry-segment-adapter/` — `apache-skills` had no
  prior precedent for shipping runnable code (see `dev/guidelines.md`'s
  Repo Layout), so this is a structural addition, not an implementation
  detail.

## Problem

- `T20260827-203753`'s survey found that generic Postgres-family MCP servers
  (e.g. `mcp-alchemy`, `helloscoopa/mcp-postgres`) work unmodified against
  Cloudberry for baseline SQL/schema access, but **none** — generic or the
  specialized `crystaldba/postgres-mcp` — expose Cloudberry's MPP-specific
  operational surface: segment health, distribution-key correctness, or
  skew-aware plan interpretation.
- No existing MCP server reads `gp_segment_configuration` or
  `gp_distribution_policy`, and no server annotates `EXPLAIN` output with
  Motion/redistribution cost the way a Cloudberry operator would need.
- Done looks like: a small, standalone MCP server (not a fork of an existing
  codebase — see the survey's rejected-alternative rationale) exposing at
  least the four tools sketched in `T20260827-203753`'s `## Recommendation`:
  `list_segments`, `get_distribution_policy`, `check_data_skew`,
  `explain_segment_aware`.

## Context

- See `T20260827-203753` (`dev/TODO/T20260827-203753-mcp-server-survey.md`)
  for the full survey and the reasoning behind reuse-vs-build per tool.
- Pair with a generic wire-protocol MCP server (e.g. `mcp-alchemy`) for
  baseline schema/SQL access — this adapter only needs to cover the
  Cloudberry-specific gap, not duplicate baseline functionality.
- **Catalog columns** (verified against Cloudberry's own docs, 2026-08-27):
  - [`gp_segment_configuration`](https://cloudberry.apache.org/docs/sys-catalogs/sys-tables/gp-segment-configuration/):
    `dbid`, `content`, `role` (`p`/`m`), `preferred_role`, `mode`
    (`s`=synchronized, `n`=not-in-sync), `status` (`u`=up, `d`=down),
    `hostname`, `address`, `port`.
  - [`gp_distribution_policy`](https://cloudberry.apache.org/docs/sys-catalogs/sys-tables/gp-distribution-policy/):
    `localoid` (→ `pg_class.oid`), `policytype` (`p`=partitioned,
    `r`=replicated), `numsegments`, `distkey` (int2vector of
    `pg_attribute.attnum`), `distclass`. A `policytype='p'` row with an
    **empty** `distkey` is Cloudberry's `DISTRIBUTED RANDOMLY` — the docs
    don't spell this out explicitly; it follows from `distkey` having
    nothing to name.
  - `EXPLAIN` on Cloudberry/Greenplum-family databases includes plan node
    types not in vanilla Postgres — `Gather Motion`, `Redistribute Motion`,
    `Broadcast Motion` — the redistribution-cost signal a generic EXPLAIN
    tool would print but not call out.
- **MCP Python SDK** (verified via the SDK's own README, 2026-08-27):
  install `mcp[cli]`; server construction and tool registration is
  `from mcp.server import MCPServer` → `mcp = MCPServer("name")` →
  `@mcp.tool()` on a type-hinted function, docstring becomes the tool
  description. **Re-confirm this import path against the actually-installed
  package at implementation time** (`python -c "import mcp.server; print(mcp.server.__file__)"`)
  before writing `server.py` — SDK reference docs can drift from a pinned
  version faster than this design doc will.

## Solution (architecture)

- **Package**: `mcp-servers/cloudberry-segment-adapter/` (new top-level dir):

  ```text
  mcp-servers/cloudberry-segment-adapter/
    README.md
    pyproject.toml                              # deps: mcp[cli], psycopg2-binary
    src/cloudberry_segment_adapter/
      __init__.py
      db.py                                      # connection factory, reads DATABASE_URL
      queries.py                                 # SQL + row-shaping, takes a cursor — no MCP/network code
      server.py                                  # MCPServer instance, 4 @mcp.tool() wrappers over queries.py
    tests/
      test_queries.py                            # unit tests, mocked cursor — no live DB
  ```

  Splitting `queries.py` (pure SQL + parsing logic) from `server.py` (MCP
  wiring) is what makes the mocked-cursor unit-test strategy possible
  without a live cluster or an MCP client harness.
- **Connection**: `psycopg2` via a `DATABASE_URL` env var — the same
  convention `T20260827-203753`'s survey confirmed for `mcp-alchemy` /
  `sql-alchemy-mcp` / `helloscoopa/mcp-postgres`, so a user already running
  one of those alongside this adapter reuses the same connection string.
- **Tools** (SQL sketched from the verified catalog columns above; exact
  text finalized during implementation, not fixed by this design):
  - `list_segments()` — `SELECT dbid, content, role, preferred_role, mode,
    status, hostname, address, port FROM gp_segment_configuration ORDER BY
    content, role;` — flags `status='d'` (down) and `mode='n'` (not in
    sync) rows in the returned summary.
  - `get_distribution_policy(table_name)` — joins `gp_distribution_policy`
    → `pg_class` → `pg_attribute` to resolve `distkey` attnums to column
    names; labels the result `REPLICATED` (`policytype='r'`), `RANDOM`
    (`policytype='p'`, empty `distkey`), or `HASH(col1, col2, ...)`.
  - `check_data_skew(table_name)` — `SELECT gp_segment_id, count(*) FROM
    <table_name> GROUP BY gp_segment_id ORDER BY gp_segment_id;` — flags
    skew when a segment's row count deviates from the mean by more than a
    threshold (start at 10%, a tool-chosen heuristic, not an official
    Cloudberry number — call this out in the tool's own docstring).
  - `explain_segment_aware(query)` — runs `EXPLAIN <query>`, returns the
    full plan text plus a separate summary list of every line containing
    `Motion` (the redistribution-cost signal generic EXPLAIN tools print
    but don't surface).
- **Alternative rejected — fork `postgres-mcp` or `mcp-alchemy`**: both are
  general-purpose servers with their own release cadence and unrelated
  tool surface; forking either means carrying their upstream code just to
  bolt on 4 unrelated tools. A small standalone server with its own 4-tool
  surface is easier to reason about and doesn't couple this repo to
  another project's upstream changes. (Same rejected-alternative pattern as
  `T20260827-203753`'s own build-from-scratch-vs-reuse call, applied the
  other direction: reuse for baseline access, build fresh for the gap.)
- **Alternative rejected — expand scope to cover query execution timing /
  historical stats (a `pg_stat_statements`-style feature)**: out of scope —
  the survey's `## Findings` already identified that gap as belonging to
  `postgres-mcp`, and duplicating coordinator-only stats gives the same
  misleading picture the survey flagged as a reason to avoid that tool on
  Cloudberry. This adapter stays scoped to catalog/plan-shape visibility.
- **Implementation note — identifier quoting**: `check_data_skew`'s
  `table_name` is caller-supplied and lands in a `FROM {table}` clause,
  which `%s` value-binding can't parameterize (it's an identifier, not a
  value). Rather than pull in `psycopg2.sql.Identifier` (which needs a live
  connection to render, complicating the mocked-cursor unit tests), the
  implementation validates `table_name` against a strict
  `^[A-Za-z_][A-Za-z0-9_]*$` identifier regex and rejects anything else —
  see `queries.py::_quote_identifier` and
  `tests/test_queries.py::test_data_skew_rejects_unsafe_table_name`.
  `explain_segment_aware`'s `query` argument is intentionally NOT
  restricted this way — it's the argument being explained, so passing it
  through is the tool's whole purpose (same trust boundary as every
  surveyed server's `execute_sql`/`explain_query`, per `## Findings` in
  `T20260827-203753`).
- **Implementation note — skew heuristic caught by its own test**: the
  first skew-detection draft compared every segment's row count to the
  *whole-set* mean and flagged any large deviation in either direction;
  `test_data_skew_flags_deviation` (mean pulled up by one outlier) caught
  that it flagged the two *normal* segments too. Fixed to flag only
  segments *above* mean × (1 + threshold) — matching Cloudberry's own
  framing that response time is bounded by the busiest segment, not the
  idlest one.

## Test plan

- [x] `tests/test_queries.py::test_list_segments_flags_down_and_unsynced` —
      mocked cursor returns rows with `status='d'`/`mode='n'`; assert the
      parsed result flags them
- [x] `tests/test_queries.py::test_distribution_policy_labels_replicated_random_hash` —
      3 mocked-row cases (`policytype='r'`; `policytype='p'`+empty
      `distkey`; `policytype='p'`+non-empty `distkey`); assert each label
      (+ a 4th case added during implementation:
      `test_distribution_policy_raises_for_unknown_table`)
- [x] `tests/test_queries.py::test_data_skew_flags_deviation` — mocked
      per-segment counts with one segment >10% off the mean; assert flagged
      (+ `test_data_skew_rejects_unsafe_table_name`, added during
      implementation once identifier-quoting became a real safety concern
      — see `## Solution`'s implementation-note below)
- [x] `tests/test_queries.py::test_explain_segment_aware_extracts_motion_lines` —
      a multi-line `EXPLAIN` text fixture containing `Gather Motion` /
      `Redistribute Motion` lines; assert they're extracted into the
      summary
- [x] Dropped `test_sql_text_for_each_tool` as a separate test — each
      existing test already asserts the exact SQL/args `cursor.execute`
      was called with (see e.g. `cursor.execute.assert_called_once_with(...)`
      in every case above), so a dedicated SQL-text test would just
      duplicate those assertions
- [ ] **Post-merge, external, unverified here**: running against a live
      Cloudberry cluster — no cluster is reachable from this environment;
      note this explicitly rather than claiming a false pass

## Done criteria

- [x] `src/cloudberry_segment_adapter/queries.py` implements all 4 tool
      functions — mapped to `tests/test_queries.py` (8/8 passing,
      `python3 -m pytest tests/ -v`)
- [x] `src/cloudberry_segment_adapter/server.py` registers all 4 as
      `@mcp.tool()` — verified via `mcp.list_tools()` smoke test (not just
      import success) during implementation, all 4 names + descriptions
      present
- [x] `pytest tests/` passes locally — 8 passed, 0 failed
- [x] `README.md` documents `DATABASE_URL` setup and the pairing note
      (use alongside a generic MCP server for baseline access)
- [x] `dev/guidelines.md`'s Repo Layout gains a one-line `mcp-servers/`
      entry — landed in a separate small PR after this one merged, in the
      spirit of the "don't update CLAUDE.md on feature branches" note
      (correcting this item's own earlier mis-citation: the actual Repo
      Layout list lives in `dev/guidelines.md`, not `CLAUDE.md`, which has
      no such section)

## Root cause

- N/A — this is a greenfield feature (`## TLDR` Type: feature) tracked in
  `dev/TODO/T20260827-107079-cloudberry-mcp-segment-adapter.md`, not a bug
  fix; there is no prior broken behavior to trace. The "why build vs. reuse"
  reasoning that a Root-cause section would normally carry is in
  `## Solution`'s rejected-alternatives bullets instead.

## Repo file references

| File | Lines | Purpose |
| --- | --- | --- |
| `mcp-servers/cloudberry-segment-adapter/pyproject.toml` | new | package metadata + deps (`mcp[cli]`, `psycopg2-binary`) |
| `mcp-servers/cloudberry-segment-adapter/src/cloudberry_segment_adapter/db.py` | new | `DATABASE_URL` → `psycopg2` connection factory |
| `mcp-servers/cloudberry-segment-adapter/src/cloudberry_segment_adapter/queries.py` | new | SQL + row-shaping for all 4 tools; cursor-only, no MCP/network code |
| `mcp-servers/cloudberry-segment-adapter/src/cloudberry_segment_adapter/server.py` | new | `MCPServer` instance + 4 `@mcp.tool()` wrappers |
| `mcp-servers/cloudberry-segment-adapter/tests/test_queries.py` | new | unit tests against a mocked cursor (5 cases, see `## Test plan`) |
| `mcp-servers/cloudberry-segment-adapter/README.md` | new | setup + pairing-with-a-generic-server note |
| `dev/guidelines.md` | Repo Layout section | +1 line for `mcp-servers/` — separate follow-up PR, see `## Done criteria` |

## Closed (2026-08-27)

- Shipped in the design PR (#14, architecture) + this implementation PR
  (`mcp-servers/cloudberry-segment-adapter/`, 8 passing unit tests).
- All Done criteria met except one, left honestly unchecked: live-cluster
  verification — no Apache Cloudberry cluster was reachable from this
  environment, so only the mocked-cursor unit tests ran. The
  `dev/guidelines.md` Repo Layout update landed separately, see below.
- The MCP Python SDK API sketched in the design (`from mcp.server import
  MCPServer`, `@mcp.tool()`) was independently confirmed correct by
  installing `mcp==2.1.1` and inspecting it directly — not just trusting
  the design doc's earlier docs-fetch.
- One real bug caught by its own test before merge: the first
  `check_data_skew` draft flagged both normal segments in a 3-segment
  skewed set (whole-set mean shifted by the one outlier) — see
  `## Solution`'s implementation note.
- No follow-up task filed — this closes the loop `T20260827-203753`
  opened; nothing further identified as in-scope.
- `doc-impact.sh` flagged 9 `.claude/skills/cloudberry-*/SKILL.md` files +
  `dev/guidelines.md` as referencing "README.md" — reviewed: false
  positive, a generic-filename substring match against unrelated Apache
  Cloudberry contribution-process docs, none of which reference this
  package's `README.md`. No change needed.
- Quality probe: 9 files touched, design score 94/100 carried through;
  static scanners (shellcheck/jscpd/gitleaks/kcov) unavailable in this
  environment, recorded `null` rather than skipped silently — see
  `dev/quality/metrics.jsonl`.

## Skills invoked

- TDD (`superpowers:test-driven-development`): skill not present in this
  environment; followed the practice manually — wrote
  `tests/test_queries.py` against a not-yet-existing `queries.py`,
  confirmed the resulting `ImportError` (red), then implemented until
  green (8/8), catching the skew-heuristic bug in the process
- Verification (`superpowers:verification-before-completion`): skill not
  present; self-verified instead — ran the real `mcp` SDK install to
  confirm the design's API sketch against the actually-installed package
  (not just docs), smoke-tested `server.py`'s tool registration via
  `mcp.list_tools()`, and cleaned build artifacts (`.pytest_cache`,
  `__pycache__`, `*.egg-info`) out of the commit, adding a `.gitignore` so
  they don't recur
- Systematic debugging (`superpowers:systematic-debugging`): no — the one
  test failure was diagnosed and fixed in one pass, not a stuck loop
- Receiving code review (`superpowers:receiving-code-review`): no — no
  Copilot/reviewer configured on this repo
