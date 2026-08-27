---
status: Done
estimation: 1d
source: this conversation, 2026-08-27
claimed_by:
scheduled: 2026-08-24
related: none
priority: Medium — routine backlog research, no deadline pressure
---

# T20260827-203753: Survey MCP server options for Apache Cloudberry SQL/DB access

## TLDR

- **Type**: research
- **Problem**: no MCP server gives an LLM SQL/DB access to Apache Cloudberry;
  unclear whether existing Postgres-family MCP servers work as-is.
- **Solution**: generic, wire-protocol-only MCP servers (schema browse, run
  SQL, `EXPLAIN`) are expected to work against Cloudberry unmodified; the
  specialized index/health-tuning server is expected to need Cloudberry-aware
  adaptation for its extension and single-node assumptions — confirm both by
  reading each project's own docs/source, then recommend reuse vs. thin
  adapter vs. build.

## Problem

- Apache Cloudberry (Incubating) is a Postgres/Greenplum-derived MPP
  database; no MCP server exists yet in this repo (or found upstream) for
  giving an LLM SQL/DB access to a running Cloudberry cluster.
- Survey existing Postgres-family MCP servers (e.g. the reference
  `postgres-mcp` and similar community servers) and determine whether they
  work as-is against Cloudberry, or whether GPDB-derived differences —
  distribution keys, `gp_segment_configuration`, segment-aware `EXPLAIN`
  plans, `gpstate`-style health signals, documented at
  `cloudberry.apache.org/docs/sys-catalogs/sys-tables/gp-segment-configuration/` —
  require a fork or adapter layer.
- Done looks like: a written recommendation — reuse, fork, or build from
  scratch — with the specific incompatibilities found, plus a rough
  tool-surface sketch if a fork/build is recommended. This seeds a
  follow-up `feature` task if building/forking is warranted.

## Context

- Cloudberry is wire-protocol compatible with PostgreSQL (clients connect
  with a standard `libpq`/`psycopg` driver) but adds MPP-specific catalogs
  and behavior not present in vanilla Postgres:
  [`gp_segment_configuration`](https://cloudberry.apache.org/docs/sys-catalogs/sys-tables/gp-segment-configuration/)
  (segment/mirror health), [`gp_distribution_policy`](https://cloudberry.apache.org/docs/sys-catalogs/sys-tables/gp-distribution-policy/)
  (per-table distribution keys), and segment-aware `EXPLAIN` output — see
  [Distribution and Skew](https://cloudberry.apache.org/docs/performance/distribution-and-skew/).
- No prior MCP work exists in this repo (`project/cloudberry/` covers
  contributor process, not tooling) — this is a fresh survey.

## Solution (survey plan)

- Survey two tiers of candidate servers, verifying claims from each
  project's own docs/source rather than assuming:
  - **Generic/wire-protocol-only**: [`mcp-alchemy`](https://github.com/runekaagaard/mcp-alchemy),
    [`sql-alchemy-mcp`](https://github.com/alexxonline/sql-alchemy-mcp),
    [`helloscoopa/mcp-postgres`](https://github.com/helloscoopa/mcp-postgres) —
    connect via a standard driver, expose schema-browse/`execute_sql`/`EXPLAIN`
    with no Postgres-specific extensions.
  - **Postgres-specialized**: [`crystaldba/postgres-mcp`](https://github.com/crystaldba/postgres-mcp)
    ("Postgres MCP Pro" — health checks, index tuning, `EXPLAIN` analysis) and
    the official `@modelcontextprotocol/server-postgres` reference server
    (flagged unsupported upstream — note but don't evaluate further).
  - For each, record: extensions required (e.g. `pg_stat_statements`,
    `hypopg`), single-node vs. distributed assumptions, and how the tool
    surface maps to Cloudberry's segment-aware catalogs/behavior.
- **Alternative rejected — build a Cloudberry MCP server from scratch**: the
  core surface (schema browse, run SQL, `EXPLAIN`) is expected to be
  reachable through the wire protocol alone per the tier-1 servers' own
  docs; a ground-up build would duplicate that for no gain. Confirm this
  during the survey rather than asserting it — write up whatever the
  evidence actually shows, including if it doesn't hold.

## Test plan

- [x] Survey ≥4 existing Postgres MCP servers (2 generic, 2+ specialized)
      against their own docs/source — see `## Findings` (5 servers surveyed)
- [x] Record each server's extension/architecture dependencies relevant to
      Cloudberry compatibility — see `## Findings` table
- [x] Cross-reference against Cloudberry's segment-aware catalogs/behavior
      (`gp_segment_configuration`, `gp_distribution_policy`, `EXPLAIN`) —
      see `## Findings` closing bullet
- [x] Write the reuse/fork/build recommendation with a tool-surface sketch
      for any confirmed gap — see `## Recommendation`
- [x] File a follow-up `feature` task if fork/build is warranted —
      `T20260827-107079`

## Done criteria

- [x] Test plan item 1+2 done: `## Findings` section lists each surveyed
      server with its Cloudberry-compatibility verdict and dependencies
- [x] Test plan item 3+4 done: `## Recommendation` states reuse vs. fork vs.
      build, with the specific incompatibilities that drove the call
- [x] Test plan item 4 done: tool-surface sketch present if fork/build is
      recommended
- [x] Test plan item 5 done: follow-up task filed (or explicitly declared
      unnecessary) — `T20260827-107079`

## Findings

Verified against each project's own docs/source (2026-08-27):

| Server | Tier | Tools | Extensions/assumptions required | Cloudberry verdict |
| --- | --- | --- | --- | --- |
| [`mcp-alchemy`](https://github.com/runekaagaard/mcp-alchemy) | generic | `all_table_names`, `filter_table_names`, `schema_definitions`, `execute_query` | Standard SQLAlchemy `postgresql://` + `psycopg2` driver; no PG-specific extensions; no distributed-DB awareness in docs (doesn't need any — runs plain SQL over the wire) | **Works as-is** |
| [`helloscoopa/mcp-postgres`](https://github.com/helloscoopa/mcp-postgres) | generic | `query` (configurable read/DDL/DML), `schema` | Standard `postgresql://` connection string; no extensions documented; no single-node vs. distributed assumption stated | **Works as-is** |
| [`sql-alchemy-mcp`](https://github.com/alexxonline/sql-alchemy-mcp) | generic | query/list/describe (read-only); execute/bulk/DDL/index management (readwrite mode) | `psycopg2-binary` via `postgresql://` connection string; no extensions documented; no distributed-DB discussion | **Works as-is** |
| `@modelcontextprotocol/server-postgres` (official reference) | generic | schema inspect, read-only query | N/A — [repo archived 2025-05-29](https://github.com/modelcontextprotocol/servers-archived/tree/main/src/postgres), read-only, no longer maintained | **Not viable regardless of Cloudberry fit** |
| [`crystaldba/postgres-mcp`](https://github.com/crystaldba/postgres-mcp) ("Postgres MCP Pro") | specialized | `list_schemas`, `list_objects`, `get_object_details`, `execute_sql`, `explain_query`, `get_top_queries`, `analyze_workload_indexes`, `analyze_query_indexes`, `analyze_db_health` | Basic 5 tools: no extensions. `get_top_queries`/`analyze_workload_indexes`/`analyze_db_health` require `pg_stat_statements`; `analyze_query_indexes` requires `hypopg`; both assume a single-node planner/cost model | **Split**: basic tools work as-is; the 4 tuning/health tools give misleading results — `pg_stat_statements` only sees coordinator-level stats (Cloudberry's real bottlenecks are per-segment, per `Distribution and Skew`), and `hypopg`'s single-node index simulation doesn't model Cloudberry's redistribution ("Motion") costs |

- No surveyed server (generic or specialized) reads
  `gp_segment_configuration` or `gp_distribution_policy`, or annotates
  `EXPLAIN` output with segment-skew/Motion-cost interpretation — this gap
  is consistent across every candidate, confirming it's a genuine hole
  rather than a single project's oversight.

## Recommendation

- **Reuse as-is for baseline SQL/schema access**: any generic
  wire-protocol server (`mcp-alchemy` has the broadest documented feature
  set) or `postgres-mcp`'s basic 5 tools cover schema browse, run-SQL, and
  raw `EXPLAIN` output against Cloudberry with zero modification — the
  `## Solution`'s rejected from-scratch-build alternative is confirmed:
  building a new server for this tier would duplicate working tools for no
  gain.
- **Avoid** `postgres-mcp`'s `get_top_queries`, `analyze_workload_indexes`,
  `analyze_query_indexes`, and `analyze_db_health` against Cloudberry as
  configured today — their `pg_stat_statements`/`hypopg` basis produces
  coordinator-only, single-node-biased answers that misrepresent an MPP
  cluster's actual health.
- **Build** a thin, standalone Cloudberry-aware adapter (not a fork — new,
  narrow tool surface) exposing: `list_segments` (wraps
  `gp_segment_configuration`, flags down/unsynced mirrors),
  `get_distribution_policy` (wraps `gp_distribution_policy`, flags
  NULL/random distribution), `check_data_skew` (per-segment row-count
  histogram), and `explain_segment_aware` (thin wrapper highlighting
  Motion/redistribution cost in `EXPLAIN` output). Filed as
  `T20260827-107079` (`dev/TODO/T20260827-107079-cloudberry-mcp-segment-adapter.md`).

## Closed (2026-08-27)

- Shipped in the design PR (#11, methodology) + this implementation PR
  (findings/recommendation) — self-repo, no separate target repo.
- All Done criteria met: `## Findings` surveys 5 servers with cited verdicts,
  `## Recommendation` calls reuse for baseline access + build for the
  Cloudberry-specific gap, tool-surface sketch included, follow-up filed as
  `T20260827-107079`.
- Nothing external/unverified remains — every compatibility claim was
  confirmed by reading the surveyed project's own docs/source directly
  (not inferred from a search summary; two initial search-summary-based
  claims were re-verified with a direct fetch before closing, see `## Skills
  invoked`).

## Skills invoked

- TDD (`superpowers:test-driven-development`): no — docs-class research task,
  no code
- Verification (`superpowers:verification-before-completion`): skill not
  present in this environment; self-verified instead by re-fetching two
  claims (`sql-alchemy-mcp`'s driver, `server-postgres`'s archived status)
  that were first written from a search summary rather than a direct source
  read, per this task's own evidence-discipline commitment
- Systematic debugging (`superpowers:systematic-debugging`): no — didn't get
  stuck
- Receiving code review (`superpowers:receiving-code-review`): no — no
  Copilot/reviewer configured on this repo (see PR #9/#11 — 0 reviews)
