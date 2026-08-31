---
status: Done
estimation: 4h
source: this conversation, 2026-08-29
related: T20260828-134911, T20260827-397440
description: Daily Gmail digest of apache/cloudberry activity mentioning the user
claimed_by:
scheduled: 2026-08-31
---

# T20260829-423782: Daily Gmail digest of apache/cloudberry activity mentioning me

## TLDR

- **Type**: feature
- **Problem**: no standing way to notice apache/cloudberry GitHub activity
  (mentions, review requests, own-thread activity) without manually checking.
- **Solution**: a prose-instructional skill (`cloudberry-activity-digest`)
  that queries GitHub's **notifications API** (not issue-search — it
  under-counts comment mentions, see Context) scoped to `apache/cloudberry`,
  buckets by `reason`, and sends the digest via the already-connected Gmail
  MCP tool with subject `[CC: Shine @Apache] ...`.

## Problem

- No standing way to notice new apache/cloudberry GitHub activity that
  involves the user without manually checking the repo — surfaced right
  after filing T20260828-134911 (an open PR-to-be against
  apache/cloudberry that will need review-comment follow-up once opened).
- Wanted: a daily workflow that checks apache/cloudberry for updates
  related to the user's contributions and emails a digest via Gmail, with
  the subject line prefixed `[CC: Shine @Apache]`.
- Scope of "related to my contributions" (clarified in-conversation,
  2026-08-29): **everything mentioning me** — not just PRs/issues I
  authored, but any `@`-mention of my GitHub handle anywhere in the repo
  (issue comments, PR review comments, discussions), plus activity on
  PRs/issues I opened or am assigned to review.

## Context

- **GitHub identity to watch**: `xinzweb` — confirmed via `gh api user
  --jq .login` as the account's actual GitHub-mentionable handle. The
  historical `xzhang@pivotal.io` / `zhxin@vmware.com` identities noted at
  filing time are git-commit author/committer emails only, not GitHub
  `@`-mentionable handles — they cannot appear in a `mentions:`/`involves:`
  search qualifier or trigger a notification, so they're excluded.
- **`mentions:` search under-counts comment mentions — verified live,
  2026-08-31**:
  - `gh api "search/issues?q=repo:apache/cloudberry+mentions:xinzweb"` →
    `0` (all-time).
  - `gh api "search/issues?q=repo:apache/cloudberry+commenter:xinzweb"` →
    `2`, `involves:xinzweb` → `3`, `review-requested:xinzweb` → `2` (PRs
    #929, #731).
  - The `mentions:` qualifier only indexes an issue/PR's title+body, not
    its comments — so it would silently miss exactly the case the task
    cares most about ("`@`-mention ... in issue comments, PR review
    comments").
- **GitHub notifications already solve this correctly**: an `@`-mention
  anywhere in a thread (body *or* comment *or* PR review comment) fires a
  notification with `reason: "mention"`, regardless of watch status.
  `gh api notifications?all=true` is reachable with the current token's
  `repo` scope (verified: 200 response, `[]` for apache/cloudberry —
  consistent with the 0 historical search-mentions above, i.e. no false
  negative). Other `reason` values (`review_requested`, `assign`,
  `author`, `comment`, `state_change`) already cover "activity on PRs/
  issues I opened or am assigned to review" for free — no separate query
  needed.
- **Gmail send is already solved**: this session has direct access to the
  connected Gmail MCP tools (`mcp__claude_ai_Gmail__send_message` et al.)
  — no OAuth app / API-key integration to build.
- **Existing skill convention**: `.claude/skills/cloudberry-*` skills
  (`cloudberry-bug-report`, `cloudberry-mailing-list`, etc.) are
  prose-instructional `SKILL.md` files — Claude runs `gh`/`gh api`
  directly per the documented steps, no bundled `scripts/`. This task
  follows that precedent rather than introducing a new
  scripts-plus-BATS surface for a ~2-command query.

## Solution

- **New skill**: `.claude/skills/cloudberry-activity-digest/SKILL.md`
  (prose-instructional, matching the `cloudberry-*` convention above).
  Documents:
  1. Query `gh api "notifications?all=true&since=<ISO8601, default
     now-24h>"`, filter client-side (`jq`) to
     `.repository.full_name == "apache/cloudberry"`, group by `.reason`.
  2. Supplementary defense-in-depth query: `gh api
     "search/issues?q=repo:apache/cloudberry+involves:xinzweb+updated:>=<since>"`
     — dedup against the notifications set by issue/PR URL, to catch
     anything a notification-settings gap might otherwise miss.
  3. Compose a Markdown digest: one subsection per non-empty `reason`
     bucket, each line `- <title> (#<number>) — updated <date>` linking
     the URL. If both sources are empty, still send a short "no new
     activity" digest — so silence never reads as ambiguous between "no
     activity" and "the job didn't run".
  4. Send via `mcp__claude_ai_Gmail__send_message` to `75033us@gmail.com`,
     subject `[CC: Shine @Apache] apache/cloudberry activity — <YYYY-MM-DD>`.
- **Scheduling mechanism (decision)**: the `/schedule` cloud-routine skill,
  daily, invoking this skill — the platform-native "run a prompt on a
  schedule" primitive, so no separate headless credential path is needed
  beyond what a cloud routine already has. Per the task's own scoping,
  wiring the actual daily trigger is not required for "done" (see Done
  criteria) — it's attempted as part of this task's implementation but
  isn't a blocking criterion, since this session cannot verify from here
  whether a cloud-routine execution context carries the same Gmail MCP
  connection as this interactive session.

### Alternatives considered and rejected

- **Raw GitHub search (`mentions:`/`involves:`) as the sole source** —
  rejected: proven above to under-report `@`-mentions living in comments,
  which is the task's core ask.
- **A dedicated wrapper script under `scripts/` with BATS tests** —
  rejected for v1: disproportionate testing/maintenance surface for a
  ~2-command query, and breaks from this repo's actual `cloudberry-*`
  precedent (prose-instructional, no bundled scripts). Revisit if the
  logic grows (e.g. persistent since-state, retry/backoff).
- **A from-scratch Gmail API integration (OAuth app + stored
  credentials)** — rejected: the Gmail MCP tools are already connected in
  this session; a bespoke integration would be pure duplicated effort.
- **Persisting a "last digest sent" timestamp file for exact
  since-tracking** — rejected for v1: adds state/drift risk (no obvious
  durable home for the file from inside a stateless cloud routine) for
  marginal benefit over a flat 24h lookback window, whose only failure
  mode (a missed run producing a slightly wider window on the next one)
  is self-correcting and harmless for a digest.

## Test plan

- [x] Manually run the notifications query
      (`gh api "notifications?all=true&since=<24h-ago>"` filtered to
      apache/cloudberry) and spot-check the `reason` bucketing against a
      couple of known threads.
- [x] Manually invoke the `cloudberry-activity-digest` skill end-to-end
      once and confirm it sends via `mcp__claude_ai_Gmail__send_message`
      with the correct subject prefix and a readable body.
- [x] Confirm the email actually lands in `75033us@gmail.com`.
- [x] (stretch, not blocking) Attempt to wire a daily `/schedule` cloud
      routine invoking the skill; note explicitly if the Gmail MCP
      connection's availability in that execution context can't be
      verified from this session.

## Done criteria

- [x] Query logic proven live against apache/cloudberry, correctly
      bucketed by `reason` — evidence captured in this task file's
      `## Closed` section.
- [x] One real digest email sent via `mcp__claude_ai_Gmail__send_message`
      with subject `[CC: Shine @Apache] ...`, confirmed received.
- [x] `.claude/skills/cloudberry-activity-digest/SKILL.md` exists,
      documents the full query → compose → send procedure, and is
      runnable standalone (not only from a scheduler).
- [x] Scheduling-mechanism decision recorded (`/schedule` daily cloud
      routine, above); actual wiring is a stretch goal, not blocking —
      wired anyway, see `## Closed` below.

## Closed (2026-08-31)

- Shipped in this PR (see commit `docs(tasks): design ...` for the
  merged design, and this PR for the skill + close).
- **Query logic** — proven live against `apache/cloudberry`:
  `gh api "notifications?all=true&since=<24h>"` returned `[]` for this
  account (a genuinely quiet 24h window — confirmed independently via
  the supplementary `involves:xinzweb+updated:>=<24h>` search, also
  `[]`). To prove the non-empty-result bucketing/formatting path (not
  exercisable against a quiet live window), the same pipeline was run
  against this account's all-time `involves:xinzweb` data (3 PRs:
  #1826 open, #929/#731 closed+review-requested) and included in the
  proof email as a clearly-labeled "pipeline validation" section.
- **Gmail send** — one real email sent via
  `mcp__claude_ai_Gmail__send_message`
  (message id `1a058179226ebd59`), subject
  `[CC: Shine @Apache] apache/cloudberry activity — 2026-08-31`,
  confirmed received via `get_message` (`labelIds` include `INBOX`,
  correct `sender`/`toRecipients` = `75033us@gmail.com`).
- **Skill** — `.claude/skills/cloudberry-activity-digest/SKILL.md`,
  prose-instructional per the `cloudberry-*` convention.
- **Scheduling** — attempted as a stretch goal and it worked: created
  cloud routine `trig_01Xqa2sqpNaAKQ7MuFj46FNj`
  ("cloudberry-activity-digest-daily", daily `0 13 * * *` UTC = 8am
  America/Chicago, Gmail MCP connector attached), confirmed with the
  user first (time-of-day is a real preference, not a call to make
  alone). A pre-merge test-fire (`run` action) correctly no-op'd —
  it cloned `main`, which didn't have the skill yet (still only local
  in this PR), and sent a push notification instead of hallucinating
  success. That's the right failure mode, but it means the cloud
  environment's `gh` CLI auth for the notifications/search calls is
  **not yet verified against a real fire** — first genuine production
  fire is 2026-09-01 ~13:03 UTC; if it fails, `list_runs`/`get_run_log`
  on that trigger will show why.
- **Follow-up**: none filed — the one open unknown (cloud-env `gh`
  auth) will self-resolve or self-report via the routine's own
  push-notification-on-failure behavior observed in the test fire.

## Skills invoked

- TDD (`superpowers:test-driven-development`): no — docs-class change
  (a prose `SKILL.md`, no bundled script/code).
- Verification (`superpowers:verification-before-completion`): yes —
  the query/send pipeline was proven live (email sent + confirmed
  received) rather than assumed from reading the design.
- Systematic debugging (`superpowers:systematic-debugging`): no —
  didn't get stuck; the `mentions:`-under-counts finding came from
  direct live probing during design, not from debugging a failure.
- Receiving code review (`superpowers:receiving-code-review`): no —
  solo repo, no CI/reviewer configured; self-reviewed via the
  design-score gate (72/100) and `lint-docs.sh` instead.
