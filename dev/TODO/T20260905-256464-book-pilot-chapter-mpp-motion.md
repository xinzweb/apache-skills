---
status: Open
estimation: 2d
source: this conversation, 2026-09-05
related: T20260828-134911
---

# T20260905-256464: Write pilot book chapter — MPP query execution & Motion nodes

## Problem

- **Type**: feature
- No internals-level documentation of Apache Cloudberry's MPP query
  execution model exists in this repo, or (as far as known) in an
  accessible book form — Cloudberry's own docs site
  (cloudberry.apache.org) covers usage, not internals.
- Goal: a personal reference/learning book, built directly from the
  open-source Cloudberry codebase, covering what's genuinely distinctive
  about its architecture — starting with **one pilot chapter** before
  committing to a full book-length project (a whole book is far bigger
  than this backlog's `15m`–`1w` estimation scale; scope decided
  2026-09-05 to pilot one chapter first and file the rest as follow-up
  tasks only if the format/depth proves out).
- **Style reference, not a structural template**: loosely inspired by
  [interdb.jp/pg](https://www.interdb.jp/pg/) ("The Internals of
  PostgreSQL") as a quality/depth bar — explicitly **not** mirroring its
  chapter breakdown, since Cloudberry's own chapter structure should come
  from what's actually distinctive about its codebase (MPP execution,
  distribution, segment coordination), not from re-deriving Postgres
  internals chapters Cloudberry mostly inherits unchanged.
- **Pilot topic**: MPP query execution and `Motion` nodes — how a query
  plan gets sliced and executed across segments (`Gather`/`Redistribute`/
  `Broadcast` Motion, the coordinator/segment split, `gp_segment_configuration`'s
  role). Chosen as the most distinctive, highest-payoff Cloudberry-specific
  subsystem, and one that ties directly to real, capturable `EXPLAIN`
  output rather than requiring only static code reading.
- **Location**: a new `book/` directory in this repo (`apache-skills`).
- Done looks like: a chapter-length markdown document in `book/`, citing
  real `file:line` references from the `apache/cloudberry` source (not
  paraphrased from memory), with at least one worked example using real,
  live-captured `EXPLAIN` output (not fabricated) — reviewed by the user
  to decide whether to continue with further chapters as follow-up tasks.

## Context

- Live-cluster infrastructure (Docker/Colima toolchain image, a
  `gpdemo` 6-segment cluster) already exists from `T20260828-134911`'s
  work and can likely be reused/extended to capture real `EXPLAIN`
  output for this chapter's worked examples, rather than standing up a
  build environment from scratch.
- Personal reference project — no external audience, no Cloudberry
  contribution-process gates (`cloudberry-license-check`,
  `cloudberry-ai-disclosure`, `cloudberry-pr-checklist`) apply, since
  nothing is being submitted upstream.
