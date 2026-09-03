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
- **Solution**: remove `mvname` (and the now-dead `mvaux_rename()` sync
  function it existed solely for) from the catalog entirely; add a new
  `gp_matviews` convenience view — modeled on Postgres's own `pg_matviews`
  — that live-joins `pg_matview_aux` → `pg_class` → `pg_namespace` for a
  correctly schema-qualified name instead of a stale, denormalized copy.
- **Status (updated 2026-09-02)**: the 2026-08-27/28 session's design,
  patch, and live-cluster validation were never pushed and were lost when
  their ephemeral `/tmp` clones' `.git` silently hollowed out across a
  session boundary (see `## Where the work lives` — incident now tracked
  as `synx-skills` `T20260902-167059`, filed to fix the underlying
  ephemeral-clone gap). The design itself was fully recoverable from this
  file's own `## Solution` (exact diffs), so the catalog fix and
  mechanical test-file rename have been **reapplied from scratch** against
  current `apache/cloudberry@main` (`867c6a14`, not the original
  `eaf8e256`) and **pushed immediately** to a durable fork
  (`xinzweb/cloudberrydb`, branch `t726-remove-mvname-column`) — before
  starting the expensive live-cluster rebuild this time, per the lesson
  from the incident. Live-cluster validation is **not yet redone** — that
  and the `.out` expected-output regeneration are the remaining work.

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

- **Catalog change** — `src/include/catalog/gp_matview_aux.h`: removed the
  `NameData mvname` field and its `gp_matview_aux_mvname_index` (was
  already non-unique, so removing it doesn't affect any misc_sanity
  unique-index check). Bumped `CATALOG_VERSION_NO` in `catversion.h`
  (`302608271`, following this repo's `3yyymmddN` convention).
- **`src/backend/catalog/gp_matview_aux.c`**: removed the `mvname`
  population in `InsertMatviewAuxEntry()`; deleted `mvaux_rename()`
  entirely (its only purpose was keeping `mvname` in sync on rename — with
  the column gone, `ALTER MATERIALIZED VIEW ... RENAME` needs **zero**
  synchronization code, since the name is now always resolved live from
  `pg_class`). Removed the now-dead call site in
  `src/backend/commands/tablecmds.c:4681`.
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
  ```

- **Alternatives rejected**:
  - *Prefix schema into the existing `mvname` column* (the maintainer's
    literal "easy way" suggestion) — rejected for the NAMEDATALEN=64
    truncation/re-collision risk above.
  - *Fork `postgres-mcp`/`mcp-alchemy`* — not applicable here, that was
    T20260827-107079's decision space, not this one.
  - *Extend `pg_matviews` itself* rather than adding a new `gp_matviews`
    view — rejected to avoid changing a name/column-set contract that
    external pg-ecosystem tooling may depend on being vanilla-Postgres-
    compatible; Cloudberry already has an established pattern of parallel
    `gp_*` views alongside `pg_*` ones for exactly this reason.
  - *Remove `mvname` with no replacement view* — rejected per user
    direction: still need *some* way to get a matview's schema-qualified
    name without hand-writing the `pg_class`/`pg_namespace` join every
    time.

## Test plan

**Re-verification needed (2026-09-02 redo — the 2026-08-27/28 session's
live-cluster evidence below was lost with its ephemeral clone; the checks
themselves are unchanged, only the completed/pending status resets):**

- [ ] Compiles clean with `-Werror` against current `main` (867c6a14) —
      verify via real Docker build, not just static review
- [ ] Catalog bootstraps correctly — `gpinitsystem` confirms catversion
      `302609021` on a live 6-segment cluster
- [ ] **The actual fix, manually proven live**: `mv0` created in two
      different schemas shows as two distinct rows via
      `gp_matviews.mvschema` — the exact scenario issue #726 describes as
      broken. (Previously confirmed 2026-08-27 as `s1 | mv0 | f | u` /
      `s2 | mv0 | f | u`; re-confirm against the new schema-collision test
      added directly to `matview_data.sql` this time, not just ad hoc SQL)
- [ ] `ALTER MATERIALIZED VIEW ... RENAME` verified live — `gp_matviews`
      reflects the new name immediately with the sync code deleted
- [ ] `src/test/regress/sql/matview_data.sql` run against the live
      cluster; expected output regenerated from the actual live
      transcript, not hand-written
- [ ] `src/test/regress/sql/aqumv.sql`'s two `gp_matviews`-referencing
      queries captured live (previously: `normal_mv_t1 | e` and
      `datastatus = u` for `aqumv_ext_mv` — re-confirm, don't assume
      unchanged)
- [ ] `misc_sanity.out` needs **zero** changes — confirm both by static
      reasoning (the removed column was fixed-length/non-toastable, and
      its index was already non-unique, so neither existing sanity check
      ever listed it) and by an actual live diff (empty)
- [ ] `contrib/pax_storage/src/test/regress/sql/aqumv.sql` and
      `src/test/singlenode_regress/sql/matview_data.sql` — got the
      identical mechanical rename but **not independently live-tested**
      (this build didn't compile with `--enable-pax` or a single-node
      config) — external, unverified here, flag explicitly in the PR
      rather than claim tested
- [ ] `mvn apache-rat:check` (Apache RAT license-header audit) — not run
      (`mvn` unavailable in this environment); structurally should pass
      since every touched file is a modification of an already
      ASF-headers-compliant file, zero new files added — but this is an
      assumption, not a verified result; CI will run it as the
      authoritative gate on the real PR either way
- [ ] Live-cluster validation on the official Rocky Linux 8+/Ubuntu
      20.04+ toolchain (this session used an unofficial Docker
      arm64-portable build) — the real apache/cloudberry CI matrix is the
      authoritative confirmation once the PR is opened

## Done criteria

- [x] Root cause identified and cited to `file:line` + the exact PR review
      comment that first flagged it
- [x] Fix designed, with alternatives-rejected reasoning, per maintainer +
      user input during this session
- [x] Patch written (reapplied 2026-09-02 from this file's own design,
      against current `main`) — [ ] compiles clean (`-Werror`), not yet
      re-verified in the new clone
- [ ] Fix proven correct on a live cluster (not just claimed) — pending
      redo, see `## Test plan`
- [x] New regression test added (schema-collision test reapplied) — [ ]
      actually run against a live cluster, not yet redone
- [x] **Push the branch to a durable location** — done eagerly this time,
      *before* the live-cluster rebuild: `t726-remove-mvname-column`
      pushed to `xinzweb/cloudberrydb` (fork of `apache/cloudberry`),
      commits `dec16ab6` (catalog fix) → `c26383e9` (test rename), based
      on `apache/cloudberry@867c6a14`.
- [ ] `cloudberry-license-check` run for real (`mvn apache-rat:check`) —
      currently only reasoned about, not executed
- [ ] `cloudberry-pr-checklist` walked before opening
- [ ] PR opened against `apache/cloudberry`, referencing this task and
      issue #726, with the AI-disclosure checkbox ticked (substantial
      AI-drafted diff touching catalog code — high-risk area per
      Cloudberry's own `AGENTS.md.template`) and the honest caveats above
      (pax_storage/singlenode untested, RAT unrun, rules.out pre-existing
      staleness) stated in the PR body, not hidden
- [ ] Maintainer review addressed

## Root cause

- See `## Problem` above — `namestrcpy(&mvname, get_rel_name(mvoid))` at
  `src/backend/catalog/gp_matview_aux.c:253` (and the same pattern in
  `mvaux_rename()`, since deleted) never schema-qualifies. Introduced in
  merged [PR #720](https://github.com/apache/cloudberry/pull/720)
  (2024-12-02) — a genuine oversight, not a deliberate design choice: the
  same PR's own reviewer flagged it same-day, before merge, but the
  follow-up (this issue) sat unactioned for ~20 months.

## Repo file references

All paths relative to the `apache/cloudberry` repo root (not this hub
repo). Base commit `867c6a14` (`main`, fetched 2026-09-02 — supersedes the
original `eaf8e256`, lost with its clone; see `## Where the work lives`).

| File | Change | Purpose |
| --- | --- | --- |
| `src/include/catalog/gp_matview_aux.h` | −5 lines | remove `mvname` field + its index declaration + `mvaux_rename` prototype |
| `src/include/catalog/catversion.h` | ±1 line | catversion bump (schema change) |
| `src/backend/catalog/gp_matview_aux.c` | −44 lines | remove `mvname` population; delete `mvaux_rename()` entirely |
| `src/backend/commands/tablecmds.c` | −4 lines | remove the now-dead `mvaux_rename()` call site |
| `src/backend/catalog/system_views.sql` | +15 lines | new `gp_matviews` view |
| `src/test/regress/sql/matview_data.sql` | ~244 lines touched | mechanical `gp_matview_aux`→`gp_matviews` rename + new self-contained schema-collision test |
| `src/test/regress/expected/matview_data.out` | ~258 lines touched | same rename + real captured output for the new test |
| `src/test/regress/sql/aqumv.sql` + `expected/aqumv.out` | 4 lines each | same mechanical rename (2 queries) |
| `src/test/singlenode_regress/sql/matview_data.sql` + `expected/matview_data.out` | ~136 lines each | same mechanical rename — **not independently live-tested**, see Test plan |
| `contrib/pax_storage/src/test/regress/sql/aqumv.sql` + `expected/aqumv.out` | 4 lines each | same mechanical rename — **not independently live-tested**, see Test plan |

## Where the work lives

- **Durable (current)**: `xinzweb/cloudberrydb` (fork of `apache/cloudberry`),
  branch `t726-remove-mvname-column`, commits `dec16ab6` → `c26383e9`,
  based on `apache/cloudberry@867c6a14`. Pushed 2026-09-02, before the
  live-cluster rebuild — not after, per the incident below.
- Ephemeral working clone (this session): `/tmp/T20260828-134911-cloudberry726-target`.
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
