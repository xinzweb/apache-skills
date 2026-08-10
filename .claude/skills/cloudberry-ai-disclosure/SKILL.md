---
name: cloudberry-ai-disclosure
description: Use when Claude Code is drafting or has drafted a pull request, commit, or substantial code change for the apache/cloudberry repository
disable-model-invocation: false
argument-hint: "checklist | commit-trailer"
---

# Cloudberry AI-Disclosure

Apache Cloudberry's rules for AI-assisted (including Claude Code) contributions, sourced from `AI_GUIDELINE.md` and `AGENTS.md.template` at the root of `apache/cloudberry`. `AGENTS.md.template` frames Cloudberry as a safety-critical, distributed PostgreSQL-based database — "small changes can affect SQL semantics, query planning, storage, and distributed execution" — so treat every change, AI-assisted or not, with that in mind.

The core rule from `AI_GUIDELINE.md`: AI-generated code must clear the identical review/testing/CI bar as manual code, never a lower one, and "the contributor owns the final code" — the human, not the AI tool, stays accountable for everything submitted. Shared project facts (mailing lists, repo URLs, this user's role) live in `../_cloudberry/README.md`; this file covers only AI-disclosure rules and does not repeat them.

## Argument

- `checklist` (default): walk the pre-PR AI-disclosure checklist (§2) against the change you're about to submit.
- `commit-trailer`: draft the optional `Assisted-by:` commit-message trailer for the current commit (§4).

No-arg invocation runs `checklist`.

## Workflow

### §1. Ground yourself in the source of truth (best-effort)
This skill's facts are a snapshot of `AI_GUIDELINE.md` and `AGENTS.md.template` from the `apache/cloudberry` repo root. If you have live access to fetch those two files, do so and prefer their current wording over this skill's if they conflict. If you cannot re-fetch (no access, offline), proceed on the snapshot below rather than blocking the workflow.

### §2. Run the pre-PR checklist (must-block — do not open or push to the PR until every item is answered)
Before opening or updating a PR against `apache/cloudberry`, confirm all of the following for the change as a whole, not just the AI-touched hunks:

- **§2.a Tests.** The change ships with corresponding tests — either new tests or clearly-identified existing coverage. AI-generated code without tests does not meet the bar.
- **§2.b License cleanliness.** Every line is compatible with Apache License 2.0. Specifically verify no GPL-licensed or otherwise incompatibly-licensed code was reproduced by an AI tool — a real risk with AI code generation, so check anything that looks copied verbatim from a known non-Apache-licensed project.
- **§2.c No drive-by refactoring.** The diff is minimal, localized, and preserves existing code style. Reject or undo any "meaningless refactoring," unrelated reformatting, or cleanup-sprees the AI introduced outside the stated purpose of the change — these complicate rebasing and force other developers to relearn code that didn't need to change.
- **§2.d High-risk-area caution.** If the change touches catalog, storage, planner/optimizer, authentication, or cluster-management code, apply extra conservatism — prefer the smallest change that fixes the problem over a broader rewrite, and say so explicitly in the PR description so reviewers know to look closely.
- **§2.e No fabricated results.** Never claim a test passed, a benchmark ran, or a build succeeded unless you actually ran it in this session and observed the output yourself. If you did not run something, say so plainly.
- **§2.f Human accountability.** The human contributor, not the AI tool, is and remains accountable for all submitted code. Tell the human reviewer explicitly which parts were AI-drafted vs human-written where that isn't obvious, so they can review with appropriate scrutiny before they submit.

### §3. Tick the AI-disclosure checkbox when generation was substantial (must-block)
If the change involved **substantial** AI generation — Claude Code wrote most of the diff, not just autocomplete-scale suggestions or reformatting — check the AI-disclosure checkbox in the PR template before the human opens the PR. Minor assistance (autocomplete, small reformatting) does not need to be flagged. Use judgment on "substantial"; when in doubt, disclose. This skill covers only the disclosure decision, not the rest of the PR template — if a `cloudberry-pr-checklist` skill exists in this skills directory, defer to it for the full template walkthrough.

### §4. Offer the `Assisted-by:` commit trailer (recommended, not required)
Following the Linux-kernel convention, Cloudberry allows an optional trailer in the commit message naming the AI tool. Draft it as a normal trailer line, e.g.:

```
Assisted-by: Claude Code
```

Present the full drafted commit message (title + body + trailer) to the human for them to review and commit themselves — do not commit on the human's behalf. Use one of Cloudberry's conventional title prefixes (`Fix`, `Feature`, `Enhancement`, `Doc`) and wrap body lines.

### §5. Flag the review-engagement expectation (reminder, best-effort)
If this PR draws review comments, remind the human that Cloudberry expects them to engage personally in the discussion rather than paste AI-generated responses verbatim. Don't draft canned replies for the human to paste unedited — flag the expectation instead.

## Important Notes

- AI is explicitly welcomed at Cloudberry for bug fixing, code review, test writing, documentation, build systems, and security research — this skill is a compliance checklist, not a gate against using AI.
- Forbidden, no exceptions: code incompatible with Apache License 2.0; GPL-licensed or otherwise incompatibly-licensed code reproduced by an AI tool; meaningless or unrelated refactoring bundled into the change.
- `AGENTS.md.template` is a template contributors may copy into their own local, **uncommitted** `AGENTS.md` — do not commit an `AGENTS.md` file into the Cloudberry repo on the human's behalf.
- Catalog, storage, planner/optimizer, authentication, and cluster-management code are called out by name in `AGENTS.md.template` as needing extra conservatism — treat a change touching any of these as higher-stakes even if it looks small.
- This skill does not submit anything on its own. The checklist is for you to verify and report on; the commit-trailer text and any review-reply guidance are drafts for the human to review and act on themselves.
