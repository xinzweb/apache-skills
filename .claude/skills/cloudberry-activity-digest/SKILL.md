---
name: cloudberry-activity-digest
description: Use when the user explicitly asks to check apache/cloudberry for GitHub activity mentioning them, or to send/preview the daily activity digest email
disable-model-invocation: false
argument-hint: "[since <ISO8601|Nh, default 24h>] [dry-run]"
---

Emails a digest of apache/cloudberry GitHub activity involving this user —
`@`-mentions (anywhere, including comments), review requests, assignments,
and activity on threads they authored or are participating in. For shared
project facts (repo, this user's GitHub handle) see
`../_cloudberry/README.md`.

## Argument

`$ARGUMENTS` is optional:

- `since <ISO8601|Nh>` — lookback window start. Default: now minus 24 hours.
  `Nh` (e.g. `48h`) is shorthand for "N hours ago".
- `dry-run` — compose the digest and print it, but do not send the email.
  Useful for testing the query/formatting without generating mail.
- No argument — default 24h window, sends the email.

## Why notifications, not issue-search

GitHub's issue-search `mentions:` qualifier only indexes an issue/PR's
**title and body** — it does not index comments, so it misses exactly the
case this skill exists for (verified live 2026-08-31:
`mentions:xinzweb` → 0 all-time vs. `commenter:xinzweb` → 2). GitHub's
**notifications** API is the correct primary source instead: an
`@`-mention anywhere in a thread — body, comment, or PR review comment —
fires a notification with `reason: "mention"`, regardless of watch
status. Other `reason` values (`review_requested`, `assign`, `author`,
`comment`, `state_change`) cover "activity on PRs/issues I opened or am
assigned to review" for free, from the same query.

A GitHub Search sweep (`involves:`) runs as a **supplementary**
defense-in-depth check — proven necessary in practice: this account's
notifications history was empty at design time (2026-08-31), so relying
on notifications alone would have silently produced an all-quiet digest
even with real open activity (PR #1826, still open, is missed by
notifications but caught by `involves:`).

## Workflow

1. **Resolve the since-timestamp.**

   ```bash
   SINCE="$(date -u -v-24H +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ)"
   ```

   (BSD `date` on macOS uses `-v-24H`; GNU `date` uses `-d '24 hours ago'`
   — the `||` fallback covers both. Substitute the parsed `since <...>`
   argument here when given.)

2. **Primary query — notifications, scoped to apache/cloudberry:**

   ```bash
   gh api "notifications?all=true&since=${SINCE}" \
     --jq '[.[] | select(.repository.full_name=="apache/cloudberry")]'
   ```

   Group the results by `.reason` (`mention`, `review_requested`,
   `assign`, `author`, `comment`, `state_change`, `subscribed`,
   `team_mention`). For each item, resolve the human-readable link via
   `gh api "<.subject.url>" --jq .html_url` (the `subject.url` in a
   notification is an API URL, not a web URL, and issues vs. PRs need
   different `/issues/` vs. `/pull/` paths — fetching `html_url` sidesteps
   that instead of hand-building it).

3. **Supplementary query — GitHub search, `involves:<handle>`:**

   ```bash
   gh api "search/issues?q=repo:apache/cloudberry+involves:xinzweb+updated:>=${SINCE}" \
     --jq '.items[] | {number, title, html_url, updated_at, is_pr: (.pull_request != null)}'
   ```

   Dedup against step 2's results by `html_url` (or issue/PR number) —
   keep the notification's `reason` bucket when an item appears in both;
   file search-only hits under a `activity` bucket.

4. **Compose the digest** (Markdown):
   - Skip empty buckets; one subsection per non-empty bucket
     (`Mentioned`, `Review requested`, `Assigned`, `My threads`,
     `Other activity`).
   - Each line: `- <title> (#<number>) — updated <date>` linking the URL.
   - If both queries return nothing: still compose a short one-line "no
     new apache/cloudberry activity in the last window" digest — silence
     must never be ambiguous between "nothing happened" and "the job
     didn't run".

5. **Send (skip if `dry-run`)** via the Gmail MCP tool
   (`mcp__claude_ai_Gmail__send_message`):
   - To: `75033us@gmail.com`
   - Subject: `[CC: Shine @Apache] apache/cloudberry activity — <YYYY-MM-DD>`
   - Body: the composed digest.

## Notes

- Stateless by design — no persisted "last sent" timestamp. A missed run
  just means the next run's 24h window slightly overlaps the last one;
  harmless for a digest (see the task's design doc, T20260829-423782, for
  the rejected alternative of persisting since-state).
- Scheduling is out of this skill's scope — invoke it manually, or wire a
  daily `/schedule` cloud routine that runs `/cloudberry-activity-digest`.
