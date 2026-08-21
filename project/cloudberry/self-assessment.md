# Apache Cloudberry — Self-Assessment & Level-Up Log

A living character sheet, not a static report — update it as you act.
Grounded in real data pulled 2026-08-10 (Gmail search + `gh` CLI against
`apache/cloudberry`), not assumptions. See `career-path.md` for the ladder
this builds on, and `dev/guidelines.md`'s Content & Privacy Guidelines
before adding anything here.

**The rule that keeps this honest**: XP and levels below track *engagement*,
not *governance status*. Nothing here promotes you. Stage/Title changes
still require a real `private@` nomination and vote per
`cloudberry-committer-onboarding` — the game motivates the work, it doesn't
replace the community that decides on it.

---

## Character sheet

| | |
|---|---|
| **Name** | Shine Zhang (`xinzweb`) |
| **Class** | PPMC Member, Apache Cloudberry (Incubating) |
| **Title Level** | 4 — PPMC Member *(real, doesn't decay; founding-member grant, see Legacy Contribution)* |
| **Legacy Bonus** | 238 distinct commits (209 direct-author + 25 co-author-only + 4 reviewer-only, deduplicated by SHA), 2016-2023 (Greenplum era, 3 confirmed identities — see below) |
| **Activity Streak** | 1 week *(2026-08-21 — Quest 0 + Quest 2 done)* |
| **XP** | 25 *(Quest 0: +5, Quest 2: +20 — see Level-up log)* |
| **Next Title Level** | N/A upward from PPMC without a project-wide event (graduation) — see `career-path.md`'s foundation-wide track (ASF Member) for the next *personal* tier instead |

---

## Findings (why Activity Streak starts at 0)

Pulled from Gmail (search across `dev@`/`private@`/`commits@cloudberry.apache.org`)
and cross-checked against `gh` — not guessed:

- **Onboarding is real and complete.** ICLA sent 2024-10-19, acknowledged
  by the ASF Secretary the same day. Apache ID correction handled via
  `private@cloudberry.apache.org` by 2024-10-23. This part of the ladder is
  solidly behind you.
- **No confirmed original post to `dev@` or `private@` since then.** A
  `from:me` search against both lists returns only that October 2024 ICLA
  thread as an unambiguous self-authored message. If you've posted since,
  it isn't surfacing in this mailbox search — worth a manual check, but
  don't assume it's there.
- **The Cloudberry-specific lists have gone quiet in this inbox — but
  `general@incubator.apache.org` hasn't.** Last `dev@` message: the 2.1.0
  release announcement, 2026-04-14. Last `private@` message: a committer
  nomination thread, ~2026-02-04. Meanwhile `general@incubator.apache.org`
  has multiple threads *every single day* through 2026-08-10. Mail delivery
  clearly still works — so either (a) the `dev@`/`private@`/`commits@`
  subscriptions themselves lapsed, or (b) traffic dropped off, or (c) it's
  landing somewhere in this mailbox that wasn't searched. **This is the
  actual first quest below, not a formality.**
- **Real governance texture, for calibration**: committer nominations run
  in visible clusters on `private@` (e.g. three separate `[DISCUSS] ... for
  Cloudberry Committer` threads on 2026-02-04 alone); binding votes look
  like a plain `+1`/`-1` reply (e.g. Ed Espino: *"No. 1 for my vote
  (binding)."* on the 2024-11-11 logo thread); Ed Espino's own ASF Member
  invitation was announced on `dev@` 2025-03-07 — the foundation-wide track
  in `career-path.md` isn't abstract, people in this exact project are on
  it.

---

## Legacy contribution (Greenplum era, 2016-2023)

Apache Cloudberry's codebase is derived from open-source Greenplum
Database, and the donation carried Greenplum's git history along with
it — so 27 commits under `author:xinzweb` predate the ASF project
entirely but are literally still in `apache/cloudberry`'s `git log`
today (`gh api search/commits -f q='repo:apache/cloudberry
author:xinzweb'`), 2016-01 through 2017-11.

A 2026-08-10/11 search across the whole `greenplum-db` GitHub org (`gh
api search/commits`, full methodology and raw numbers in
`dev/JOURNAL/2026-08-11-T20260810-367141-catalog-greenplum-legacy-contributions.md`)
found a much larger body of work under
**three confirmed identities**, all the same person (user-confirmed).
Numbers below are **deduplicated by SHA** — the same commit can appear
under more than one repo because several `greenplum-db` repos share
donated/forked history, so a naive per-identity search count
double-counts:

- GitHub `xinzweb` — **34 unique commits**
- `xzhang@pivotal.io` (Pivotal era) — **151 unique commits**.
  Independently verified, not just name-matched: the merge commit for a
  PR literally named `xinzweb/enable_ccache` (`gporca-archive` `b53c1acd`)
  has this email as the actual PR branch's commit author — the branch was
  pushed from the `xinzweb` GitHub account.
- `zhxin@vmware.com` (VMware era, post-Pivotal-acquisition) — **24 unique
  commits**, 2020. Spot-checked for content, not just titles: real
  RPM/Debian packaging and Concourse CI release-engineering work (e.g. a
  4-file, +119/-85 change co-authored with two other VMware engineers) —
  a materially different kind of work than the 2016-era ORCA/gpdb code
  fixes.

**Resolved by direct SHA comparison** (not just plausible reasoning):
diffing the sorted SHA lists from
`gh api search/commits -f q='repo:apache/cloudberry author:xinzweb'`
against
`gh api search/commits -f q='org:greenplum-db author:xinzweb'` via
`comm -23`/`comm -12` shows all 27 `apache/cloudberry` SHAs land inside
the 34 `xinzweb` commits here (27/27 match, 0 unique to
`apache/cloudberry` only) — not an additional, separate count. Don't add
the two numbers together.

The `greenplum-db`-org totals (deduplicated):

- **209 unique direct-author commits** (34 + 151 + 24 above)
- **+25 unique commits** credited only as `Co-authored-by` (45 raw hits,
  20 were the same SHA already counted as direct-author — likely
  squash-merge duplication)
- **+4 unique commits** credited only as `Reviewed-by` (no overlap with
  either set above)
- **238 total distinct commits** touched in some capacity
- Spanning **2016 through November 2023** — seven-plus years
- Across `gpdb-archive`, `gporca-archive`, `gp-xerces-archive` (not
  previously known to the user — surfaced by this search), and
  `greenplum-database-release-archive`
- Most recent confirmed activity: a `Reviewed-by: Xin Zhang
  <zhxin@vmware.com>` credit on a November 2023 `gpdb-archive` commit —
  about 11 months before the Cloudberry ICLA (2024-10-19)
- **`pxf-archive`, which the user specifically expected to have
  contributions in, came back with zero hits** across every identity
  checked, including several additional email-variant guesses — flagged
  rather than assumed away; either a 4th identity exists that hasn't
  been found, or the expectation doesn't hold

Highlights from the `apache/cloudberry` slice (2016-01 through 2017-11):

- `Fix implied predicates under limit subquery [#129871531] (#125)` —
  2016-11-28, a query-planner correctness fix
- `Adding installcheck-bugbuster (ICB) for all flavors for enterprise
  build. (#1181)` and `Add ICG jobs to run all 4 flavors for enterprise
  build. (#1179)` — 2016-10, CI/build infrastructure
- Several self-merged branches — `fix_32bit_debug`, `enable_ccache`,
  `fix_version` — the merge-pull-request pattern implies commit/merge
  access on Greenplum itself at the time, not just PR-and-wait
- Plus doc/build fixes (README updates, Vagrantfile, minidump
  instructions)

This also lines up with the record already in
`.claude/skills/_cloudberry/README.md`'s sourcing: the original
incubation proposal
(cwiki.apache.org/confluence/display/INCUBATOR/CloudberryProposal) lists
**Shine Zhang among the 22 Initial Committers** named at founding — PPMC
status here was granted as a founding member on the strength of this
Greenplum-era track record, not climbed to from Stage 1 inside Cloudberry
itself. That's a legitimate, different path onto the ladder than
`career-path.md`'s generic Stage 1→2→3→4 sequence describes, and worth
naming as such rather than forcing this into the generic shape.

## Formal Title vs. Merit-Based Level — the actual gap

Two different axes, and the gap is narrower than "no track record" — it's
specifically about **recency**, not competence:

- **Formal Title Level**: Stage 4, PPMC Member. Well-supported — founding
  Initial Committer on real, verifiable Greenplum engineering history
  (above), not a nominal grant.
- **Merit-based, if judged only on activity *since joining the ASF
  project*** (Oct 2024 - present): thin. One PR review comment
  ([#929](https://github.com/apache/cloudberry/pull/929), 2025-05-23),
  zero self-authored Cloudberry PRs or issues found under `xinzweb`, no
  confirmed `dev@`/`private@` post beyond onboarding administrivia (see
  Findings above).

**So the honest read**: this isn't "prove you can do the work" — 2016-2023
already proved that, decisively, and repeatedly. It's "the current
project doesn't see you very often." Those call for different fixes.
Proving competence again
would be redundant; the quest log below is deliberately about *presence* —
small, visible, recent actions — not about re-establishing technical
credibility that was never in question.

---

## Quest log

Check items off as you complete them; log the date and XP earned.

### 🔴 Quest 0 — Where Did Everyone Go? *(do this first)*

- [x] Confirm `dev-subscribe@cloudberry.apache.org`,
      `private@cloudberry.apache.org`, and `commits@cloudberry.apache.org`
      subscriptions are actually active on the address you check — the
      4-6 month inbox silence above is either a real project slowdown or a
      broken subscription, and you want to know which before drawing any
      other conclusion from this file.
- **Done 2026-08-21, +5 XP.** Confirmed broken, not a slowdown: `dev@`
  last delivered 2026-04-14, `private@` 2026-02-05, `commits@` 2026-02-23,
  nothing since on any of them, while `general@incubator.apache.org` kept
  delivering (last seen 2026-08-05) and `apache/cloudberry` had commits as
  recent as 2026-08-19. Resubscribed to all three and completed the ezmlm
  double opt-in. `private@` is moderated (pending approval); `dev@`/
  `commits@` confirmations sent, welcome mail not yet observed — recheck
  next session. **Why it's first**: every other quest below assumes
  you're actually seeing list traffic; if you're not, re-engagement starts
  with fixing that, not with picking up a bug.

### 🟢 Quest 1 — The Confused Column

- [ ] Issue [#726](https://github.com/apache/cloudberry/issues/726) —
      `mvname` column in `gp_matview_aux` isn't schema-qualified, so it can
      be ambiguous. Small, catalog-adjacent, already has a maintainer's
      steer in the comments ("An easy way is just add schema."). Catalog
      code is a flagged high-risk area (`cloudberry-ai-disclosure`'s
      AGENTS.md.template notes) — keep the change minimal and localized.
- **Reward**: +10 XP on filing/claiming the fix, +40 XP when a PR merges.
  Run it through `cloudberry-pr-checklist` + `cloudberry-license-check` +
  `cloudberry-ai-disclosure` before opening the PR.

### 🟡 Quest 2 — Second Pair of Eyes

- [x] PR [#1826](https://github.com/apache/cloudberry/pull/1826) fixes
      issue #1825 (`gpexpand` first-stage crash — `'SyncPackages' object
      has no attribute 'ret'`), open since 2026-06-18, **zero reviews**.
      A real review here both unblocks a contributor and closes a real
      regression.
- **Done 2026-08-21, +20 XP.** Left an Approve review after independently
  re-deriving the bug from current `main` (not trusting the PR
  description): confirmed the `WorkerPool`/`OperationWorkerPool` signature
  mismatch by reading `base.py` directly, and confirmed the "fixed once,
  silently reverted by a merge" claim by checking both commit SHAs
  (`cd3c88f6e1e` the original fix, `0f4cf8d5068` the reverting merge) and
  their dates. CI was fully green. Flagged a non-blocking test-coverage
  gap. See T20260810-723411 for full detail.

### 🟡 Quest 3 — Dust Off the Old Ones

- [ ] Pick one long-stale, zero-review PR from committers and give it a
      real look: [#757](https://github.com/apache/cloudberry/pull/757)
      (open since 2024-12-05) or
      [#787](https://github.com/apache/cloudberry/pull/787) (CI workflow
      for branding checks, open since 2024-12-16).
- **Reward**: +20 XP. A PPMC review on a year-old PR is exactly the kind
  of project-health signal `asf-pmc-duties` flags as scarce.

### ⚪ Ongoing — Weekly Habit

- [ ] Check `dev@` (once Quest 0 confirms it's actually reaching you) —
      use `cloudberry-mailing-list search` before assuming there's nothing
      new.
- **Reward**: +15 XP per week you do this; **Activity Streak** increments
  once per calendar week this is checked off, resets to 0 on a skipped
  week.

---

## XP reference table

| Action | XP | Notes |
|---|---:|---|
| Verify/fix a lapsed list subscription | 5 | one-time per list |
| Triage or acknowledge a stale issue | 5 | e.g. confirm repro, add a label suggestion |
| File a new reproducible bug | 10 | via `cloudberry-bug-report` |
| Weekly `dev@` check-in | 15 | resets Activity Streak if skipped |
| Post/reply on `dev@` (`[DISCUSS]`/`[PROPOSAL]`) | 15 | via `cloudberry-mailing-list` |
| Substantive PR review | 20 | real feedback, not a rubber-stamp approval |
| Cast a binding vote on `private@` | 25 | committer/PPMC nomination or release vote |
| Get a PR merged | 40 | via `cloudberry-pr-checklist` |
| Nominate a new committer | 50 | via `cloudberry-committer-onboarding` |

## Level-up log

Append one line per milestone — this is the only part of the file that's
purely additive, don't edit past entries.

```
2026-08-10  0 XP   File created. Activity Streak reset to 0. Quest 0 opened.
2026-08-21  25 XP  Quest 0 done (+5): dev@/private@/commits@ subscriptions
                    confirmed lapsed and resubscribed. Quest 2 done (+20):
                    substantive Approve review left on PR #1826. Activity
                    Streak -> 1 week. See T20260810-723411.
```
