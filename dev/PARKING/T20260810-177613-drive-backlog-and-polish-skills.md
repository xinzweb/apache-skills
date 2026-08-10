---
status: Parked
estimation: 2w
priority: Medium
source: conversation 2026-08-10 — user's 3-phase re-engagement plan, phase 2
description: Close ~10 apache/cloudberry backlog items and revise the cloudberry-* skills based on real usage friction
blocked-by: T20260810-723411
blocks: T20260810-368302
---

# T20260810-177613: Drive the backlog down by 10, polish apache-skills

Phase 2 of 3. Parked — deliberately gated on T20260810-723411, this task
acts on real friction found there rather than guessing at it in parallel.
**When T20260810-723411 completes**: `git mv` this back to `dev/TODO/`,
set `status: Open`, drop this note.

## Backlog work

- [ ] ~10 real items closed or meaningfully advanced on `apache/cloudberry`
      — a mix of bug fixes, PR reviews, and issue triage counts; doesn't
      have to be 10 merged PRs
- [ ] Keep working from `project/cloudberry/self-assessment.md`'s quest
      log and the wider open-issue/PR lists, not just the original
      shortlist

## Skill polish

- [ ] Revise `cloudberry-pr-checklist`, `cloudberry-license-check`,
      `cloudberry-bug-report`, `cloudberry-ai-disclosure`,
      `cloudberry-mailing-list` based on what T20260810-723411 actually
      needed and didn't have, or got wrong/stale
- [ ] Re-run `/repo-conventions check` and a skill-conventions pass after
      edits

## Definition of done

- Backlog count and `project/cloudberry/self-assessment.md` XP log
  updated to reflect real closed items
- Skill changes committed with a clear note on what real-usage gap each
  edit closes
