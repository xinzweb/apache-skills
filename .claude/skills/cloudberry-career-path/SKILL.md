---
name: cloudberry-career-path
description: Use when the user asks about the Apache Cloudberry contributor progression (first-time contributor to committer to PPMC), what stage they are at, or what to do next to become more active
disable-model-invocation: false
argument-hint: "show | my-status"
---

Map of the Apache Cloudberry contributor ladder and which skill operationalizes each rung. See `../_cloudberry/README.md` for shared project facts (mailing lists, chat links, this user's actual PPMC status) — this file inlines only what's needed to place someone on the ladder and point them at the next concrete action.

## Argument

$ARGUMENTS is one verb, no further parameters:

- `show` — display the full four-stage ladder as a general reference (stages, what each grants, which skill covers it). This is also the default when no argument is given.
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

5. **Beyond Stage 4 — not deeply documented in current research.** Eventually the podling as a whole (not any individual) graduates from the Incubator to a Top-Level Project, at which point ASF-wide PMC duties apply in full. If asked about the mechanics of that transition, say plainly that it isn't covered here rather than guessing.

6. **This user's actual position** (per `../_cloudberry/README.md`, use for the `my-status` verb):
   a. Shine Zhang (GitHub `xinzweb`) is already a **PPMC member**, confirmed on the `cloudberry.apache.org/team/` roster. The ICLA, the apache.org email, and both nomination votes (Stage 3 and Stage 4) are already behind them — do not walk them back through those steps or imply they need to re-earn rank.
   b. They are currently re-engaging after a period of low activity. Answer "what stage am I at" / "what do I do next" in those terms: rank is retained, what's being rebuilt is **Stage 1–2 habits** — `dev@` presence, PRs, reviews — not a re-climb of the formal ladder.
   c. Concrete next actions for re-engagement, in ladder terms: reappear on `dev@` (`cloudberry-mailing-list` skill), pick up a PR or a review (`cloudberry-pr-checklist` skill), or file/triage something (`cloudberry-bug-report` / `cloudberry-discuss` skills).
   d. Worth naming explicitly, not just as a personal-development note: the `asf-pmc-duties` skill's project-viability section flags that ASF projects want at least 3 active PMC members monitoring the project. This user re-engaging has direct value to the project's health, not only to their own standing.

## Important Notes

- This is a map, not a duplicate — the process detail for Stage 3/4 (the 7-step and 8-step nomination sequences, ICLA, apache.org email setup) lives in `cloudberry-committer-onboarding`; don't re-derive those steps here.
- Treat `../_cloudberry/README.md` as a dated snapshot (research from 2026-08-09/10), not a live feed — re-check cloudberry.apache.org/team/ if the user's status might have changed since.
- The podling-to-Top-Level-Project graduation step (past Stage 4) is explicitly unconfirmed in current research — flag it as such rather than fabricating a timeline or process.
- This is a pure reference/lookup skill: it doesn't file, send, or submit anything itself. For any action it points to (a PR, a discussion post, a mailing-list draft), hand off to the named skill.
