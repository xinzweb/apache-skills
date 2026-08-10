---
name: cloudberry-release-runbook
description: Use when the user explicitly asks to cut an Apache Cloudberry release, follow the source release checklist, or merge a large pull request that GitHub's UI cannot rebase
disable-model-invocation: false
argument-hint: "checklist | runbook | merge-large-pr <PR number>"
---

# Cloudberry Release Runbook

Coordinates Release Manager (RM) work for `apache/cloudberry` per the project
wiki (https://github.com/apache/cloudberry/wiki): the Release Process
Overview, the Release Runbook, and the Source Release Checklist. Everything
here assumes **committer push access** — release management and the
large-PR merge workaround both require it; if the user doesn't have it, say
so and stop. See `../_cloudberry/README.md` for shared project facts (repo,
mailing lists, this user's PPMC status); this file inlines the release- and
merge-specific facts on top of that.

At a high level, per the Release Process Overview, an RM (a committer chosen
by community consensus) takes a release through: goals/timeline → finalize
the codebase (reviews, testing, dependency/license audits) → update docs →
Apache RAT → set the version via SemVer → cut and sign a release candidate
(RC) → community testing → a formal vote → IPMC approval → publish and
announce. `runbook`/`checklist` below walk the mechanics; `merge-large-pr`
is a standalone git operation used while assembling the release branch.

## Argument

`$ARGUMENTS` is one verb, optionally with an argument:

- `runbook` (default, no arg) — walk the full RM playbook end-to-end:
  prerequisites, preparation, validation, the two-stage vote, publication.
- `checklist` — walk just the Source Release Checklist, the 7-stage,
  artifact-level list for producing one RC's source release.
- `merge-large-pr <PR number>` — merge a specific large PR (100+ commits)
  into a release branch via CLI rebase, working around GitHub's disabled
  "Rebase and merge" button.

## Workflow

### §1. `runbook` — full RM playbook

1. **Must-block.** Confirm RM prerequisites before doing anything else: an
   Apache account, committer access, a registered GPG key, and SVN
   credentials. If any is missing, stop and tell the user which one, rather
   than proceeding partway.
2. **Preparation.**
   a. Start a discussion thread on `dev@cloudberry.apache.org` announcing
      the intent to release. Use the `cloudberry-mailing-list` skill
      (`draft-discuss` or `draft-proposal`) to draft it — do not send it
      yourself, hand the draft to the user.
   b. Align release-branch commits and versions across all components that
      ship together: core, `cloudberry-backup`, `cloudberry-pxf`.
   c. Tag the RC as `x.x.0-incubating-rcN`.
   d. Generate signed artifacts using the repo's provided release scripts
      (not ad hoc commands you construct yourself).
   e. All of this happens on a dedicated release branch (e.g.
      `REL_2_STABLE`) — confirm the actual branch name for this release
      rather than assuming; never do release prep on `main`.
3. **Validation (must-block before moving to a vote).**
   a. Untar the source artifacts and confirm a clean build from source on
      multiple operating systems.
   b. Verify GPG signatures, SHA-512 checksums, and Apache RAT — see §2
      stages 3–4 (or `cloudberry-license-check` for the RAT mechanics in
      more depth) for how each of those is produced/checked.
4. **Voting — two stages, both required.**
   a. **Stage 1 (community):** vote on `dev@cloudberry.apache.org`, open
      ≥72 hours, needs ≥3 binding **+1** from the PPMC. Draft it with
      `cloudberry-mailing-list`'s `draft-vote` verb, but note the recipient
      list here is `dev@cloudberry.apache.org`.
   b. **Stage 2 (Incubator PMC):** only after stage 1 passes, vote on
      `general@incubator.apache.org`, open ≥72 hours, needs ≥3 binding
      **+1** from the IPMC.
   c. A failed vote at either stage means regenerating the RC and returning
      to step 2 — it does not mean patching the existing RC in place.
5. **Publication.** Promote the RC from `dist/dev` to `dist/release` via
   SVN, tag it, generate the changelog, update the website, and announce to
   `announce@apache.org`. Treat sending the announcement the same as any
   other outbound email from this skill (see `cloudberry-mailing-list`'s
   draft-and-hand-off step): draft it, hand it to the user, do not send it
   yourself.
6. **Must-block, incubating-specific:** every artifact filename must
   include "incubating", and the release must ship a `DISCLAIMER` file.
   Confirm both are present before any vote is called, not just before
   publication.

### §2. `checklist` — Source Release Checklist (7 stages)

Use this when the user wants just the artifact-level checklist for one RC,
without walking the full RM lifecycle in §1.

1. Tag the release with SemVer plus `-incubating`, cut from a clean commit
   (no uncommitted or cherry-picked-but-unpushed changes).
2. Assemble source archives with `git archive`. Confirm the archive
   contains `LICENSE`, `NOTICE`, `DISCLAIMER`, and `README`, and contains
   **no binaries**.
3. GPG-sign the artifacts and generate SHA-512 checksums. Confirm the
   signing key is on the public keyservers.
4. **Must-block.** Run `mvn apache-rat:check` and review dependency
   licenses for compatibility (Apache-2.0 or ASF-compatible only). For the
   detailed RAT workflow (reading `target/rat.txt`, header vs. exclusion
   decisions), use the `cloudberry-license-check` skill rather than
   re-deriving it here.
5. Upload the artifacts to the ASF dev staging area,
   `dist.apache.org/repos/dist/dev/incubator/cloudberry/`, via SVN, using
   standardized naming.
6. **Must-block.** Get community verification: at least one committer
   *other than the RM* must independently confirm the build from source
   before a vote is called. Do not call the vote on the RM's own build
   confirmation alone.
7. Send the formal vote email to `dev@cloudberry.apache.org` (draft via
   `cloudberry-mailing-list`, hand to the user to send), then seek IPMC
   approval on `general@incubator.apache.org` — this is §1.4 above.

### §3. `merge-large-pr <PR number>` — CLI rebase-and-merge

GitHub's "Rebase and merge" button is disabled or fails for very large PRs
(100+ commits). **That is a UI limitation, not evidence the PR is broken** —
don't treat the disabled button as a signal to re-review the PR's content.

1. Confirm the target release branch for this merge (e.g. `REL_2_STABLE`)
   with the user or the PR itself — must-block, never assume the branch
   name.
2. Fetch and check out the PR branch — `gh pr checkout <PR number>`, or
   without `gh`:
   ```
   git fetch origin pull/<PR number>/head:pr-<PR number>
   git checkout pr-<PR number>
   ```
3. Update the local release branch to match the remote:
   ```
   git checkout <release-branch>
   git pull --ff-only origin <release-branch>
   ```
4. Rebase the PR branch onto the updated release branch:
   ```
   git checkout pr-<PR number>
   git rebase <release-branch>
   ```
   **Must-block on conflicts:** resolve them by hand, commit-by-commit. Do
   not blanket-resolve with `-X ours`/`-X theirs` — that silently drops one
   side's intent across potentially dozens of commits.
5. Fast-forward-only merge into the release branch:
   ```
   git checkout <release-branch>
   git merge --ff-only pr-<PR number>
   ```
   If this fails, the rebase didn't leave the branch fast-forwardable — stop
   and re-rebase. Do **not** fall back to a regular (non-`--ff-only`) merge;
   that reintroduces the merge commit this workaround exists to avoid.
6. **Must-block, before pushing.** Verify no merge commits were introduced
   and history stayed linear:
   ```
   git log --oneline --merges <release-branch>@{upstream}..<release-branch>
   git log --graph --oneline -20 <release-branch>
   ```
   The first must print nothing; the second should show a straight line,
   not a fork/join.
7. **Must-block.** Push only once step 6 is clean, and only with explicit
   confirmation from the user if there's any doubt — this writes directly
   to a shared release branch:
   ```
   git push origin <release-branch>
   ```

## Important Notes

- This entire skill assumes committer push access to `apache/cloudberry`.
  If that's not confirmed for the user, stop and say so rather than
  attempting any step in §1–§3.
- This is a prose/drafting skill for anything that leaves the repo as an
  email (discussion, vote, announcement) — always hand the drafted text to
  the user and let them send it from their own subscribed address; never
  send it yourself. Use `cloudberry-mailing-list` for the actual drafting
  mechanics.
- Incubating-release requirements are non-negotiable release-content items,
  not optional polish: "incubating" in every artifact filename, plus a
  `DISCLAIMER` file in the source archive.
- The wiki pages this skill is sourced from were last checked 2026-08-09/10
  (see `../_cloudberry/README.md`) — treat exact field names, script
  locations, and staging paths as a snapshot, and re-check the live wiki
  before treating anything here as current if the release process may have
  changed since.
- A failed vote (either stage in §1.4) means regenerating the RC, not
  patching the existing one in place.
