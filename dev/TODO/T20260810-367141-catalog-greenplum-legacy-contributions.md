---
status: Coding
estimation: 4h
priority: Medium
source: conversation 2026-08-10/11 — user asked for a thorough search of greenplum-db org history
description: Fully catalog Shine Zhang's Greenplum-era contributions across greenplum-db repos for project/cloudberry/self-assessment.md
claimed_by: Shines-Laptop.local:/Users/xlj/workspace/xinzweb/apache-skills
scheduled: 2026-08-10
---

# T20260810-367141: Catalog Greenplum-era legacy contributions

Scoping search done (2026-08-10/11, via `gh api search/commits`); this
task is the full catalog + write-up, not the discovery.

## Confirmed identities (user confirmed both corporate emails are theirs)

- GitHub `xinzweb` — direct author, 48 commits
- `xzhang@pivotal.io` — direct author, 181 commits (Pivotal era).
  Verified as the same person: the merge commit for PR "xinzweb/enable_ccache"
  (gporca-archive `b53c1acd`) has this email as the second parent's author —
  i.e. the actual PR branch, pushed from the `xinzweb` GitHub account, used
  this email for its commits.
- `zhxin@vmware.com` — direct author, 24 commits (VMware era, post-Pivotal
  acquisition) — user-confirmed, not independently proven the same rigorous
  way as the Pivotal email.

## Scoping numbers (2026-08-10/11, `org:greenplum-db`)

- Direct-author commits: 48 (`xinzweb`) + 181 (`xzhang@pivotal.io`) + 24
  (`zhxin@vmware.com`) = 253
- `Co-authored-by: Xin Zhang` credits: 45 total (28 pivotal.io, 15
  vmware.com, 2 xinzweb-noreply)
- `Reviewed-by: Xin Zhang` credits: 4 total (1 pivotal.io, 2 vmware.com, 1
  xinzweb-noreply)
- Repos touched: `gpdb-archive`, `gporca-archive`, `gp-xerces-archive`
  (not previously known to the user — surfaced by this search),
  `greenplum-database-release-archive`
- **`pxf-archive` — confirmed zero hits** across all 3 identities (author,
  co-author, reviewer, and plain-text search). If the user has PXF
  contributions, they're under a different identity not yet found, or the
  user is misremembering — don't assume the repo has contributions to find.
- Date range so far: 2016-01 through 2023-11 (nearly 8 years) — the
  `zhxin@vmware.com` work (2020, mostly RPM/Debian packaging and Concourse
  CI release engineering) is a materially different kind of contribution
  than the 2016-era ORCA/gpdb code fixes; worth describing as such, not
  flattening into one bucket.

## Remaining work

- [ ] Paginate past the 100-result search cap to get exact, complete repo
      breakdowns for `xzhang@pivotal.io` (181 total, only 100 enumerated
      so far) and confirm the `Reviewed-by`/`Co-authored-by` sets are
      fully captured too
- [ ] Spot-check a sample of the `zhxin@vmware.com` commits for content
      (not just titles) to characterize the nature of that work accurately
- [ ] Check for a 4th identity possibility: a plain `Shine Zhang <...>`
      form (not just `Xin Zhang`) — this search only covered name variants
      the user listed (Xin Zhang, Shine Zhang, Shin Zhang combined with
      known emails); "Shine Zhang" as an exact commit-author name returned
      0 in the initial scoping pass, worth one more pass by email domain
      alone (`*@pivotal.io`, `*@vmware.com`) filtered to first-name "Xin"
      in case of a name variant not yet tried
- [x] Rewrite `project/cloudberry/self-assessment.md`'s "Legacy
      contribution" section with the headline numbers from the scoping
      search — done in this same PR
- [ ] Verify whether the 27 `apache/cloudberry`-only commits are actually
      a subset of the 253 `org:greenplum-db` figure, or a separate count —
      `apache/cloudberry` lives in the `apache` GitHub org, not
      `greenplum-db`, so the org-wide search never covered it. Don't
      assume containment just because the donation carried Greenplum's
      git history; verify by SHA before stating it either way.
- [ ] Decide presentation: a full commit-by-commit list would be far too
      long for that file — summarize by repo/era/kind of work, link out to
      the actual `gh api search/commits` queries (reproducible) rather
      than embedding raw commit lists
