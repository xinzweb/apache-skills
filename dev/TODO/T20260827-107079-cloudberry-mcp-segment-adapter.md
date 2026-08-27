---
status: Open
scheduled: 2026-09-07
estimation: 4h
source: T20260827-203753 (MCP server survey) — follow-up feature seeded by its recommendation
related: T20260827-203753
description: Thin Cloudberry-aware MCP adapter for segment health, distribution keys, and skew
---

# T20260827-107079: Build a thin Cloudberry-aware MCP adapter for segment/distribution visibility

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
