---
name: cloudberry-pr-checklist
description: Use when the user explicitly asks to open, prepare, or review a pull request against Apache Cloudberry
disable-model-invocation: false
argument-hint: "prepare | checklist <PR number>"
---

# Cloudberry PR Checklist

Prepare a new pull request against `apache/cloudberry`, or review an already-open
one against the repo's actual merge gates (`.github/pull_request_template.md`
and `.asf.yaml` branch protection). See `../_cloudberry/README.md` for shared
project facts (repo, mailing lists, this user's role); this file inlines
everything specific to opening and reviewing a PR.

## Argument

- `prepare` (default, no arg): walk the branch/commit workflow and draft the
  PR template content for a PR that has not been opened yet.
- `checklist <PR number>`: review an already-open PR against the merge-gate
  checklist (branch protection, reviewer checklist, template completeness).

## Workflow

### §1. `prepare` — get the branch and PR content ready

1. **Branch workflow** (best-effort to walk, but do each step for real, don't
   skip):
   a. Confirm the repo is forked to the user's own GitHub account and cloned
      locally.
   b. Check for the upstream remote before adding it (`git remote -v`); if
      missing, add it: `git remote add upstream https://github.com/apache/cloudberry.git`.
   c. Create a feature branch, make the change, and write tests for it.
   d. Follow PostgreSQL coding standards while writing: 4-column tab spacing,
      BSD-style brace/indent layout, lines within 80 characters, match the
      style of the nearby existing code, and follow the "PostgreSQL Error
      Message Style Guide" for any error messages. Editor configs exist for
      Vim/Emacs/CLion if the user wants them.
   e. Commit, then push the branch to the user's fork (not upstream).
2. **Must-block — no rebasing published commits.** Once a PR is open and
   under review, do **not** rebase, amend, or force-push commits that
   reviewers may already have commented on — it destroys the reviewer
   comment anchors and confuses the review. Push additional commits on top
   instead. (This is distinct from the wiki's "Rebase-and-merge" technique,
   which is a **committer-only, final-merge** workaround for very large
   PRs — see `cloudberry-release-runbook` — not something a PR author does
   to their own branch mid-review.)
3. **Draft the PR template content.** `.github/pull_request_template.md`
   auto-populates on PR creation; fill in each section rather than leaving
   template boilerplate:
   - Issue link: `Fixes #ISSUE_Number`.
   - "What does this PR do?" — a real description, not a placeholder.
   - Type of Change checkbox: Bug fix / New feature / Breaking change /
     Documentation update.
   - Breaking Changes section — fill in, or remove the section if not
     applicable.
   - Test Plan checklist: unit tests added/updated, integration tests
     added/updated, passed `make installcheck`, passed
     `make -C src/test installcheck-cbdb-parallel`. Only check a box for a
     command you (or the human) actually ran and observed pass — never mark
     a test-plan item done on the assumption it would pass.
   - Impact section: Performance / User-facing changes / Dependencies.
   - Final Checklist: followed the contribution guide
     (cloudberry.apache.org/contribute/code), added/updated documentation,
     reviewed code for security implications, disclosed whether the PR
     contains AI-assisted code generation (run the `cloudberry-ai-disclosure`
     skill to work through this item, don't answer it ad hoc), requested
     review from the `cloudberry-committers` GitHub team.
4. **CI-skip tag, only if this PR is documentation-only or otherwise
   exceptional.** To skip CI, put a bracketed tag containing "ci" plus
   "skip" or "no" in the PR **title** itself — e.g. `[skip ci]`,
   `[ci skip]`, `[no ci]`. Putting it in the PR body does nothing; it must
   be in the title. Do not use this for ordinary code changes.
5. **Must-block.** Present the full drafted PR title, body (all template
   sections filled in), and target branch to the user for review before
   opening anything — opening a public PR notifies the whole project and
   requests reviewer time, so it isn't something to fire off unattended,
   the same principle as sending email or filing an ICLA. Once approved,
   open it with `gh pr create --repo apache/cloudberry` (fill `--title`
   and `--body` from the approved text) or point the user at
   `https://github.com/apache/cloudberry/compare` to open it themselves.

### §2. `checklist <PR number>` — review an already-open PR

1. Pull the current state: `gh pr view <PR number> --repo apache/cloudberry`
   and `gh pr checks <PR number> --repo apache/cloudberry`.
2. Walk the reviewer checklist from the Code Contribution Guide against the
   PR (best-effort — flag what you can verify from the diff/description,
   note what needs a human's judgment):
   - Necessity/scope: does the change align with the project, and is there a
     prior proposal/acceptance for it where one would be expected?
   - PR size: is it small enough to review, or does it need splitting?
   - Code-convention alignment (PostgreSQL style, per §1.1.d).
   - Backward compatibility.
   - CI/test pipeline success.
   - Code efficiency and readability.
   - License compatibility: **Apache License 2.0 components only** — no
     GPLv2/3 or other non-OSI-compatible code anywhere in the diff. Treat
     any hit here as a hard blocker, not a nitpick.
3. **Must-block — check branch protection gates**, per `.asf.yaml`: `main`
   requires 2 approving reviews (stale reviews are not auto-dismissed), all
   review conversations resolved, and the required status checks green and
   up to date with `main` (strict checks) — roughly 15 checks including
   `rat-check` (see `cloudberry-license-check`), RPM build/install tests,
   the `ic-*`/`pax-ic-*` integration-check jobs, and `build-report`. Merges
   are squash-and-rebase only with linear history required (plain merge
   commits are disabled); commit signatures are not required. The branch
   auto-deletes after merge.
4. Confirm review was requested from the `cloudberry-committers` GitHub
   team, and confirm the AI-disclosure checkbox state matches reality (run
   `cloudberry-ai-disclosure` if this wasn't already settled in `prepare`).
5. Report the checklist result to the user as a pass/fail list against
   steps 2-4, not a merge action — merging itself requires approval from at
   least 2 maintainers with write access, which is not something this
   skill or Claude Code does on the user's behalf.
6. If review has been open with no feedback, the guide sets the expectation
   of waiting **up to two weeks** before proactively pinging the
   `cloudberry-committers` team — don't recommend pinging sooner than that.

## Important Notes

- Never rebase, amend, or force-push commits on a branch that already has an
  open PR under review (§1.2) — this is the single most disruptive mistake a
  PR author can make mid-review.
- License compatibility is a hard gate, not a style preference: Apache
  License 2.0 components only, no GPLv2/3 or other non-OSI-compatible code.
- Never open a PR, or otherwise submit to GitHub, before the user has
  explicitly approved the exact drafted title/body — same rule as filing an
  issue or sending an email.
- This skill does not merge PRs and does not decide CI/review outcomes on
  the user's behalf; it drafts, checks, and reports so a human (or a
  committer with write access) can act.
- For shared community facts (mailing lists, Slack, Discord, this user's
  PPMC status), see `../_cloudberry/README.md` rather than re-deriving them
  here.
