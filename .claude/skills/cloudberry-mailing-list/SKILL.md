---
name: cloudberry-mailing-list
description: Use when the user explicitly asks to check dev@cloudberry.apache.org for relevant discussion, or to draft a [DISCUSS]/[PROPOSAL]/[VOTE] email to the Apache Cloudberry dev list
disable-model-invocation: false
argument-hint: "search <topic> | draft-discuss <topic> | draft-proposal <topic> | draft-vote <topic>"
---

For shared project facts (mailing list roster, this user's PPMC status, subscribe/archive links) see `../_cloudberry/README.md` — treat it as a snapshot, not a live feed.

## Argument

$ARGUMENTS is one verb plus a topic string:

- `search <topic>` — search the dev@ archive for existing discussion on `<topic>`. This is also the default when no verb is given — never skip straight to drafting without it.
- `draft-discuss <topic>` — draft a `[DISCUSS]` thread that floats an idea and invites objections.
- `draft-proposal <topic>` — draft a `[PROPOSAL]` thread for a concrete ask, aimed at lazy consensus rather than a formal vote.
- `draft-vote <topic>` — draft a formal `[VOTE]` thread.

## Workflow

1. **(must-block, all verbs)** Search the archive first: https://lists.apache.org/list.html?dev@cloudberry.apache.org — look for an existing or recent thread on the topic so you don't fork a duplicate discussion. If the verb is `search`, summarize what you find for the user and stop here.

2. **(must-block before telling the user it's safe to send)** Confirm the user is subscribed to `dev@cloudberry.apache.org` (via `dev-subscribe@cloudberry.apache.org`, confirm-by-reply). If subscription status is unknown, say so explicitly in your response rather than assuming it — do not tell the user a draft is ready to send without this caveat.

3. Pick the right subject tag for the topic:
   - **3.a** Floating an idea, still gathering objections, no concrete ask yet → `[DISCUSS]`.
   - **3.b** A concrete ask, seeking lazy consensus (silence = consent after ≥72h) → `[PROPOSAL]` — may combine with a topic tag, e.g. `[PROPOSAL][Repo] ...`.
   - **3.c** Something that genuinely needs explicit, countable approval — a release, adding a committer/PMC member, a bylaws-type decision → `[VOTE]`.
   - Default to DISCUSS/PROPOSAL. Most day-to-day changes use lazy consensus, not a formal vote — only escalate to `[VOTE]` for the cases in 3.c.

4. Compose the draft (To: `dev@cloudberry.apache.org`, Subject, Body) per the chosen verb:
   - **4.a `draft-discuss`** — Subject: `[DISCUSS] <topic>`. Body: state the idea plainly, explain the motivation, explicitly invite objections/alternatives.
   - **4.b `draft-proposal`** — Subject: `[PROPOSAL] <topic>` (add a bracketed topic tag if one fits, e.g. `[PROPOSAL][Repo] <topic>`). Body: state the concrete proposal and that you intend to proceed via lazy consensus if there's no objection within 72 hours.
   - **4.c `draft-vote`** — Subject: `[VOTE] <topic>`. Body: state precisely what is being voted on, the voting scale (-1 to +1; fractional values like +0.9/-0.5 indicate intensity), the voting period (minimum ~72 hours), and which vote category it falls under (see §5) so recipients know the pass criteria.

5. **(must include verbatim for any `draft-vote`)** Before handing off a `[VOTE]` draft, state the applicable category and its rule, since it determines how the vote resolves:
   - **Procedural** — simple majority.
   - **Code-modification** — consensus approval: a single valid **-1** with technical justification is a veto and cannot be overridden by majority.
   - **Package/release** — needs ≥3 binding **+1** votes, more +1 than -1, and cannot be vetoed.
   Also note: only PMC/PPMC members' votes are binding; others are advisory. This user is a PPMC member (`../_cloudberry/README.md`), so their own +1/-1 is binding on code-modification and committer/PPMC votes.

6. **(must-block)** Present the finished draft (To/Subject/Body) to the user for review and tell them to send it themselves from their subscribed address. Do not send the email or submit anything on the user's behalf.

7. **(best-effort)** Only if the user mentions a `[VOTE]` thread has already closed, remind them that a `[RESULT][VOTE]` follow-up summarizing the outcome is expected — but don't draft it unless asked.

## Important Notes

- `dev@cloudberry.apache.org` is the binding decision channel. Apache Way: "if it didn't happen on the mailing list, it didn't happen" — Slack/Discord/GitHub discussion is fine for brainstorming but is not a substitute for a `dev@` thread when a real decision needs to be made.
- Never send the drafted email or submit any form yourself — this is a prose/drafting skill only. Always hand the finished draft to the user and let them send it from their own mail client.
- Posting requires prior subscription (`dev-subscribe@cloudberry.apache.org`, confirm-by-reply); if you can't confirm the user is subscribed, say so rather than guessing.
- Reserve `[VOTE]` for things that truly need explicit approval (releases, adding committers/PMC members, bylaws-type decisions). Default to lazy consensus (`[DISCUSS]`/`[PROPOSAL]`, ≥72h silence = consent) for everything else.
