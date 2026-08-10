# Developer Guidelines

These guidelines apply to all work in the apache-skills project.

## Core Principles

- **KISS** / **DRY** — keep it simple, don't repeat yourself
- **Idempotent, sourceable, function-wrapped** bash scripts
- **Fix the root cause, not the symptom**

## Repo Layout

- `.claude/skills/` — Claude-facing skill definitions (SKILL.md + scripts).
  Fixed location, auto-discovered by Claude Code — never relocate a skill
  out of here even if its subject matter has a `project/<name>/` folder.
- `project/<name>/` — human-facing material for a specific Apache project
  this repo covers (career plans, self-assessments, issue-triage notes).
  One folder per project (e.g. `project/cloudberry/`).
- `dev/` — this repo's own TODO lifecycle (not project-specific).

## Content & Privacy Guidelines

This repo is public and its subject matter is other people's projects — hold every file to this bar before committing:

- **No secrets.** No API keys, tokens, passwords, or `.env` contents — ever, in any file.
- **No PII beyond self-disclosure.** Never add another person's private contact info (personal email, phone, address), even if it surfaced during research. Official ASF mailing-list addresses (`dev@`, `private@`, `secretary@`, etc.) are public infrastructure, not PII, and are fine to reference. Your own already-publicly-listed info (e.g. an ASF roster entry) is fine to include about yourself — that allowance doesn't extend to other individuals.
- **Cite, don't hoard.** Describe another project's process and link to the live official source rather than reproducing it wholesale — pages change, and a stale mirror reads as more authoritative than it is.
- **No fabricated claims about real people or projects.** Verify against a live source before writing a name, role, URL, or process detail into a committed file — see `.claude/skills/_cloudberry/README.md`'s sourcing for the pattern.
- **Apache-brand-friendly.** Use official project naming (e.g. "Apache Cloudberry (Incubating)", not "Cloudberry"), never imply ASF endorsement of this repo or its skills, and don't reproduce ASF/project logos or trademarks without checking ASF's trademark policy first.
- **Prefer roles over names — for *current-status* claims.** To illustrate a governance tier (e.g. "who's on the Board"), link to the live official roster instead of hardcoding specific individuals — those rosters turn over annually, and a stale name reads as a factual claim about someone no longer in that role. This does **not** apply to citing a specific, permanently-archived historical event (a real vote, an announcement, a merged PR) by name and date — that's a fixed fact from a public record, not a claim about someone's role today, and doesn't go stale the way "X currently holds role Y" does.

## Branch and Merge Policy

The `main` branch is the source of truth. Never push directly to `main`.

1. **Create a feature branch** — all changes go through a feature branch, no exceptions
2. **Branch naming**: `t{task-id}-short-description` for tracked tasks; `fix/`, `feat/`, `docs/` prefixes for untracked work
3. **Open a PR** — clear summary and test plan
4. **CI must pass** — all checks green before merge
5. **Merge method** — rebase and merge (`bash ~/.claude/skills/_gh/gh.sh pr merge --rebase --delete-branch`)
6. **Delete the branch after merge**

## TODO Lifecycle

Tasks live as individual files — the filesystem is the index. **Never mirror the index in CLAUDE.md.**

- **Open tasks**: `dev/TODO/*.md`
- **Parked tasks**: `dev/PARKING/*.md`
- **Completed**: `dev/JOURNAL/yyyy-mm-dd-{id}-slug.md`

### Task ID Format

```
TYYYYMMDD-NNNNNN
```

Generate with the shared helper — single source of truth, so every skill that creates a task uses the same generator and the same collision-avoidance rules:

```bash
bash ~/.claude/skills/_taskid/new.sh --check ./dev
```

Pass `--check <dev-dir>` so the helper rejects any ID that already exists under `dev/{TODO,PARKING,JOURNAL}/` and retries. Do NOT inline the `printf ... /dev/urandom ...` command in a new skill or script — add a call to this helper instead.

### Task File Header

Task metadata uses **YAML frontmatter** (`---` … `---` at the top of the file), same convention as `SKILL.md` files in `synx-skills`. The H1 title follows. See `synx-skills/todo/SKILL.md` for the full field schema and semantics.

```markdown
---
estimation: {30m|1h|2h|4h|1d|2d|1w|2w}
status: {Open|Design|Coding|Review|Blocked by T{id}}
source: {GitHub issue, upstream link, or process note}
description: {One-line summary}
---

# T{ID}: {Title}
```

### Status Flow

```
Open → Design → Coding → Review → Done
         ↕                          ↕
    Blocked by T{id}             Parked
```

- **Done** = `git mv` from `dev/TODO/` to `dev/JOURNAL/yyyy-mm-dd-{id}-slug.md`. Include this move in the implementing PR.
- **Parked** = `git mv` from `dev/TODO/` to `dev/PARKING/`.

### Branch Rule

**Do NOT update CLAUDE.md when journaling.** The `dev/JOURNAL/` folder IS the index. Mirroring it in CLAUDE.md duplicates content, eats the auto-loaded context budget, and creates merge conflicts on every completed task. CLAUDE.md only changes when the project's overall structure changes.

## Script Standards

```bash
#!/usr/bin/env bash
set -euo pipefail

function my-operation() {
  local param="${1:-default-value}"
  # Idempotent body
}

# Run only if executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  my-operation "$@"
fi
```

Rules: wrap logic in functions, make scripts sourceable, keep operations idempotent, use `set -euo pipefail`.

## Documentation

- **Task tracking**: `dev/TODO/` (active), `dev/JOURNAL/` (completed)
- **Inline comments**: only where logic isn't self-evident
- **Commit messages**: conventional commits format
- **Prefer bullets over paragraphs**: chunk information into bullet points, short lists, and tables so a reader can scan and find the one fact they need — don't bury it inside a paragraph. Keep each level to roughly 3 bullets; nest a sub-list under one of them instead of running past that into a wall of siblings, or folding the extra detail back into prose. Reserve prose for narrative that genuinely doesn't decompose (a root-cause story, a rationale). Applies to README, guidelines, task files, and JOURNAL entries alike.
