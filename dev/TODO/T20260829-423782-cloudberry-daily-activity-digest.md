---
status: Design
estimation: 4h
source: this conversation, 2026-08-29
related: T20260828-134911, T20260827-397440
description: Daily Gmail digest of apache/cloudberry activity mentioning the user
claimed_by: Shines-Laptop.local:/Users/xlj/workspace/xinzweb/apache-skills
scheduled: 2026-08-31
---

# T20260829-423782: Daily Gmail digest of apache/cloudberry activity mentioning me

## Problem

- **Type**: feature
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
- Known GitHub identities to watch (from this repo's earlier contribution
  cataloging work, `dev/JOURNAL/` — the Greenplum-era legacy-contribution
  catalog task): `xinzweb` is the primary active handle; historical
  commits also carry `xzhang@pivotal.io` / `zhxin@vmware.com` as
  co-author/committer emails, but those are unlikely to be relevant to a
  forward-looking mention-watch (they're git-commit identities, not
  GitHub `@`-mentionable handles) — confirm the actual handle(s) to watch
  at design time rather than assuming.
- Done looks like: a working v1 — the query logic (what GitHub API/search
  surfaces "mentions me" + my own PR/issue/review activity) and the Gmail
  send (correct subject prefix, readable digest body) both proven working
  end to end at least once, manually triggered. The daily-schedule
  mechanism itself (cron vs. the `/schedule` cloud-routine skill vs.
  something else) is a design-time decision, not fixed by this filing.
