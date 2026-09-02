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
- **Status**: design, patch, and live-cluster validation are complete this
  session (2026-08-27/28). **Not yet pushed anywhere** — the two commits
  exist only in ephemeral local clones (see `## Repo file references` /
  `## Where the work lives` below). Pushing to a fork + opening the PR is
  the only remaining work.

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

- [x] Compiles clean with `-Werror` against current `main` (verified via
      real Docker build, not just static review)
- [x] Catalog bootstraps correctly — `gpinitsystem` confirms catversion
      `302608271` on a live 6-segment cluster
- [x] **The actual fix, manually proven live**: `mv0` created in two
      different schemas now shows as two distinct rows via
      `gp_matviews.mvschema` (`s1 | mv0 | f | u` and `s2 | mv0 | f | u`) —
      the exact scenario issue #726 describes as broken, confirmed fixed
- [x] `ALTER MATERIALIZED VIEW ... RENAME` verified live — `gp_matviews`
      reflects the new name immediately with the sync code deleted
- [x] `src/test/regress/sql/matview_data.sql` run against the live
      cluster — caught and fixed a **real bug in my own new test** (it
      referenced `t1`, a table already dropped earlier in the file at
      line 947); expected output regenerated from the actual live
      transcript, not hand-written. Remaining diff vs. the original
      capture is limited to pre-existing 2-segment-vs-3-segment cluster
      noise (non-deterministic row order on unordered `LIKE` queries,
      `Gather/Redistribute/Broadcast Motion` segment-count labels in an
      unrelated join-planning test section) — confirmed unrelated to this
      patch, not something this task fixes
- [x] `src/test/regress/sql/aqumv.sql`'s two `gp_matviews`-referencing
      queries verified byte-identical to the original capture
      (`normal_mv_t1 | e` and `datastatus = u` for `aqumv_ext_mv`)
- [x] `misc_sanity.out` needs **zero** changes — confirmed both by static
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
- [x] Patch written and compiles clean (`-Werror`)
- [x] Fix proven correct on a live cluster (not just claimed)
- [x] New regression test added, and — critically — actually run, catching
      a real bug in the test itself before it could have shipped broken
- [ ] **Push the branch to a durable location** — right now the two
      commits (`c9149a2c`, `cfb6c9cd` on branch `t726-remove-mvname-column`,
      based on `apache/cloudberry@eaf8e256`) exist **only** in ephemeral
      local clones that could be cleaned between sessions:
      `/private/tmp/claude-501/.../scratchpad/cloudberry` (canonical) and
      `/Users/xlj/tmp-t726-build/cloudberry` (build copy, in sync). Push
      to a fork before either gets swept, or the validated patch is lost
      and this task's evidence trail (above) becomes the only record.
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
repo). Base commit `eaf8e256` (`main`, fetched 2026-08-27).

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

- Canonical clone: `/private/tmp/claude-501/-Users-xlj-workspace-xinzweb-apache-skills/3cddcb20-c202-4811-bbe6-09b2f795df6f/scratchpad/cloudberry`,
  branch `t726-remove-mvname-column`, commits `c9149a2c` → `cfb6c9cd`.
- Build/validation copy (kept in sync, used for the live-cluster tests
  above): `/Users/xlj/tmp-t726-build/cloudberry`. Companion build tooling
  clone: `/Users/xlj/tmp-t726-build/2026-cfp-coc-asia`
  (`Synx-Data-Labs/2026-cfp-coc-asia`, unmodified).
- Both are ephemeral scratch locations — see the unpushed-branch Done
  criteria item above.

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
