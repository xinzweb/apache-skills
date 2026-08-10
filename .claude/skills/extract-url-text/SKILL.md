---
name: extract-url-text
description: Use when the user explicitly asks to extract, read, or pull the text content of a given URL — especially a page that returns empty/blocked content to a plain script or generic HTTP client
disable-model-invocation: false
argument-hint: "<url> [--max-chars N] [--ignore-robots]"
---

Fetch a URL with `scripts/extract.py` (stdlib-only Python — no install step)
and print its readable text. Built as a more reliable fallback for the
common case where a page blocks requests carrying no/generic User-Agent
strings (`curl`, bare `python-requests`) — it identifies as a normal
browser instead. It does **not** attempt to defeat JS-challenge or
CAPTCHA-based bot detection (e.g. Cloudflare's managed challenge) — that's
out of scope by design, not a missing feature; see Important Notes.

## Argument

`<url>` is required; flags are optional:

- `python3 .claude/skills/extract-url-text/scripts/extract.py "<url>"` —
  fetch and print readable text (default: truncated to 20000 chars).
- `--max-chars N` — change the truncation limit; `--max-chars 0` disables
  truncation entirely.
- `--ignore-robots` — skip the robots.txt allow-check. Only pass this when
  you have a specific, articulable reason the page should be fetched
  despite a disallow rule — never as a default habit.

## Workflow

1. Run the script from the repo root:
   ```bash
   python3 .claude/skills/extract-url-text/scripts/extract.py "<url>"
   ```
2. **robots.txt is checked by default** and the fetch is refused (exit code
   2) if disallowed for our user-agent — this is deliberate, not a bug.
   Don't reach for `--ignore-robots` reflexively; treat a disallow as a
   real signal, same as you would for a manual browser visit.
3. On success, stdout is: an optional `# <page title>` line, then the
   extracted body text (script/style/nav/header/footer/aside content
   stripped, whitespace collapsed). A redirect notice (if any) goes to
   stderr, not stdout, so it doesn't pollute the extracted text.
4. On failure, stderr explains why (HTTP status, timeout after retries,
   robots.txt block) and the script exits non-zero — read the message
   rather than retrying blindly with different flags.
5. If a page still comes back empty or clearly wrong after this, that's a
   sign the site uses a genuine JS-rendered/anti-bot-challenge frontend,
   not something this script's User-Agent trick can fix — fall back to the
   built-in `WebFetch` tool or ask the user to paste the content.

## Important Notes

- **Scope, explicitly**: this handles naive user-agent sniffing (the most
  common form of "why does `curl` get nothing but my browser works fine").
  It does not solve CAPTCHAs, does not spoof TLS/browser fingerprints, and
  does not rotate IPs/proxies to dodge rate limits — building any of that
  would cross from "read a public page" into bot-detection evasion, which
  this skill deliberately does not do.
- **robots.txt is respected by default** — this is a well-behaved fetcher,
  not a scraper that ignores site policy. Don't build a workflow around
  routinely passing `--ignore-robots`.
- Only for **publicly accessible** pages — this has no concept of login,
  cookies, or session state, so it cannot and should not be used against
  anything behind authentication or a paywall.
- Output is plain extracted text, not a faithful HTML→Markdown conversion
  (no links, no formatting) — if structure matters, use `WebFetch` instead,
  which converts to Markdown.
- Dependency-free by design (Python stdlib only: `urllib`, `html.parser`,
  `gzip`, `zlib`) — don't add a pip dependency (e.g. `requests`,
  `beautifulsoup4`) to this script; that would break it running anywhere
  without a prior `pip install` step.
