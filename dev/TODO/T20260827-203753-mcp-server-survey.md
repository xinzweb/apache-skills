---
status: Design
estimation: 1d
source: this conversation, 2026-08-27
claimed_by: Shines-Laptop.local:/Users/xlj/workspace/xinzweb/apache-skills
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

- [ ] Survey ≥4 existing Postgres MCP servers (2 generic, 2+ specialized)
      against their own docs/source
- [ ] Record each server's extension/architecture dependencies relevant to
      Cloudberry compatibility
- [ ] Cross-reference against Cloudberry's segment-aware catalogs/behavior
      (`gp_segment_configuration`, `gp_distribution_policy`, `EXPLAIN`)
- [ ] Write the reuse/fork/build recommendation with a tool-surface sketch
      for any confirmed gap
- [ ] File a follow-up `feature` task if fork/build is warranted

## Done criteria

- [ ] Test plan item 1+2 done: `## Findings` section lists each surveyed
      server with its Cloudberry-compatibility verdict and dependencies
- [ ] Test plan item 3+4 done: `## Recommendation` states reuse vs. fork vs.
      build, with the specific incompatibilities that drove the call
- [ ] Test plan item 4 done: tool-surface sketch present if fork/build is
      recommended
- [ ] Test plan item 5 done: follow-up task filed (or explicitly declared
      unnecessary)

## Closed

## Skills invoked
