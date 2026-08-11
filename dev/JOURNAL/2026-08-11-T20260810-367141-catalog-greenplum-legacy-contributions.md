---
status: Done
estimation: 4h
priority: Medium
source: conversation 2026-08-10/11 — user asked for a thorough search of greenplum-db org history
description: Fully catalog Shine Zhang's Greenplum-era contributions across greenplum-db repos for project/cloudberry/self-assessment.md
claimed_by:
scheduled: 2026-08-10
---

# T20260810-367141: Catalog Greenplum-era legacy contributions

Full catalog complete (2026-08-11), including dedup by SHA — the raw
per-identity search counts double-count commits that appear in more than
one repo (shared donated history between `gpdb-archive`/`gporca-archive`/
etc.), so the honest total is lower than the first scoping pass reported.

## Confirmed identities (user confirmed both corporate emails are theirs)

- GitHub `xinzweb` — direct author, **34 unique commits** (48 raw
  search hits before dedup)
- `xzhang@pivotal.io` — direct author, **151 unique commits** (181 raw,
  Pivotal era). Verified as the same person: the merge commit for PR
  "xinzweb/enable_ccache" (`gporca-archive` `b53c1acd`) has this email as
  the second parent's author — the actual PR branch, pushed from the
  `xinzweb` GitHub account, used this email for its commits.
- `zhxin@vmware.com` — direct author, **24 unique commits** (no
  cross-repo duplication — all in one repo), VMware era, post-Pivotal
  acquisition. User-confirmed. Spot-checked commit content (not just
  titles): real, substantive RPM/Debian packaging and Concourse CI
  release-engineering work, e.g. `aad732dc` (single-file build-script
  change) and `3871bd0a` (4-file, +119/-85, co-authored with two other
  VMware engineers) — a materially different kind of work than the
  2016-era ORCA/gpdb code fixes.

No 4th identity found — tried `xin.zhang@{pivotal.io,vmware.com}`,
`xzhang2@pivotal.io`, `xzhang@vmware.com`, `zhangxin@{pivotal.io,vmware.com}`,
and `author-name:"Shine Zhang"` org-wide. All returned 0.

## Final numbers (deduplicated by SHA, 2026-08-11)

- **209 unique direct-author commits**: 34 (`xinzweb`) + 151
  (`xzhang@pivotal.io`) + 24 (`zhxin@vmware.com`)
- **+25 additional unique commits** credited only as `Co-authored-by`
  (45 raw `Co-authored-by: Xin Zhang` hits, 20 of which are the same SHA
  already counted in direct-author — likely squash-merge duplication of
  the primary author into the merge commit's trailer)
- **+4 additional unique commits** credited only as `Reviewed-by` (no
  overlap with either set above)
- **238 total distinct commits** touched in some capacity
- Repos: `gpdb-archive`, `gporca-archive`, `gp-xerces-archive` (not
  previously known to the user — surfaced by this search),
  `greenplum-database-release-archive`
- Date range: 2016-01 through 2023-11 (nearly 8 years)
- **`pxf-archive` — confirmed zero hits** across all 3 identities
  (author, co-author, reviewer, plain-text). If the user has PXF
  contributions, they're under a different identity not yet found, or
  the expectation doesn't hold — don't assume the repo has contributions
  to find.

## Relationship to the `apache/cloudberry` 27-commit figure

**Resolved by direct SHA comparison**: all 27 commits found earlier under
`repo:apache/cloudberry author:xinzweb` are an **exact subset** of the 34
unique `xinzweb`-authored commits above (27/27 SHAs match, 0 unique to
`apache/cloudberry` only) — expected, since Cloudberry's donated history
traces back to `gpdb-archive`. **Not additive** — don't add 27 to 238.

## Work log

- [x] Paginated past the 100-result cap for `xzhang@pivotal.io` (181 raw
      across 2 pages) and confirmed `Co-authored-by`/`Reviewed-by` sets
      (45 and 4, both under the cap, no pagination needed)
- [x] Spot-checked `zhxin@vmware.com` commit content — see identity
      section above
- [x] Checked for a 4th identity — none found (variants tried above)
- [x] Rewrote `project/cloudberry/self-assessment.md`'s "Legacy
      contribution" section with the final deduplicated numbers
- [x] Verified the 27-vs-238 relationship by direct SHA comparison — see
      section above
- [x] Presentation: summarized by identity/repo/era in
      `self-assessment.md`, this file holds the full reproducible
      methodology and raw numbers; no commit-by-commit list embedded
      anywhere

## Closed (2026-08-11)

Shipped in PR (this branch, `t20260810-367141-catalog`). All scoping
questions from the original "Remaining work" list resolved with evidence
(SHA-level dedup, SHA-level subset proof for the 27-commit figure,
content spot-checks, identity-variant sweep). `project/cloudberry/self-assessment.md`
updated with the final numbers. No follow-up tasks filed — the `pxf-archive`
zero-hit finding is noted as a flag, not something actionable without new
information from the user.

## Skills invoked

- TDD (`superpowers:test-driven-development`): no — docs-class (no code,
  only markdown/task-file content)
- Verification (`superpowers:verification-before-completion`): not
  available in this environment (not installed) — applied the underlying
  discipline manually: every numeric claim re-derived from a fresh `gh
  api search/commits` query and cross-checked by direct SHA comparison
  before being written down (see the dedup and 27-vs-238 sections above)
- Systematic debugging (`superpowers:systematic-debugging`): no — no
  stuck points, this was research/query work, not debugging
- Receiving code review (`superpowers:receiving-code-review`): not
  available in this environment (not installed) — no review comments to
  address on this PR (docs-only, self-authored research)
