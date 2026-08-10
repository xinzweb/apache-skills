---
name: cloudberry-career-path
description: Use when the user asks about the Apache Cloudberry contributor progression (first-time contributor to committer to PPMC) or the wider ASF-wide governance track (Member, Officer, Board), what stage they are at, or what to do next to become more active
disable-model-invocation: false
argument-hint: "show | my-status"
---

Map of the Apache Cloudberry contributor ladder and which skill operationalizes each rung. See `../_cloudberry/README.md` for shared project facts (mailing lists, chat links, this user's actual PPMC status) — this file inlines only what's needed to place someone on the ladder and point them at the next concrete action.

## Argument

$ARGUMENTS is one verb, no further parameters:

- `show` — display the full ladder as a general reference: the four Cloudberry project stages plus the foundation-wide Member/Officer/Board track (stages, what each grants, which skill covers it). This is also the default when no argument is given.
- `my-status` — apply the ladder to this specific user, using the confirmed position in `../_cloudberry/README.md`, and report their actual stage plus concrete next actions rather than the generic ladder text.

## Conventions

The four-stage Apache Cloudberry contributor ladder, per cloudberry.apache.org/contribute and /team/*:

1. **Stage 1 — First-time Contributor**
   a. Get help before or during a first contribution: Slack `#dev` or Discord (invite links in `../_cloudberry/README.md`), or WeChat for Mandarin speakers. The official how-to-contribute page (cloudberry.apache.org/contribute/how-to-contribute) explicitly invites first-timers to ask in Slack `#dev` or GitHub Discussions "especially when making your first contribution."
   b. Read cloudberry.apache.org/contribute/how-to-contribute and the Code of Conduct before doing anything else.
   c. Ways in — pick one: file or investigate a bug (`cloudberry-bug-report` skill); propose an idea or ask a question via GitHub Discussions (`cloudberry-discuss` skill); review someone else's open PR or proposal; or submit a first code/doc PR (`cloudberry-pr-checklist` + `cloudberry-license-check` + `cloudberry-ai-disclosure` skills together).

2. **Stage 2 — Regular Contributor**
   a. Sustained PRs and reviews over time — no fixed count or time-in-project threshold is documented.
   b. Active, visible presence on `dev@cloudberry.apache.org` (`cloudberry-mailing-list` skill).
   c. This is the stage where PPMC members start noticing someone as a committer candidate. Nomination criteria are informal — "productive contributors," "demonstrated leadership and commitment" — not a fixed quota.

3. **Stage 3 — Committer**
   a. Reached via the 7-step `private@` nomination-plus-vote process (`cloudberry-committer-onboarding` skill).
   b. Grants write access to the repo, GitBox, and a vote that carries more informal weight in code reviews.
   c. Does not relax the PR bar: PRs still need the same 2-approval threshold per `.asf.yaml`, including a committer's own PRs.
   d. Optional next step: a committer may take on release-manager duties (`cloudberry-release-runbook` skill).

4. **Stage 4 — PPMC Member**
   a. Reached via the 8-step PPMC nomination process, which requires already being a committer (Stage 3) first (`cloudberry-committer-onboarding` skill covers both processes).
   b. Grants `private@` list access, a BINDING vote on committer/PPMC nominations and on releases, and a role in guiding project direction.
   c. From here on, general ASF-wide PMC/PPMC duties apply — board reporting, roster maintenance, project-viability roll calls, and the rest. These are not Cloudberry-specific; see the separate `asf-pmc-duties` skill, which applies to any ASF project.

5. **Project Graduation — project-level, not individual.** The podling as a whole (not any one person) graduates from the Incubator to a Top-Level Project once its infrastructure, community, and decision-making are judged self-sustaining. The PPMC becomes the new TLP's PMC; ASF-wide PMC duties (`asf-pmc-duties` skill) apply in full from that point. Exact graduation mechanics/timeline for Cloudberry specifically are not covered here — say so rather than guessing.

6. **Beyond the project ladder — the foundation-wide personal track.** These tiers are ORTHOGONAL to Stages 1–5: they're granted by the ASF as a whole, not by any one project, and do not require your own project to have graduated first (an active committer/PMC member on an incubating podling can already hold these). Source: apache.org/foundation/governance/, news.apache.org board-announcement posts.
   a. **ASF Member** — the Foundation's voting membership. An existing ASF Member nominates a candidate (typically a committer/PMC member showing sustained merit and contribution to the Foundation's growth, not necessarily on one project alone); all Members vote, a simple majority (more Yes than No) elects; ballots are secret. New members are typically elected at the Annual Members Meeting (held roughly every 13 months).
   b. **Foundation Officer / VP** — roles like President, Secretary, Treasurer, VP Legal Affairs, or VP Incubator, appointed to run a foundation-wide function; distinct from a **Project VP**, which is the formal corporate title held by the elected PMC Chair of a graduated Top-Level Project (scoped to that one project). Officers are typically drawn from ASF Members with demonstrated cross-foundation involvement.
   c. **Board of Directors** — 9 seats, elected annually by ASF Members at the Annual Members Meeting via Single Transferable Vote; only ASF Members can nominate candidates, and in practice every candidate has already been a Member; one-year terms, no term limits. The Board is the Foundation's top governance body and, once seated, appoints/confirms the Foundation Officers.

7. **This user's actual position** (per `../_cloudberry/README.md`, use for the `my-status` verb):
   a. Shine Zhang (GitHub `xinzweb`) is already a **PPMC member**, confirmed on the `cloudberry.apache.org/team/` roster. The ICLA, the apache.org email, and both nomination votes (Stage 3 and Stage 4) are already behind them — do not walk them back through those steps or imply they need to re-earn rank.
   b. They are currently re-engaging after a period of low activity. Answer "what stage am I at" / "what do I do next" in those terms: rank is retained, what's being rebuilt is **Stage 1–2 habits** — `dev@` presence, PRs, reviews — not a re-climb of the formal ladder.
   c. Concrete next actions for re-engagement, in ladder terms: reappear on `dev@` (`cloudberry-mailing-list` skill), pick up a PR or a review (`cloudberry-pr-checklist` skill), or file/triage something (`cloudberry-bug-report` / `cloudberry-discuss` skills).
   d. Worth naming explicitly, not just as a personal-development note: the `asf-pmc-duties` skill's project-viability section flags that ASF projects want at least 3 active PMC members monitoring the project. This user re-engaging has direct value to the project's health, not only to their own standing.

## Important Notes

- This is a map, not a duplicate — the process detail for Stage 3/4 (the 7-step and 8-step nomination sequences, ICLA, apache.org email setup) lives in `cloudberry-committer-onboarding`; don't re-derive those steps here.
- Treat `../_cloudberry/README.md` as a dated snapshot (research from 2026-08-09/10), not a live feed — re-check cloudberry.apache.org/team/ if the user's status might have changed since.
- Cloudberry's own graduation timeline/mechanics (item 5) are explicitly unconfirmed in current research — flag that as such rather than fabricating a date or process, even though the general ASF Member/Officer/Board mechanics (item 6) are documented and fine to state.
- **Never hardcode specific individuals' names into item 6** (who's currently on the Board, who holds an Officer role) — those rosters turn over annually (one-year Board terms). Point to the live source (apache.org/foundation/board/, apache.org/foundation/members) instead, per this repo's `dev/guidelines.md` "Content & Privacy Guidelines" — a name written here today reads as a current fact to whoever reads it later, and will go stale.
- This is a pure reference/lookup skill: it doesn't file, send, or submit anything itself. For any action it points to (a PR, a discussion post, a mailing-list draft), hand off to the named skill.
