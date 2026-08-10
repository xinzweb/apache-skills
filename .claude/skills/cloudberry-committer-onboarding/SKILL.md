---
name: cloudberry-committer-onboarding
description: Use when the user explicitly asks about nominating a new Apache Cloudberry committer or PPMC member, or about ICLA / apache.org email setup steps
disable-model-invocation: false
argument-hint: "nominate-committer <candidate> | nominate-ppmc <candidate> | icla | apache-email"
---

# Cloudberry Committer Onboarding

Four related but distinct Apache Cloudberry processes: nominating a new
committer, nominating a new PPMC member, filing an ICLA, and setting up an
`@apache.org` email account. See `../_cloudberry/README.md` for shared
project facts (mailing lists, this user's PPMC status); this file inlines
everything specific to onboarding.

This user is already a PPMC member (`../_cloudberry/README.md`) with an
existing ICLA and `@apache.org` address. That means: (a) the `nominate-*`
verbs are the ones they'll actually use going forward, to propose *other*
people — PPMC members are the ones who initiate these nominations; (b) the
`icla` and `apache-email` verbs mostly serve as reference material — either
to walk a newly-accepted candidate through their own onboarding, or to
recall the process the user already went through.

## Argument

$ARGUMENTS is one verb, plus a candidate name for the two nomination verbs:

- `nominate-committer <candidate>` — walk through proposing `<candidate>` as
  a new Apache Cloudberry committer (§1).
- `nominate-ppmc <candidate>` — walk through proposing `<candidate>` as a
  new PPMC member (§2).
- `icla` — walk through the ICLA (Individual Contributor License Agreement)
  filing steps for a new committer (§3).
- `apache-email` — walk through setting up the `@apache.org` email account
  (§4).
- No argument — ask the user which of the four they mean rather than
  guessing; the committer and PPMC nomination processes share the same vote
  mechanics (§1.2/§2.2) but have different eligibility bars — PPMC requires
  an existing committer — and picking the wrong one wastes a private@
  thread.

## Workflow

### §1. `nominate-committer <candidate>` — New Committer process
(cloudberry.apache.org/team/new-committers, 7 steps)

1. **Must-block.** Draft a private discussion email — To:
   `private@cloudberry.apache.org`, body proposing `<candidate>` with
   concrete justification (contributions, review quality, community
   engagement). Present the draft to the user for review/editing; they send
   it, not you. This discussion runs **at least 7 days** before a vote can
   open.
2. **Best-effort**, once discussion has been positive for 7+ days. Draft a
   formal `[VOTE]` thread to `private@cloudberry.apache.org`: scale +1
   (yes) / 0 (abstain) / -1 (no, must include reasoning), one-week voting
   period, passing bar is **≥3 binding +1 votes and no vetoes**. Present the
   draft for the user to send.
3. The outcome — positive or negative — is announced publicly either way. A
   negative result **halts the process here**; do not proceed to steps 4–7.
4. On success, a private, confidential invitation to accept/decline is sent
   to the candidate.
5. If the candidate accepts, they file an ICLA to `secretary@apache.org` —
   hand off to the `icla` verb (§3).
6. The new committer sets up their `@apache.org` email account (hand off to
   the `apache-email` verb, §4), completes GitBox setup (linking their
   GitHub account), and enables two-factor authentication on GitHub. The
   source facts name GitBox setup and 2FA but give no further procedural
   detail — say so explicitly and point the user to
   `cloudberry.apache.org/team/new-committers` rather than inventing steps.
7. PPMC members update the official roster (granting permissions), send a
   welcome email, and announce the new committer publicly on
   `dev@cloudberry.apache.org`.

### §2. `nominate-ppmc <candidate>` — New PPMC Member process
(cloudberry.apache.org/team/new-ppmc-member, 8 steps)

Eligibility check first: the candidate should be an **existing committer**
who has demonstrated leadership and commitment to the project — if
`<candidate>` isn't already a committer, this is the wrong process (point
back to §1 instead).

1. **Must-block.** Any PPMC member proposes the candidate on
   `private@cloudberry.apache.org` with rationale. Draft it, present to the
   user, they send it. 7+ day discussion.
2. **Best-effort**, after a positive discussion. Draft a one-week formal
   `[VOTE]` thread, same scale (+1/0/-1) and same bar as §1.2: ≥3 binding
   +1 votes, no vetoes.
3. Results announced.
4. Private invitation to accept/decline.
5. Roster updated via the **Whimsy** tool, granting appropriate privileges
   (source facts name the tool but don't detail its UI — don't guess).
6. A formal welcome email is sent from the PPMC.
7. Public announcement on `dev@cloudberry.apache.org`.
8. Notification shared across other community channels — the source facts
   say "other community channels" without naming them; don't guess beyond
   that.

New permissions once PPMC (informational, for context when explaining the
step to a candidate): access to project archives, ability to read private
PPMC discussions, participation in PPMC decision-making, authority to
invite new committers/PPMC members, and a voice in guiding project
direction.

### §3. `icla` — sign and file the ICLA
(cloudberry.apache.org/team/sign-icla)

1. Download the Individual Contributor License Agreement (ICLA) form from
   the Apache website — the source facts don't give the direct PDF URL, so
   don't fabricate one; point the candidate to
   `cloudberry.apache.org/team/sign-icla` for the link.
2. Fill in: Full Name; optional Public Name (defaults to Full Name if left
   blank); a **detailed postal address down to door number** (the page
   warns a vague address causes rejection); email; and a preferred Apache
   ID (this becomes their `xxx@apache.org` address). Set "Notify project:
   Apache Cloudberry".
3. Sign digitally — macOS: Preview's Tools > Annotate > Signature; iOS:
   the Files app's built-in Signature; Android: a PDF tool such as Adobe
   Acrobat's Fill & Sign.
4. **Must-block.** Present the fully filled-in field values (and confirm
   the form is signed) to the user for review before anything is sent —
   filing this is not something to do unattended. Once approved, they email
   it themselves:
   - To: `secretary@apache.org` **only** — no other recipients.
   - Subject: `ICLA from [Your Name] for Project Cloudberry`
   - Body: a brief note that they're a new committer for the Cloudberry
     podling.
5. Tell them to keep a copy of the signed form for their own records.
6. The source page documents no specific follow-up timeline — say so
   explicitly if asked when to expect confirmation, rather than guessing.

### §4. `apache-email` — set up the `@apache.org` account
(cloudberry.apache.org/team/setup-apache-email-account)

Prerequisite: the person already has a Gmail account and an issued Apache
ID + password (from §1/§3).

1. In Gmail: Settings > Accounts and Import > "Send mail as" > add the
   `@apache.org` address.
2. Configure SMTP: server `mail-relay.apache.org`, port `465`, authenticate
   with the Apache ID + password, and select "Secured connection using SSL
   (recommended)".
3. A confirmation email titled "Gmail Confirmation - Send Mail as
   `xx@apache.org`" arrives — click its confirmation link to complete
   setup.
4. Test it: have someone send a message from another account to the new
   `@apache.org` address and confirm it's received.
5. Going forward, select the `@apache.org` address as sender when composing
   from that Gmail account.

## Important Notes

- Nominations happen on `private@cloudberry.apache.org`, the PPMC-only
  list — see `../_cloudberry/README.md`. Only PPMC members can initiate a
  nomination and only PPMC members' votes are binding; if you're drafting
  this on behalf of someone who isn't a PPMC member, say so before
  drafting.
- Never send the private@ discussion/vote email, the welcome email, the
  public announcement, or the ICLA on the user's behalf — every email in
  §1–§4 is a draft-and-hand-off: present the exact To/Subject/Body (or
  filled form) and let the human send/submit it themselves.
- A negative vote outcome in either §1.2 or §2.2 halts the process — don't
  continue drafting downstream steps (invitation, roster update, welcome
  email) once that's happened.
- The ICLA goes to `secretary@apache.org` and nowhere else — don't add
  `private@` or any other CC.
- Where the source facts name a tool or step without further detail
  (GitBox setup, 2FA, the Whimsy roster tool, the ICLA PDF's exact URL),
  say that plainly and point to the relevant `cloudberry.apache.org/team/*`
  page rather than inventing specifics.
