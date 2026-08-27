---
status: Open
estimation: 2d
source: conversation 2026-08-27 — surfaced while manually driving T20260827-107079's follow-up work (apache/cloudberry issue #726)
description: Teach /drive (and /ccxp) to natively drive work in apache/cloudberry itself, not just this repo's own dev/TODO tasks
---

# T20260827-397440: Fold the ccxp/drive skillset into cloudberry-driven upstream work

## Problem

- This repo has two skill families that have never been connected:
  `.claude/skills/{drive,ccxp,todo,claim,stage,top,bottom}` (the generic
  engineering-loop orchestrator — task lifecycle, claim locking, PR-driving)
  and `.claude/skills/cloudberry-*` (Apache Cloudberry-specific process:
  `cloudberry-license-check`, `cloudberry-ai-disclosure`,
  `cloudberry-pr-checklist`, `cloudberry-bug-report`,
  `cloudberry-mailing-list`, `cloudberry-discuss`,
  `cloudberry-committer-onboarding`, `cloudberry-release-runbook`).
- Concretely observed this session: driving a real fix for
  `apache/cloudberry` issue [#726](https://github.com/apache/cloudberry/issues/726)
  (surfaced from `T20260810-723411`'s "Pick at least one real item" list)
  required manually re-deriving, from scratch, everything `/drive`'s
  existing `Target repo:` cross-repo dispatch (Phase 1.5) already automates
  for *internal* Synx-Data-Labs repos: research the issue, design the fix,
  find/validate a build+test harness, write the patch, run tests. None of
  the `cloudberry-*` skills were invoked along the way even though at least
  `cloudberry-license-check`, `cloudberry-ai-disclosure`, and
  `cloudberry-pr-checklist` clearly apply once a real PR is about to open
  against `apache/cloudberry` — they simply aren't wired into `/drive`'s
  flow, so nothing prompts for them.
- Done looks like: `/drive`'s cross-repo path (or a thin
  `cloudberry-drive` wrapper around it) automatically applies the
  Cloudberry-specific gates and a documented build/validate harness when
  the target is `apache/cloudberry`, and `/ccxp`/`/todo next` can source
  candidate work directly from apache/cloudberry's own issue tracker (e.g.
  `good first issue`/`help wanted` labels), not only this repo's
  `dev/TODO/queue.md`.

## Context

- `/drive` Phase 1.5 (cross-repo dispatch) already has the right shape:
  hub repo (`apache-skills`, where the task file + tracking lives) +
  ephemeral target-repo clone. It was designed for internal
  Synx-Data-Labs repos, where the target repo shares this project's own
  conventions (dev/TODO, `task_claim.sh` peer-locking, CI-gated auto-merge).
  None of that holds for `apache/cloudberry`:
  - **No dev/TODO in the target repo** — apache/cloudberry doesn't have
    (and shouldn't get) our task-lifecycle files; the task/tracking stays
    entirely in `apache-skills`' own `dev/TODO/`.
  - **No `task_claim.sh` peer-lock** — Cloudberry's own claim norm is
    informal: a GitHub issue assignee (often set by a triage bot,
    `my-ship-it`, once someone starts work) with no comment-to-claim rule.
    Verified this session via `gh api` history on 6+ closed
    "good first issue" tickets — assignee-then-PR is the real pattern, not
    anything `/drive` currently models.
  - **Contribution gates that don't exist for internal repos**: license/RAT
    check, AI-assisted-authorship disclosure, the maintainer PR checklist —
    each already has its own skill (`cloudberry-license-check`,
    `cloudberry-ai-disclosure`, `cloudberry-pr-checklist`) but nothing
    currently *calls* them from `/drive`'s Phase 4.
  - **Build/test is not `npm test`** — verified this session: official docs
    (`cloudberry.apache.org/docs/build/`) support Rocky Linux 8+/Ubuntu
    20.04+ only (macOS build support was dropped from current docs), need
    8GB+ RAM / 20GB+ disk, and stand up an 8-process MPP demo cluster. A
    fast local path exists via Docker (this session used
    `Synx-Data-Labs/2026-cfp-coc-asia`'s `make dist
    CLOUDBERRY_LOCAL_SRC=<patched-checkout> CLOUDBERRY_REF=<branch>` +
    `make cluster`, reusing a cached from-source GCC toolchain image) but
    that path isn't documented anywhere `/drive` would find it.
- Existing `cloudberry-*` skills (already written, just unwired):
  `.claude/skills/cloudberry-license-check`, `cloudberry-ai-disclosure`,
  `cloudberry-pr-checklist`, `cloudberry-bug-report`,
  `cloudberry-mailing-list`, `cloudberry-discuss`,
  `cloudberry-committer-onboarding`, `cloudberry-career-path`,
  `cloudberry-release-runbook`.

## Solution (starting sketch — needs a real design pass before implementation)

- **Option A — extend `/drive` directly**: when Phase 1.5's `Target repo:`
  resolves to `apache/cloudberry` (or a configurable list of "Apache
  project" targets), branch its Phase 4 (Create PR) to require
  `cloudberry-license-check` + `cloudberry-ai-disclosure` +
  `cloudberry-pr-checklist` before opening the PR, and point Phase 3
  (Implement) at a documented build/validate harness doc instead of the
  generic test-runner assumption.
- **Option B — a thin `cloudberry-drive` wrapper skill**: a new
  `.claude/skills/cloudberry-drive/SKILL.md` that sets up the
  Cloudberry-specific context (target repo, claim norms, gates, build
  harness pointer) and then invokes `/drive` under the hood — keeps
  `/drive` itself generic, avoids Apache-specific branching inside a
  skill used by non-Cloudberry repos too.
- Either option needs, as its own sub-piece: a `cloudberry-ccxp`
  auto-pick source (query apache/cloudberry's `good first issue`/
  `help wanted`-labeled open issues, cross-reference against already-open
  PRs the way `T20260827-203753`'s research did, surface as `/todo`-style
  candidates) and a written-down build/validate harness doc (this
  session's playbook, generalized past the one Docker repo that happened
  to be available).
- **Alternatives not yet weighed** — this needs its own design pass:
  whether the build harness should point at `2026-cfp-coc-asia` specifically
  (a conference-talk repo, not meant to be a permanent dependency) vs. the
  official `devops/sandbox -c local` path vs. something apache-skills
  should own and maintain itself.

## Test plan

- [ ] Design doc written and scored (`design-score/scripts/score.sh`)
      before implementation, per standard `/drive` Phase 2 gate
- [ ] Dry-run against a second real apache/cloudberry issue (not #726 —
      that one will already be closed) to prove the wired-up gates and
      build harness actually fire and work end to end

## Done criteria

- [ ] `/drive` (or `cloudberry-drive`) opens a real apache/cloudberry PR
      that visibly ran `cloudberry-license-check` +
      `cloudberry-ai-disclosure` + `cloudberry-pr-checklist` as part of the
      flow, not as a manually-remembered extra step
- [ ] A documented, referenced build/validate harness exists that the next
      session doesn't have to rediscover from scratch
- [ ] `cloudberry-ccxp` (or equivalent) can surface a candidate
      apache/cloudberry issue without the user naming one first
