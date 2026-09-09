---
status: Review
scheduled: 2026-08-31
estimation: 2h
source: T20260810-723411's "Pick at least one real item" list (issue #726 flagged "Not attempted this session") + this conversation, 2026-08-27/28
related: T20260810-723411
target-repo: apache/cloudberry
description: Fix apache/cloudberry#726 (gp_matview_aux.mvname schema confusion) — PR opened, CI has 4 unrelated failures under investigation
claimed_by: Shines-Laptop.local:/Users/xlj/workspace/xinzweb/apache-skills
---

# T20260828-134911: Fix apache/cloudberry#726 — gp_matview_aux.mvname schema confusion

## TLDR

- **Type**: bug
- **Problem**: `gp_matview_aux.mvname` is populated from a bare, non-schema-qualified
  relation name, so two materialized views of the same name in different
  schemas produce identical, indistinguishable `mvname` values.
- **Solution**: additive only. Add a new `gp_matviews` view — modeled on
  Postgres's own `pg_matviews` — that live-joins `gp_matview_aux` →
  `pg_class` → `pg_namespace` for a correctly schema-qualified name.
  `gp_matview_aux.mvname` itself is left completely unchanged (still
  populated, still synced on rename via the existing `mvaux_rename()`)
  and marked deprecated via `COMMENT ON COLUMN`, pointing at
  `gp_matviews`.
- **Status**: [apache/cloudberry#1970](https://github.com/apache/cloudberry/pull/1970)
  open since 2026-09-07. CI has 4 failing jobs (`pax-ic-isolation2-opt-on`,
  `ic-resgroup-v2`, two `ic-recovery` variants) — none touch matview code;
  investigation (see `## Test plan`) points to pre-existing environment
  flakiness, not this patch. `ic-cbdb-parallel` (the job that runs
  `matview_data.sql`, the test this patch actually adds) passed on every
  platform. Awaiting resolution of the CI question and maintainer review.

## Problem

- GitHub issue [apache/cloudberry#726](https://github.com/apache/cloudberry/issues/726)
  ("mvname column in gp_matview_aux may be confused"), filed 2024-11-22 by
  avamingli, labeled `type: Enhancement` + `good first issue`, still `OPEN`
  and unfixed on `main` as of 2026-08-27 (verified via `gh api`).
- Root cause: `src/backend/catalog/gp_matview_aux.c:253`, inside
  `InsertMatviewAuxEntry()`: `namestrcpy(&mvname, get_rel_name(mvoid));` —
  `get_rel_name()` returns only the bare relation name, never
  schema-qualified. The same bare-name write happens again on rename, in
  `mvaux_rename()` (`gp_matview_aux.c:699`, called from
  `RenameRelation()` in `tablecmds.c:4681` — this specific call site was
  missed by GitHub's own code-search API and only found by grepping the
  full 24k-line file directly).
- Introduced in [PR #720](https://github.com/apache/cloudberry/pull/720)
  ("Fix REFRESH fast path", merged 2024-12-02); flagged the same day in
  that PR's own review by @yjhnupt
  (`https://github.com/apache/cloudberry/pull/720#discussion_r1851410975`):
  *"mvname without schema, maybe same `mvname` cause confused."* A project
  member (@yjhjstz) suggested *"An easy way is just add schema"* — the
  issue was filed as a tracked follow-up but never actioned; it sat
  assigned-to-the-author-via-triage-bot but dormant for ~20 months,
  including through a stretch where the same author shipped 5-6 other PRs
  on this exact subsystem without touching this ticket.

## Context

- **`mvname` is genuinely dead weight, not load-bearing**: exhaustive
  local grep (not just GitHub's code-search API, which is confirmed
  incomplete — see Root cause above) found **zero** C code anywhere that
  reads `Form_gp_matview_aux->mvname`. AQUMV's rewrite matcher
  (`src/backend/optimizer/plan/aqumv.c`) matches by `mvoid` + parsed
  `Query` structure, never by name. Every catalog lookup goes through the
  `MVAUXOID` syscache, keyed on `mvoid`
  (`src/backend/utils/cache/syscache.c:791-796`). The only real consumers
  of `mvname` were direct SQL against the catalog — ~121 regression-test
  assertions across `src/test/regress/sql/{matview_data,aqumv}.sql` +
  duplicates in `contrib/pax_storage/` and `src/test/singlenode_regress/`
  — none of which ever exercised two same-named matviews in different
  schemas (confirmed by grep; this is exactly why the bug shipped
  unnoticed).
- **`mvname` is `NameData` (NAMEDATALEN=64, 63 usable bytes)** — the
  maintainer's suggested "just add schema" fix, read literally as
  prefixing `schema.name` into this same column, would silently truncate
  (and could re-collide) for long identifiers. This is why the chosen fix
  adds a separate, always-correct `mvschema` column via a view instead of
  reusing the constrained field.
- **Community norm confirmed**: apache/cloudberry has no formal
  claim-before-code process (checked `CONTRIBUTING.md` +
  `cloudberry.apache.org/contribute/code`); a `good first issue` with a
  20-month-dormant assignee is normal to pick up, courtesy comment
  recommended but not required.
- **Build/validation environment**: official docs support Rocky Linux
  8+/Ubuntu 20.04+ only (macOS build support dropped from current 2.x
  docs). Validated instead via `Synx-Data-Labs/2026-cfp-coc-asia`
  (Colima + Docker, arm64) — `make dist CLOUDBERRY_LOCAL_SRC=<patched
  checkout> CLOUDBERRY_REF=<branch>` builds Cloudberry core from a local
  checkout using a cached from-source GCC toolchain image, `make cluster`
  stands up a real 6-segment MPP demo cluster. Two environment gaps found
  and worked around (unrelated to this patch): the cached `coc-build:rocky8`
  image lacked `libicu-devel` (current `main` needs ICU; the pinned
  `2.1.0-incubating` release this repo defaults to didn't), and
  `make dist BUILD_IMAGE=...` silently clobbers a hand-patched image
  sharing that tag name (the `image:` Makefile target unconditionally
  rebuilds it) — worked around by invoking the underlying `docker run`
  directly instead of through `make`.
- **Colima on this host now runs off the external drive**
  (`/Volumes/1TB20260908`, `~/.colima` symlinked there) after an earlier
  internal-disk-space exhaustion — see `.claude/skills/cloudberry-ic-colima`
  (once written) for the full local-CI-repro playbook and its gotchas
  (native arm64 image required, correct container flags for cgroup v2
  visibility, exact CI-matching `make` targets per job).

## Solution

- **New view** — `src/backend/catalog/system_views.sql`, placed directly
  after `pg_matviews` (same file, same pattern):

  ```sql
  CREATE VIEW gp_matviews AS
      SELECT
          A.mvoid,
          N.nspname AS mvschema,
          C.relname AS mvname,
          A.has_foreign,
          A.datastatus
      FROM gp_matview_aux A
           JOIN pg_class C ON (C.oid = A.mvoid)
           LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace);

  COMMENT ON VIEW gp_matviews IS 'Schema-qualified view of gp_matview_aux, resolving mvname live from pg_class/pg_namespace instead of a stored copy. Prefer this over gp_matview_aux.mvname, which is not schema-qualified (see https://github.com/apache/cloudberry/issues/726).';

  COMMENT ON COLUMN gp_matview_aux.mvname IS 'Deprecated: bare, non-schema-qualified materialized view name, retained for backward compatibility only. Two materialized views with the same name in different schemas are indistinguishable via this column. Use gp_matviews.mvname (with gp_matviews.mvschema) instead. See https://github.com/apache/cloudberry/issues/726.';
  ```

- **`gp_matview_aux.mvname` is completely untouched**: still populated in
  `InsertMatviewAuxEntry()`, still synced on rename via the existing
  `mvaux_rename()`, index unchanged. Deprecation is marked purely via
  `COMMENT ON COLUMN` — there is no catalog-level "deprecated" flag in
  Postgres/Cloudberry; `COMMENT ON` (queryable via `col_description()` /
  `\d+`), a code comment, and the PR/release-notes description are the
  standard mechanism.
- **`catversion.h`** bumped (`302609031`) — required whenever bootstrap
  catalog content changes (a new view here), independent of whether the
  change is additive or removes something.
- **Alternatives rejected**:
  - *Prefix schema into the existing `mvname` column* (the maintainer's
    literal "easy way" suggestion) — rejected for the NAMEDATALEN=64
    truncation/re-collision risk.
  - *Add a new stored/synced `mvschema` column* instead of a view —
    rejected: verified via `grep` that **zero** existing code syncs a
    matview's schema anywhere in `tablecmds.c`'s
    `AlterTableNamespace`/`SET SCHEMA` path (nothing needed to, since
    `mvname` never tracked schema) — a new synced column would need that
    sync code added from scratch, and if ever missed, would go stale the
    same way `mvname` already does. A live-resolved view cannot go stale
    by construction.
  - *Remove `mvname` entirely* — rejected as unnecessarily breaking for
    an undocumented-but-real catalog column with unknown external
    direct-SQL consumers, when the additive form fixes the same bug with
    a smaller, non-breaking diff.
  - *Extend `pg_matviews` itself* rather than adding a new `gp_matviews`
    view — rejected to avoid changing a name/column-set contract that
    external pg-ecosystem tooling may depend on being vanilla-Postgres-
    compatible; Cloudberry already has an established pattern of parallel
    `gp_*` views alongside `pg_*` ones for exactly this reason.

## Test plan

All items below verified live against the current, additive-only design
(commits `cf5a0a9e` → `1fae8eb5`), on a real 6-segment `gpdemo` cluster
built from this branch:

- [x] Compiles clean with `-Werror` — real Docker build (`make dist`)
      completed cleanly against `apache/cloudberry@867c6a14` + this patch;
      grepped the full build log for `error:`/`undefined reference`/
      `collect2:`/`ld:` — zero hits
- [x] Catalog bootstraps correctly — `gpinitsystem`/`gpdemo` succeeded on
      the reprovisioned cluster; live-confirmed `SELECT catalog_version_no
      FROM pg_control_system();` → `302609031`, matching `catversion.h`
- [x] **The actual fix, proven live**: `mv0` created in two schemas —
      `gp_matview_aux.mvname` alone shows two indistinguishable
      `mv0 | u` rows (the deprecated, unchanged, still-buggy-for-direct-
      queriers behavior); `gp_matviews` correctly distinguishes them via
      `mvschema` (`mv_s1 | mv0 | f | u` / `mv_s2 | mv0 | f | u`) — the
      exact #726 scenario, now fixable by switching to the new view
- [x] `ALTER MATERIALIZED VIEW ... RENAME` verified live — `gp_matviews`
      reflects the new name immediately (resolved live, not synced); the
      other schema's `mv0` is unaffected
- [x] `COMMENT ON COLUMN`/`COMMENT ON VIEW` deprecation notices verified
      live queryable via `col_description()`/`obj_description()` — exact
      text confirmed present on the running cluster, not just in source
- [x] `src/test/regress/sql/matview_data.sql` run against the live
      cluster; new schema-collision test block's expected output spliced
      into `matview_data.out` at its exact insertion point — confirmed via
      diff against the pristine upstream file that this is a **pure
      addition** (66 insertions, 0 deletions); the rest of the file's
      diff (pre-existing 2-vs-3-segment topology noise in unrelated
      sections) is untouched/unclaimed, as before
- [x] `src/test/regress/sql/aqumv.sql` — not touched by this design; live
      diff against its checked-in `.out` confirmed via `grep` to contain
      **zero** `gp_matview`/`mvname`/`mvschema` hits — 100% pre-existing
      drift (GUC-ordering in `EXPLAIN VERBOSE`, new `DISTRIBUTED BY`
      notices, topology Motion labels), unrelated to this patch and
      correctly left unmodified
- [x] `misc_sanity.out` needs zero changes — confirmed by an actual live
      diff: byte-identical, zero-byte diff
- [x] `contrib/pax_storage/src/test/regress/sql/aqumv.sql` and
      `src/test/singlenode_regress/sql/matview_data.sql` — not touched by
      this design; no action needed
- [x] `mvn apache-rat:check` — `Unapproved: 0, unknown: 0` on both the
      final commit and after the `.out` file addition
- [x] Live-cluster validation on the official Rocky Linux 8+/Ubuntu
      20.04+ toolchain — real apache/cloudberry CI on PR #1970:
      `ic-cbdb-parallel` (runs `src/test/regress`, where `matview_data.sql`
      lives) passed on Rocky 8, Rocky 10, and Debian/Ubuntu.
- [ ] **CI has 4 unrelated failures under investigation**:
      `pax-ic-isolation2-opt-on` (segfault in `autovacuum-analyze`,
      `contrib/pax_storage`), `ic-resgroup-v2` (`resgroup_cpu_max_percent`),
      and two `ic-recovery` jobs (`t/019_replslot_limit.pl` subtests 8-9).
      None touch matview code. Evidence gathered so far:
      - `main` itself independently failed `ic-resgroup-v2` — the exact
        same job — on 2026-09-07, with no relation to this PR. It also
        failed `pax-ic-isolation2-opt-off` that day, which is a sibling
        variant of our failing `pax-ic-isolation2-opt-on` (same
        `contrib/pax_storage` isolation2 suite, opposite optimizer GUC
        setting) rather than the identical job — weaker evidence, but
        still points at that test suite being flaky on `main` in
        general, independent of this PR.
      - Local reproduction of the exact CI-failing `autovacuum-analyze`
        test (same scope, same PR commit `f4a5556`) **passed cleanly**
        (56s, no crash) — did not reproduce CI's segfault.
      - `ic-resgroup-v2` could not be locally reproduced: a real
        environment incompatibility (cgroup v2 delegation fails under
        this nested-VM setup, `cgroup.c:341`) blocks the test mechanism
        itself, unrelated to the patch (which touches zero resgroup
        code).
      - `ic-recovery` not cleanly locally reproduced (run was confounded
        by a concurrent cluster rebuild); no direct `main`-branch
        corroboration found in the CI history sampled, though the patch
        touches zero replication/recovery code.
      - Conclusion pending: strong evidence these are pre-existing/
        environment flakiness, not caused by this patch, but not yet
        formally resolved on the PR (comment + possible re-run request).

## Done criteria

- [x] Root cause identified and cited to `file:line` + the exact PR review
      comment that first flagged it
- [x] Fix designed, with alternatives-rejected reasoning, per maintainer +
      user input
- [x] Patch written and compiles clean (`-Werror`) — verified live
- [x] Fix proven correct on a live cluster (not just claimed) — verified
      live, see `## Test plan`
- [x] New regression test added and actually run against a live cluster,
      expected output captured from the real transcript
- [x] Branch pushed to a durable location before each live-cluster
      rebuild — see `## Where the work lives`
- [x] `cloudberry-license-check` run for real (`mvn apache-rat:check`) —
      `Unapproved: 0`
- [x] `cloudberry-ai-disclosure` checklist walked (§2.a–f) — AI-disclosure
      checkbox ticked in the PR
- [x] `cloudberry-pr-checklist` walked; PR title/body drafted
- [x] PR opened against `apache/cloudberry` — [#1970](https://github.com/apache/cloudberry/pull/1970)
- [ ] CI's 4 unrelated-looking failures resolved (re-run, comment, or
      accepted as pre-existing — see `## Test plan`)
- [ ] Maintainer review addressed

## Root cause

- See `## Problem` above — `namestrcpy(&mvname, get_rel_name(mvoid))` at
  `src/backend/catalog/gp_matview_aux.c:253` (and the same pattern in
  `mvaux_rename()`, unchanged by the current design) never
  schema-qualifies. Introduced in merged [PR #720](https://github.com/apache/cloudberry/pull/720)
  (2024-12-02) — a genuine oversight, not a deliberate design choice: the
  same PR's own reviewer flagged it same-day, before merge, but the
  follow-up (this issue) sat unactioned for ~20 months.

## Repo file references

All paths relative to the `apache/cloudberry` repo root (not this hub
repo). Base commit `867c6a14` (`main`).

4 files changed, +117/−1:

| File | Change | Purpose |
| --- | --- | --- |
| `src/include/catalog/catversion.h` | ±1 line | catversion bump (new view added to bootstrap catalog content) |
| `src/backend/catalog/system_views.sql` | +15 lines | new `gp_matviews` view + `COMMENT ON VIEW`/`COMMENT ON COLUMN` deprecation notice on `gp_matview_aux.mvname` |
| `src/test/regress/sql/matview_data.sql` | +35 lines | new self-contained schema-collision test (nothing else in this file touched) |
| `src/test/regress/expected/matview_data.out` | +66 lines | real captured output for the new test, spliced in at the exact insertion point — confirmed a pure addition vs. upstream |

Not touched by this design: `gp_matview_aux.h`, `gp_matview_aux.c`,
`tablecmds.c`, `aqumv.sql`/`aqumv.out` (both copies),
`singlenode_regress/matview_data.sql`/`.out`.

## Cross-repo work

- Implementation: [apache/cloudberry#1970](https://github.com/apache/cloudberry/pull/1970)
  (`xinzweb:t726-remove-mvname-column`) — opened 2026-09-07. Requesting
  review from the `cloudberry-committers` GitHub team was left unchecked
  in the PR body: outside contributors typically can't request a team as
  reviewer without write access to the repo (untested here — noting it
  rather than claiming it was done).
- Live-cluster validation container (`t726-cluster`, local Docker) torn
  down 2026-09-07 after the PR opened successfully.

## Where the work lives

- **Durable**: `xinzweb/cloudberrydb` (fork of `apache/cloudberry`),
  branch `t726-remove-mvname-column`, HEAD `1fae8eb5`, based on
  `apache/cloudberry@867c6a14`.
- An earlier, separately-implemented version of this fix (design:
  removing `mvname` entirely rather than the current additive approach)
  was lost to an ephemeral-clone `.git`-hollowing incident before being
  pushed anywhere durable — root-cause + prevention tracked as
  `synx-skills` [T20260902-167059](https://github.com/Synx-Data-Labs/synx-skills/pull/254).
  No work is currently at risk; the design was fully recoverable from
  this file's own exact diffs and reimplemented from scratch, pushed
  eagerly this time.
- No ephemeral working clones currently active for this task.

## Skills invoked

- TDD (`superpowers:test-driven-development`): skill not present in this
  environment; followed the practice manually against a real compiler +
  live cluster instead of a local unit-test harness — ran the actual
  regression test, found a real bug in it, fixed it, reran
- Verification (`superpowers:verification-before-completion`): skill not
  present; self-verified via live Docker build + live cluster + live
  regression-test runs at every step rather than static review alone
- Systematic debugging (`superpowers:systematic-debugging`): yes — build
  failures (ICU, image-clobbering) and CI-failure triage were each
  diagnosed from the actual error message to a specific root cause before
  being fixed, not trial-and-error
- Receiving code review (`superpowers:receiving-code-review`): n/a — no
  maintainer review comments yet
- `cloudberry-ai-disclosure`: walked the §2 pre-PR checklist against this
  change — flagged as substantial AI generation touching a high-risk
  (catalog) area, per the skill's own guidance
- `cloudberry-license-check`: run for real (`mvn apache-rat:check`) —
  `Unapproved: 0`
