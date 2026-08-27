---
status: Open
estimation: 1d
source: this conversation, 2026-08-27
---

# T20260827-203753: Survey MCP server options for Apache Cloudberry SQL/DB access

## Problem

- **Type**: research
- Apache Cloudberry (Incubating) is a Postgres/Greenplum-derived MPP
  database; no MCP server exists yet in this repo (or found upstream) for
  giving an LLM SQL/DB access to a running Cloudberry cluster.
- Survey existing Postgres-family MCP servers (e.g. the reference
  `postgres-mcp` and similar community servers) and determine whether they
  work as-is against Cloudberry, or whether GPDB-derived differences
  (distribution keys, `gp_segment_configuration`, segment-aware `EXPLAIN`
  plans, `gpstate`-style health signals) require a fork or adapter layer.
- Done looks like: a written recommendation — reuse, fork, or build from
  scratch — with the specific incompatibilities found, plus a rough
  tool-surface sketch if a fork/build is recommended. This seeds a
  follow-up `feature` task if building/forking is warranted.
