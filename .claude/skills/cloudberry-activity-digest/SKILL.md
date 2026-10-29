---
name: cloudberry-activity-digest
description: Use when the user explicitly asks to check apache/cloudberry for recent activity mentioning them, or to send/preview the daily activity digest email
disable-model-invocation: false
argument-hint: "[since <Nd|Nh, default 24h>] [dry-run]"
---

Emails a digest of Apache Cloudberry GitHub activity — `@`-mentions
(anywhere, including comments), threads this user authored or commented
on, and a roll-up of everything else that moved in the window.

**Source of truth is Gmail, not the GitHub API.** See "Why Gmail" below.
For shared project facts (repos, this user's GitHub handle) see
`../_cloudberry/README.md`.

## Argument

`$ARGUMENTS` is optional:

- `since <Nd|Nh>` — lookback window. Default: 24 hours (`1d`).
  Gmail's `newer_than:` accepts `d`/`h`; round sub-day windows **up** to
  the next whole day and filter precisely on each message's `date` field.
- `dry-run` — compose the digest and print it; do not send.
- No argument — default 24h window, sends the email.

## Why Gmail, not the GitHub API

Three GitHub paths were tried and all fail in a scheduled cloud session
(verified 2026-09-02):

- **The sandbox blocks GitHub outright.** Every request to
  `api.github.com` / `github.com` — `curl`, `git`, WebFetch, atom feeds —
  returns `403 GitHub access to this repository is not enabled for this
  session`. Only repos explicitly attached to the session pass the proxy,
  and `apache/cloudberry` cannot be attached: it belongs to the ASF org,
  so extending the Claude GitHub App to it needs Apache Infra, not us.
- **No `gh` CLI** is installed, and it could not authenticate anyway.
- **The `mentions:` search qualifier is the wrong tool regardless** — it
  indexes only issue/PR *titles and bodies*, never comments, which is
  exactly the case this skill exists for.

Meanwhile `commits@cloudberry.apache.org` mails **every** GitHub event on
every `apache/cloudberry*` repo to this inbox, filtered into the label
`1.Notifications.CloudBerry` (11k+ messages, ~15-25/day). Each mail
carries the actor, the action, the PR/issue number, the full comment
body, and the canonical `https://github.com/...` URL. That is a superset
of what the notifications API would have returned, it needs no GitHub
credentials, and it covers the sibling repos (`cloudberry-site`,
`cloudberry-backup`, `cloudberry-pxf`) too.

## Gmail query syntax that actually works here

Verified against this account — do not "improve" these without retesting:

- `label:1.Notifications.CloudBerry` — **label by NAME.** `label:Label_3`
  (the label ID) silently returns zero results through this MCP server.
- `from:git@apache.org` — equivalent and more robust; prefer it.
- `newer_than:2d`, `after:YYYY/MM/DD` — both work, and combine with terms.
- Free-text terms search message **bodies**, so `xinzweb` matches an
  `@xinzweb` mention buried in a code-review comment. This is the whole
  reason the approach works.
- `search_threads` previews only the ~5 **oldest** messages per thread and
  shows no truncation marker. Never read recency off a preview — call
  `get_thread` with `messageFormat: PLAIN_TEXT` for anything you report.

## Workflow

1. **Resolve the window.** Compute `SINCE` (UTC ISO8601) and the Gmail
   shorthand `WINDOW` (e.g. `1d`):

   ```bash
   SINCE="$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null \
          || date -u -v-24H +%Y-%m-%dT%H:%M:%SZ)"
   ```

2. **Primary query — direct involvement.** Gmail `search_threads`:

   ```text
   from:git@apache.org newer_than:<WINDOW> xinzweb
   ```

   Every hit is a message whose body names this user — an `@`-mention, a
   review request, or one of his own comments quoted in a reply chain.
   `get_thread` each hit (`PLAIN_TEXT`), then for each message inside the
   window read off: actor, action verb, repo, PR/issue number, the
   `URL: https://github.com/...` line, and one line of context.

   Classify each into a bucket by the body text:
   - **Mentioned** — body contains `@xinzweb`
   - **My threads** — `xinzweb opened|commented on|merged ...`
   - **Review requested / assigned** — body says so explicitly

3. **Supplementary query — everything else that moved.** Same window,
   no term, metadata-only view (do **not** fetch bodies for these):

   ```text
   from:git@apache.org newer_than:<WINDOW>
   ```

   Use `view: THREAD_VIEW_MINIMAL`; the `subject` + `snippet` alone give
   actor, action and PR number. Dedup against step 2 by PR/issue URL.
   Roll these up as counts per repo plus the 5-8 most notable threads
   (new PRs, merges, releases) — never a wall of every comment.

4. **Compose the digest** (Markdown):
   - One subsection per non-empty bucket: `Mentioned`, `Review requested`,
     `Assigned`, `My threads`, then `Other activity`.
   - Each line: `- <actor> <action> — <title> (#<number>)` linking the URL.
   - `Other activity` closes with a one-line count: `N more messages
     across apache/cloudberry, cloudberry-site, ...`.
   - If step 2 is empty, say so plainly ("no activity naming you in the
     last 24h") and still include the `Other activity` roll-up — silence
     must never be ambiguous between "nothing happened" and "the job
     didn't run".

5. **Send (skip if `dry-run`)** via the Gmail MCP `send_message` tool.
   The tool is namespaced differently per surface (`mcp__Gmail__*` here,
   `mcp__claude_ai_Gmail__*` elsewhere) — resolve it from the live tool
   list rather than hardcoding.
   - To: `75033us@gmail.com`
   - Subject: `[CC: Shine @Apache] apache/cloudberry activity — <YYYY-MM-DD>`
   - Body: the composed digest.

## Failure reporting

If the Gmail queries themselves fail (auth expired, connector off), send
a digest that says **tooling failure**, names the failing query verbatim,
and does not imply quiet. Never let an access failure render as
"no new activity".

## Notes

- Stateless by design — no persisted "last sent" timestamp. A missed run
  means the next window overlaps slightly; harmless for a digest.
- Requires only the Gmail connector. No GitHub access, no `gh`, no repo
  attachment — that independence is the point of this design.
- Scheduling is out of scope: the daily run is the
  `cloudberry-activity-digest-daily` scheduled task.
