---
status: Review
scheduled: 2026-08-10
estimation: 1w
priority: Medium
source: conversation 2026-08-10 (filed retroactively — work predates this task file)
description: Foundation Cloudberry skills, career-path extension, and repo layout/privacy guidelines
related: PR #1
---

# T20260810-394882: Cloudberry skills foundation + repo conventions

**Filed retroactively** — this work was done and PR'd (github.com/xinzweb/apache-skills#1)
before it had a tracked task file. Filing now so the record is complete;
move to `dev/JOURNAL/` once #1 merges, same as any other task.

## Scope (already done, in PR #1)

- `extract-url-text` skill — dependency-free URL text extractor
- `cloudberry-career-path` extended with the foundation-wide ASF
  Member/Officer/Board track
- `project/cloudberry/` — career plan + self-assessment, moved out of
  `docs/` per the new repo layout convention
- `dev/guidelines.md` — Repo Layout + Content & Privacy Guidelines sections

## Follow-up

- On merge: `git mv` this file to `dev/JOURNAL/2026-08-10-T20260810-394882-cloudberry-skills-foundation.md`
- Going forward: every non-trivial change in this repo gets a task file
  *before* the PR, not after — this file is the exception, not the pattern.
