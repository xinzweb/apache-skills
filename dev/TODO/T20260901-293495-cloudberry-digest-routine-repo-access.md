---
status: Open
estimation: 1h
source: this conversation, 2026-09-01 — first real production fire of the T20260829-423782 daily routine
related: T20260829-423782
description: The cloudberry-activity-digest cloud routine can't reach apache/cloudberry — GitHub access is scoped to xinzweb/apache-skills only
---

# T20260901-293495: Fix the cloudberry-activity-digest routine's apache/cloudberry access

## Problem

- **Type**: bug
- The daily cloud routine (`trig_01Xqa2sqpNaAKQ7MuFj46FNj`,
  "cloudberry-activity-digest-daily") set up in T20260829-423782 ran for
  the first time in production on 2026-09-01T13:39:36Z
  (session `cse_01Qx8iigiMK32SeMJvBD36eE`) and **could not query
  `apache/cloudberry` at all**:
  - The sandbox has no `gh` CLI — the session fell back to a
    `mcp__github__*` MCP connector instead of the `gh api` commands
    the skill documents.
  - That connector is scoped only to the routine's own source repo:
    `mcp__github__list_pull_requests`/`list_issues` against
    `owner=apache, repo=cloudberry` both returned `Access denied:
    repository "apache/cloudberry" is not configured for this session.
    Allowed repositories: xinzweb/apache-skills`.
  - The narrower `search_issues`/`search_pull_requests` calls that did
    run returned stale/irrelevant results (e.g. `mentions:xinzweb` — 0,
    consistent with the interactive-session finding in T20260829-423782,
    but also no genuinely fresh data since the write-scoped list calls
    were denied).
- **It failed safely** — this is not "make it not crash", it's "make it
  actually work": the routine correctly recognized it couldn't verify
  activity, emailed an honest explanation instead of a false "no
  activity" digest (per the skill's own silence-must-never-be-ambiguous
  rule), and pushed a mobile notification. See message id `1a05d346d6b823d3`
  and `RemoteTrigger get_run_log` on the session above for the full
  transcript.
- Done looks like: the routine's next real fire successfully queries
  `apache/cloudberry` (via either a `gh` CLI + token available in the
  CCR sandbox, or a GitHub MCP connector/source explicitly scoped to
  `apache/cloudberry`) and sends a digest reflecting real query results
  — verified by triggering a `RemoteTrigger run` and reading its
  `get_run_log`, not just by inspecting the routine config.
