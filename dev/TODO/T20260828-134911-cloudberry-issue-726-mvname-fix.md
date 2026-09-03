---
status: Coding
scheduled: 2026-08-31
estimation: 2h
source: T20260810-723411's "Pick at least one real item" list (issue #726 flagged "Not attempted this session") + this conversation, 2026-08-27/28
related: T20260810-723411
target-repo: apache/cloudberry
description: Fix apache/cloudberry#726 (gp_matview_aux.mvname schema confusion) — design, patch, and live validation done; not yet pushed/opened as a PR
claimed_by: Shines-Laptop.local:/Users/xlj/workspace/xinzweb/apache-skills
---

# T20260828-134911: Fix apache/cloudberry#726 — gp_matview_aux.mvname schema confusion

## TLDR

- **Type**: bug
- **Problem**: `gp_matview_aux.mvname` is populated from a bare, non-schema-qualified
  relation name, so two materialized views of the same name in different
  schemas produce identical, indistinguishable `mvname` values.
- **Solution (revised 2026-09-03 — see `## Status`)**: additive only. Add a
  new `gp_matviews` view — modeled on Postgres's own `pg_matviews` — that
  live-joins `gp_matview_aux` → `pg_class` → `pg_namespace` for a correctly
  schema-qualified name. `gp_matview_aux.mvname` itself is left completely
  unchanged (still populated, still synced on rename via the existing
  `mvaux_rename()`) and marked deprecated via `COMMENT ON COLUMN`, pointing
  at `gp_matviews`. The earlier design (remove `mvname` + `mvaux_rename()`
  entirely) was implemented and live-validated first, then reworked to this
  smaller, non-breaking shape after user review — see `## Status` for why.
- **Status (updated 2026-09-03)**: the 2026-08-27/28 session's design,
  patch, and live-cluster validation were never pushed and were lost when
  their ephemeral `/tmp` clones' `.git` silently hollowed out across a
  session boundary (see `## Where the work lives` — incident now tracked
  as `synx-skills` `T20260902-167059`, filed to fix the underlying
  ephemeral-clone gap). The design itself was fully recoverable from this
  file's own `## Solution` (exact diffs), so the catalog fix and
  mechanical test-file rename were **reapplied from scratch** against
  current `apache/cloudberry@main` (`867c6a14`) and **pushed immediately**
  to a durable fork (`xinzweb/cloudberrydb`, branch
  `t726-remove-mvname-column`) — before starting the live-cluster rebuild,
  per the lesson from the incident — then fully live-validated end to end
  (commit `bf918702`, see the now-superseded validation below).
- **Then reworked (2026-09-03), before opening the PR**: the user asked
  why this needed to be a breaking change instead of an additive fix, and
  pointed out `gp_matview_aux` is a real catalog table (not a view) — a
  plain column could be added to it. Investigated: a new stored/synced
  `mvschema` column would reproduce the exact bug class this issue is
  about (verified — `grep` found **zero** existing sync code for a
  matview's schema anywhere in `tablecmds.c`'s `AlterTableNamespace`/`SET
  SCHEMA` path, since `mvname` never tracked schema; a new synced column
  would need to add that from scratch and could go stale the same way).
  A live-resolved *view* avoids that permanently — so the view was kept,
  but the column-removal was dropped: `mvname`, `mvaux_rename()`, and its
  index are now **left completely untouched**, deprecated via
  `COMMENT ON COLUMN` instead of removed. Branch history was rewritten
  (safe — no PR was open yet) and re-validated live from scratch on the
  same already-provisioned cluster (much faster: no toolchain rebuild
  needed, just a recompile). See `## Test plan` for the current,
  superseding validation.

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

## Solution

**Current (additive-only, see `## Status` for the design history):**

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
  - *Add a new stored/synced `mvschema` column* instead of a view — this
    was the user's first alternative to weigh against the (now-superseded)
    removal approach. Rejected: verified via `grep` that **zero** existing
    code syncs a matview's schema anywhere in `tablecmds.c`'s
    `AlterTableNamespace`/`SET SCHEMA` path (nothing needed to, since
    `mvname` never tracked schema) — a new synced column would need that
    sync code added from scratch, and if ever missed, would go stale the
    same way `mvname` already does. A live-resolved view cannot go stale
    by construction.
  - *Remove `mvname` entirely* (the original 2026-08-27/28 design, fully
    implemented and live-validated before being reworked) — rejected on
    user review as unnecessarily breaking for an undocumented-but-real
    catalog column with unknown external direct-SQL consumers, when the
    additive form fixes the same bug with a smaller, non-breaking diff.
  - *Extend `pg_matviews` itself* rather than adding a new `gp_matviews`
    view — rejected to avoid changing a name/column-set contract that
    external pg-ecosystem tooling may depend on being vanilla-Postgres-
    compatible; Cloudberry already has an established pattern of parallel
    `gp_*` views alongside `pg_*` ones for exactly this reason.

## Test plan

**Re-verification needed (2026-09-02 redo — the 2026-08-27/28 session's
live-cluster evidence below was lost with its ephemeral clone; the checks
themselves are unchanged, only the completed/pending status resets):**

All items below verified live against the **current, additive-only**
design (commits `cf5a0a9e` → `1fae8eb5`), on a real 6-segment `gpdemo`
cluster built from this branch — 2026-09-03:

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
- [x] `src/test/regress/sql/aqumv.sql` — **not touched by this design**
      (only needed changes under the now-superseded remove-`mvname`
      approach); live diff against its checked-in `.out` confirmed via
      `grep` to contain **zero** `gp_matview`/`mvname`/`mvschema` hits —
      100% pre-existing drift (GUC-ordering in `EXPLAIN VERBOSE`, new
      `DISTRIBUTED BY` notices, topology Motion labels), unrelated to this
      patch and correctly left unmodified
- [x] `misc_sanity.out` needs **zero** changes — confirmed by an actual
      live diff: byte-identical, zero-byte diff
- [x] `contrib/pax_storage/src/test/regress/sql/aqumv.sql` and
      `src/test/singlenode_regress/sql/matview_data.sql` — **not touched**
      by this design (they only needed the mechanical rename under the
      now-superseded approach); no action needed, nothing to flag
- [x] `mvn apache-rat:check` — run for real (Homebrew Maven installed
      this session): `Unapproved: 0, unknown: 0` on both the final commit
      and after the `.out` file addition
- [ ] Live-cluster validation on the official Rocky Linux 8+/Ubuntu
      20.04+ toolchain (this session used an unofficial Docker
      arm64-portable build) — the real apache/cloudberry CI matrix is the
      authoritative confirmation once the PR is opened

## Done criteria

- [x] Root cause identified and cited to `file:line` + the exact PR review
      comment that first flagged it
- [x] Fix designed, with alternatives-rejected reasoning, per maintainer +
      user input during this session (twice — see `## Status`)
- [x] Patch written and compiles clean (`-Werror`) — verified live
- [x] Fix proven correct on a live cluster (not just claimed) — verified
      live, see `## Test plan`
- [x] New regression test added and actually run against a live cluster,
      expected output captured from the real transcript
- [x] **Push the branch to a durable location** — done eagerly, *before*
      each live-cluster rebuild: `t726-remove-mvname-column` on
      `xinzweb/cloudberrydb` (fork of `apache/cloudberry`), current HEAD
      `1fae8eb5` (history rewritten once, pre-PR, when the design changed
      — see `## Status`), based on `apache/cloudberry@867c6a14`.
- [x] `cloudberry-license-check` run for real (`mvn apache-rat:check`) —
      `Unapproved: 0`
- [x] `cloudberry-ai-disclosure` checklist walked (§2.a–f) — AI-disclosure
      checkbox will be ticked in the PR
- [x] `cloudberry-pr-checklist` walked; PR title/body drafted
- [ ] PR opened against `apache/cloudberry` — **pending final user
      approval of the revised (additive-only) PR body** before `gh pr
      create` is run
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
repo). Base commit `867c6a14` (`main`, fetched 2026-09-02 — supersedes the
original `eaf8e256`, lost with its clone; see `## Where the work lives`).

Current (additive-only) design — 3 files, +117/−1:

| File | Change | Purpose |
| --- | --- | --- |
| `src/include/catalog/catversion.h` | ±1 line | catversion bump (new view added to bootstrap catalog content) |
| `src/backend/catalog/system_views.sql` | +15 lines | new `gp_matviews` view + `COMMENT ON VIEW`/`COMMENT ON COLUMN` deprecation notice on `gp_matview_aux.mvname` |
| `src/test/regress/sql/matview_data.sql` | +35 lines | new self-contained schema-collision test (nothing else in this file touched) |
| `src/test/regress/expected/matview_data.out` | +66 lines | real captured output for the new test, spliced in at the exact insertion point — confirmed a pure addition vs. upstream |

Not touched by the current design (all touched under the now-superseded
remove-`mvname` approach — see `## Status`): `gp_matview_aux.h`,
`gp_matview_aux.c`, `tablecmds.c`, `aqumv.sql`/`aqumv.out` (both copies),
`singlenode_regress/matview_data.sql`/`.out`.

## Where the work lives

- **Durable (current)**: `xinzweb/cloudberrydb` (fork of `apache/cloudberry`),
  branch `t726-remove-mvname-column`, HEAD `1fae8eb5` (`cf5a0a9e` the
  additive-only rework + `1fae8eb5` its `.out` capture), based on
  `apache/cloudberry@867c6a14`. History was rewritten once, pre-PR (safe —
  no PR was open yet), when the design changed from removal to additive —
  the superseded commits (`dec16ab6`→`bf918702`, fully implemented and
  live-validated before being reworked) are only in the reflog now, not on
  any remote.
- Ephemeral working clone (this session): `/tmp/T20260828-134911-cloudberry726-target`.
- Live demo cluster (this session, for re-validation after the rework):
  Docker container `t726-cluster` on this host, built from the current
  HEAD — still running as of this checkpoint, not yet torn down.
- **2026-08-27/28 originals — confirmed unrecoverable (2026-09-02)**: the
  canonical scratch clone (`/private/tmp/claude-501/.../scratchpad/cloudberry`)
  and its build/validation copy (moved by the user to
  `/tmp/tmp-t726-build/cloudberry`, companion tooling clone
  `/tmp/tmp-t726-build/2026-cfp-coc-asia`) both had `.git` silently
  hollowed out (0 objects/refs/logs) despite the directory tree surviving
  — the two original commits (`c9149a2c`, `cfb6c9cd`) and all live-cluster
  test evidence are gone. Root-cause + prevention now tracked as
  `synx-skills` [T20260902-167059](https://github.com/Synx-Data-Labs/synx-skills/pull/254).

## Skills invoked

- TDD (`superpowers:test-driven-development`): skill not present in this
  environment; followed the practice manually against a real compiler +
  live cluster instead of a local unit-test harness (this is C/catalog
  code, not the Python MCP adapter T20260827-107079 could unit-test) —
  ran the actual regression test, found a real bug in it, fixed it, reran
- Verification (`superpowers:verification-before-completion`): skill not
  present; self-verified via live Docker build + live cluster + live
  regression-test runs at every step rather than static review alone —
  see `## Test plan`'s repeated "not just claimed"/"confirmed both by
  static reasoning and by" language
- Systematic debugging (`superpowers:systematic-debugging`): yes — the
  `t1`-already-dropped test failure and the ICU/image-clobbering build
  failures were each diagnosed from the actual error message to a
  specific root cause before being fixed, not trial-and-error
- Receiving code review (`superpowers:receiving-code-review`): n/a — no
  PR opened yet
- `cloudberry-ai-disclosure`: walked the §2 pre-PR checklist against this
  change (see `## Test plan`/`## Done criteria`) — flagged as
  substantial AI generation touching a high-risk (catalog) area, per
  the skill's own guidance
- `cloudberry-license-check`: read, not executed (`mvn` unavailable) — see
  `## Done criteria`
