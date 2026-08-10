---
name: asf-pmc-duties
description: Use when the user asks what a PMC or PPMC member is responsible for at the Apache Software Foundation, generally (not specific to one project)
disable-model-invocation: false
argument-hint: "show | roll-call"
---

Generic ASF reference — applies to any top-level project or Incubator podling, not just one project. Source: https://www.apache.org/dev/pmc.html. For how this generic duty set maps onto this user's actual PPMC role on the Cloudberry podling, use the `cloudberry-career-path` skill instead of trying to derive it from this one.

## Argument

$ARGUMENTS is one verb:

- `show` (default) — answer using all eight sections below. Use this whenever the user's question isn't specifically about a Board roll call.
- `roll-call` — narrow the answer to just **§1** and **§7**, and state the two concrete numbers plainly: at least three active PMC members must be able to respond to a Board roll call within the given timeline, and mature/slow-moving projects should run their own roll call (recommended yearly) proactively, replying to board@ with a link to the mailing-list thread that demonstrates the engagement.

## Conventions

Answer from the following ASF source, organized by responsibility area; cite the §-number if the user needs to trace a duty back to a specific area.

### §1. Reporting & Board Accountability
- PMC Chairs/VPs SHALL submit a quarterly project-health report to the Board.
- Reply to director questions about those reports via board@.
- Monitor Board meeting minutes for project-related comments and relay them to the PMC.
- When the Board requests a roll call, demonstrate that at least three active PMC members can respond within the given timeline.

### §2. Policy Compliance
- Ensure project work complies with Apache License usage, IP/copyright handling, cryptography export rules, and official release procedures.
- Manage the project brand per ASF guidelines and the PMC Branding Responsibilities doc.
- Review third-party misuse of the project brand/trademark and follow ASF trademark-reporting guidelines.

### §3. Mailing List & Communication Management
- Nearly all technical decisions and PMC work should happen on the normal public lists (dev@, user@).
- Allow at least ~72 hours for geographically dispersed members to weigh in before treating silence as consent.
- Subscribe to and monitor the project's private@ list so the PMC stays responsive to Board requests.
- private@ is ONLY for pre-disclosure security issues, confidential third-party discussions, nominee discussions, and personnel conflicts — never general business.

### §4. PMC Member Recruitment & Management
- Elect new PMC members via a private-list vote, per ASF voting rules.
- Formally invite accepted candidates, copying private@, and wait for their acceptance before updating the roster.
- Update the official roster via the Whimsy tool once the candidate accepts.
- Remind new PMC members to subscribe to private@ and read the PMC Branding Responsibilities doc.
- Resignations take effect immediately on receipt by the list, with a 72-hour window during which the member may withdraw the resignation.
- Removing a member without their consent requires sending justification to board@ (cc private@) for Board approval.
- On a member's death, notify root@apache.org and secretary@apache.org so the account can be disabled and Foundation records updated.

### §5. Project Committer Management
- Nominate productive contributors as new committers.
- Hold a formal PMC vote on the private list, per ASF voting rules.
- Collect an ICLA from any new committer who doesn't already have one, sent to secretary@apache.org.
- Once the ICLA is filed, use the ASF New Account Request form to request the account — include the PMC name, the desired account ID, and a reference to the vote.
- Grant repository write access via the Whimsy roster tool, or contact Infra if the automated LDAP process fails.
- For a candidate who already holds an Apache account, grant project-specific access the same way (Whimsy roster tool).

### §6. Chair-Specific Duties
- Facilitate PMC discussions so all members have a voice.
- Own quarterly board-report completeness and timeliness — may delegate the writing, not the accountability.
- Ensure a newly elected committer actually receives repository access ("karma") after the vote and account creation; a vote by itself grants nothing.
- Keep the PMC's official roster in committee-info.txt current. NOTICE emails now fire automatically on roster updates, so no manual notice is needed first.
- On a chair/VP change, hold a PMC vote or reach consensus, then send a formal resolution to board@ via the Board Agenda Tool for Board approval.
- Make sure enough PMC members monitor private@ to answer Board roll calls.

### §7. Project Viability & Health
- Keep at least three PMC members active and monitoring the project — fewer risks the project being moved to the Attic.
- Mature/slow-moving projects should hold a roll call (recommended yearly) confirming 3+ active members, responding to board@ with a link to the mailing-list thread showing that engagement.
- Maintain the capacity to issue security releases and handle serious bugs promptly — the Board checks for this.

### §8. General Oversight & Judgment
- Guide new committers to the right resources/ASF docs (new-committer guide, FAQ).
- Respect project self-governance: escalate conflicts or policy questions to the relevant Board committee/officer via the Escalation Guide, and only after internal resolution has failed.
- Keep Board feedback and pre-approved board-meeting minutes confidential until formally approved for public discussion.

## Important Notes

- This is a lookup/reference skill only — it does not send email, cast votes, submit the ICLA or New Account Request form, or update any roster on the user's behalf. Where a duty above requires an actual action (§4 invite, §5 ICLA/account request, §6 resolution to board@), draft the content and hand it to the user to send themselves; do not act unattended on any of these.
- Generic across the whole ASF: do not fold in any single project's mailing-list addresses, roster, or roles here. This skill intentionally has no project-specific facts to inline for standalone use — it's ASF-wide by design.
- §1's "SHALL submit a quarterly report" and §7's "at least three active PMC members" are the two hard, Board-checked minimums in this list; the rest are strong ASF norms rather than bright-line rules.
- If the user needs current specifics beyond what's summarized here (e.g., the live text of the PMC Branding Responsibilities doc or the Escalation Guide), tell them to check https://www.apache.org/dev/pmc.html directly rather than inventing a URL — none is given here beyond that source.
