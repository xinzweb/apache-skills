# Apache Cloudberry Contributor Career Path — Shine Zhang

A living plan, not a reference doc — check items off as you do them. For
Claude-facing process instructions on *how* to do each step, see the
`.claude/skills/cloudberry-*` skills; this file is the human-facing plan of
*what* and *when*.

- **Identity**: GitHub `@xinzweb` · `zhang75033us@apache.org`
- **Current stage**: Stage 4 — PPMC Member
- **Situation**: already hold PPMC standing, activity has been low, goal is
  to re-engage — not to re-climb the ladder
- **Written**: 2026-08-10 — revisit and re-date when you next update this

---

## Where I am on the ladder

| Stage | Status |
|---|---|
| 1. First-time Contributor | ✅ done (historical) |
| 2. Regular Contributor | ✅ done (historical) |
| 3. Committer | ✅ done (historical) |
| **4. PPMC Member** | **◀ here — re-engaging** |
| 5. PMC / Graduation | not yet — podling-wide, not individual |

---

## Right now: 30/60/90-day re-engagement plan

This is the part to actually follow. Update the checkboxes as you go;
add a date next to each when completed.

### First 30 days — get back in the loop

- [ ] Confirm `private@cloudberry.apache.org` and `dev@cloudberry.apache.org`
      subscriptions are still active and landing somewhere you'll see them
- [ ] Read back through the last 60 days of the `dev@` archive
      (https://lists.apache.org/list.html?dev@cloudberry.apache.org) to
      catch up on open threads, in-flight releases, and any pending votes
- [ ] Skim open PRs and Discussions for anything stalled that a PPMC
      voice would help unstick
- [ ] Rejoin Slack `#dev` / Discord if you've drifted out of the loop there

### Next 60 days — one real contribution

- [ ] Pick **one** concrete thing and finish it: a reproducible bug filed,
      a stalled PR reviewed, or a Discussion idea responded to — small and
      finished beats large and abandoned
- [ ] Cast a vote (binding, as PPMC) on the next committer/PPMC nomination
      or release vote thread that comes up — don't let one pass by default
- [ ] If drafting anything with Claude Code, run it through the
      `cloudberry-pr-checklist` / `cloudberry-license-check` /
      `cloudberry-ai-disclosure` skills before opening a PR

### Next 90 days — sustained presence

- [ ] Set a recurring personal cadence for checking `dev@` (weekly is
      reasonable) rather than re-engaging once and drifting out again
- [ ] Consider whether there's a committer candidate worth proposing —
      PPMC members are the ones who initiate that nomination
      (`cloudberry-committer-onboarding`)
- [ ] Re-assess: are you now one of the project's active PPMC members by
      the ASF's own bar (see "Why this matters" below)? If not yet,
      extend this plan rather than declaring it done

---

## The stages, with deliverables and goals

### Stage 1 — First-time Contributor *(historical for you)*

- **Entry**: none — anyone can start
- **Deliverables**: subscribe to `dev@`; read the Code of Conduct; file one
  reproducible bug OR open one Discussion idea; land one small PR
- **Goal**: prove you can follow the project's process end to end
- **Skills**: `cloudberry-bug-report`, `cloudberry-discuss`

### Stage 2 — Regular Contributor *(historical for you)*

- **Entry**: a track record from Stage 1
- **Deliverables**: several merged PRs; reviews on others' PRs; visible
  participation in `dev@` threads (not just PR comments)
- **Goal**: become someone PPMC members would recognize and vouch for
- **Skills**: `cloudberry-pr-checklist`, `cloudberry-license-check`,
  `cloudberry-mailing-list`

### Stage 3 — Committer *(historical for you)*

- **Entry**: a PPMC member proposes you on `private@` (≥7-day discussion),
  then a 1-week vote needs ≥3 binding +1 and no vetoes
- **Deliverables**: not self-directed — the "deliverable" at this stage is
  the sustained Stage-2 record that makes someone else propose you
- **Goal**: write access, GitBox, and a voice reviewers take seriously
- **Skills**: `cloudberry-committer-onboarding`

### Stage 4 — PPMC Member *(you are here)*

- **Entry**: same nomination mechanics as Stage 3, but the candidate must
  already be a committer
- **Deliverables** (ongoing, not one-time): binding votes on committer/PPMC
  nominations and releases; monitoring `private@`; helping nominate the
  next committer when one is warranted
- **Goal**: keep the project's governance capacity healthy — see "Why this
  matters" below
- **Skills**: `cloudberry-committer-onboarding`, `cloudberry-release-runbook`,
  `asf-pmc-duties`

### Stage 5 — PMC / Graduation *(not yet — project-level, not individual)*

- **Entry**: the whole podling graduates from the Incubator to a
  Top-Level Project — not something one person triggers
- **Deliverables**: project-wide — diverse active PPMC, demonstrated
  self-governance, a track record of releases
- **Goal**: full ASF PMC status; the general ASF-wide PMC duties apply from
  here on
- **Skills**: `asf-pmc-duties`

---

## Beyond the project ladder: the foundation-wide track

These are **orthogonal** to Stages 1–5 above — granted by the ASF as a
whole, not by any one project, and reachable without your own project
having graduated. An active committer/PMC member on a still-incubating
podling can already hold these. (Sources: apache.org/foundation/governance/,
news.apache.org board-announcement posts — current as of 2026-08-10; check
live before treating a specific person's role as current, per this repo's
`dev/guidelines.md` privacy guidelines — names in leadership roles turn over
annually and are deliberately not hardcoded here.)

- **ASF Member** — the Foundation's voting membership. An existing Member
  nominates a candidate based on sustained merit/contribution to the
  Foundation, not necessarily on one project alone; all Members vote by
  secret ballot, simple majority elects. Typically decided at the Annual
  Members Meeting (~every 13 months).
  - *Goal*: foundation-wide voting rights and eligibility for Officer/Board
    roles.
- **Foundation Officer / VP** — roles like President, Secretary, Treasurer,
  VP Legal Affairs, or VP Incubator, appointed to run a foundation-wide
  function. Distinct from a **Project VP** — the formal title the elected
  PMC Chair of a *graduated* Top-Level Project holds, scoped to that one
  project. Officers are typically drawn from ASF Members with visible
  cross-foundation involvement (e.g. mentoring multiple podlings).
  - *Goal*: operational leadership of a Foundation-wide function.
- **Board of Directors** — 9 seats, elected annually by ASF Members via
  Single Transferable Vote; only Members can nominate, and in practice
  every candidate has already been a Member; one-year terms, no term
  limits. The Board is the ASF's top governance body and appoints the
  Officers once seated.
  - *Goal*: set Foundation-wide policy; the ceiling of this track.
- **Skills**: `asf-pmc-duties` for the duties that come with PMC-adjacent
  governance roles generally; no dedicated skill yet for the
  Member/Officer/Board nomination mechanics themselves — extend
  `cloudberry-committer-onboarding` or add a new one if this becomes
  actionable rather than aspirational.

---

## Why this matters (not just for me)

The ASF expects at least **three active PMC/PPMC members** monitoring a
project — fewer risks the project being flagged inactive or moved toward
the Attic (source: apache.org/dev/pmc.html, distilled in the
`asf-pmc-duties` skill). Re-engaging isn't just about personal standing —
it's one of the project's few concrete health signals.

---

## Revisiting this plan

This is a snapshot from 2026-08-10. Re-read it every time you sit down to
work on Cloudberry, update the checkboxes, and rewrite the 30/60/90 section
once its window has passed rather than letting it go stale.
