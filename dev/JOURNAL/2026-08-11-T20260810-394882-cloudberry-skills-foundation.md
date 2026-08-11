---
status: Done
scheduled: 2026-08-10
estimation: 1w
priority: Medium
source: conversation 2026-08-10 (filed retroactively — work predates this task file)
description: Foundation Cloudberry skills, career-path extension, and repo layout/privacy guidelines
related: "[PR #1](https://github.com/xinzweb/apache-skills/pull/1) (merged 2026-08-11, 5 independent review rounds)"
---

# T20260810-394882: Cloudberry skills foundation + repo conventions

**Filed retroactively** — this work was done and opened as
[PR #1](https://github.com/xinzweb/apache-skills/pull/1) before it had a
tracked task file. Merged 2026-08-11 after 5 rounds of independent review
(fixed: SSRF via file:///ftp:// redirect, uncaught exceptions crashing
with raw tracebacks, a misapplied RFC 9309 citation, unrecognized
Content-Encoding corruption, a stale doc cross-reference, and a
robots.txt message-accuracy issue — see the PR's review comments for the
full history).

## Scope

- `extract-url-text` skill — dependency-free URL text extractor
- `cloudberry-career-path` extended with the foundation-wide ASF
  Member/Officer/Board track
- `project/cloudberry/` — career plan + self-assessment, moved out of
  `docs/` per the new repo layout convention
- `dev/guidelines.md` — Repo Layout + Content & Privacy Guidelines sections

## Process note

Going forward: every non-trivial change in this repo gets a task file
*before* the PR, not after — this file is the exception, not the pattern.
