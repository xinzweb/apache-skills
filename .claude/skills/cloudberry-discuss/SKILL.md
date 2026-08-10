---
name: cloudberry-discuss
description: Use when the user explicitly asks to open a feature idea, proposal, or question about Apache Cloudberry — these are routed to GitHub Discussions, not Issues
disable-model-invocation: false
argument-hint: idea <summary> | proposal <summary> | question <summary>
---

Shared facts (repo, mailing lists, website, this user's identity) live in
`../_cloudberry/README.md` — read it if you need those, they are not
re-derived here. This skill only covers the facts specific to routing a
feature idea, proposal, or question into `apache/cloudberry` GitHub
Discussions.

## Argument

`$ARGUMENTS` is one verb plus a short summary of what the user wants to raise:

- `idea <summary>` — routes to the **Ideas/Feature Requests** Discussion
  category, using the structured form at
  `.github/DISCUSSION_TEMPLATE/ideas-feature-requests.yml`.
- `proposal <summary>` — routes to the **Proposal** Discussion category (for
  developers proposing major changes/enhancements), using the structured form
  at `.github/DISCUSSION_TEMPLATE/proposal.yml`.
- `question <summary>` — routes to the **Q&A** Discussion category (help
  running or developing Cloudberry). No structured template file for Q&A is
  confirmed in this skill's source facts — draft freeform.

**No argument**: do not guess — ask the user which of the three categories
applies. They are not interchangeable (different form, different audience),
so drafting against the wrong one wastes the user's edit.

## Workflow

1. **Classify, and reject the wrong venue.** `apache/cloudberry`'s
   `.github/ISSUE_TEMPLATE/config.yml` has `blank_issues_enabled: true` but no
   feature-request or question Issue template — its `contact_links`
   intentionally send feature ideas, proposals, and questions to GitHub
   Discussions instead. If what the user actually wants is a bug report, stop
   here: this skill is not the right one, don't draft an Issue-shaped thing as
   a Discussion.

2. **Get the exact form fields (best-effort).** For `idea` or `proposal`,
   read the matching template before drafting so field names match the real
   form:
   ```
   gh api repos/apache/cloudberry/contents/.github/DISCUSSION_TEMPLATE/ideas-feature-requests.yml --jq '.content' | base64 -d
   gh api repos/apache/cloudberry/contents/.github/DISCUSSION_TEMPLATE/proposal.yml --jq '.content' | base64 -d
   ```
   If `gh` access isn't available, fall back to opening
   https://github.com/apache/cloudberry/discussions/new and selecting the
   category to see its fields directly — do not invent field names you
   haven't actually seen. For `question`, no template file is confirmed;
   draft a plain title + body and let the Q&A form's own fields (whatever
   GitHub shows for that category) apply.

3. **Draft the content**, don't post it yet:
   - Title: plain and specific. For `proposal`, precedent on this repo uses a
     `[Proposal] <Title>` bracket prefix (see discussion #868, "[Proposal]
     Apache Cloudberry (Incubating) Roadmap" —
     https://github.com/apache/cloudberry/discussions/868) — follow that
     convention for proposals. No such prefix precedent is confirmed for
     `idea` or `question`; leave those titles unprefixed.
   - Body: fill every field the chosen template exposes (from step 2) —
     summary/motivation/details as the form names them. Don't leave template
     fields blank without at least noting "N/A" where the user has no answer.
   - Category: state it explicitly in your draft output (Ideas/Feature
     Requests, Proposal, or Q&A) so the user picks the matching dropdown
     entry.

4. **For `proposal`, or anything the user describes as a major change**
   (best-effort but don't skip silently): point them at the website's
   Proposal Guide, linked from https://cloudberry.apache.org/contribute,
   before they post — a Discussion draft for a substantial change should
   follow that guide's structure, not just this skill's template fields.

5. **Flag the mailing-list record requirement — must not skip for
   `proposal`.** GitHub Discussions is a fine place to flesh out details, but
   under the Apache Way, "if it isn't on the mailing list it didn't happen":
   anything beyond early brainstorming — anything that will become a real
   decision — must also get a `[DISCUSS]` or `[PROPOSAL]` email to
   `dev@cloudberry.apache.org` to be part of the binding record. Tell the
   user this explicitly whenever the content is proposal-shaped; do not treat
   the Discussion thread alone as sufficient. Use the `cloudberry-mailing-list`
   skill to draft that email — don't duplicate its logic here.

6. **Hand off for posting — do not attempt to post it yourself.** There is no
   first-class `gh discussion create` subcommand; creating a Discussion via
   CLI would require the GitHub GraphQL API (`gh api graphql`), which is
   fiddly and easy to get subtly wrong. Do not invent a `gh discussion`
   command. Instead, present the finished title + category + body to the
   user and tell them to paste it into
   https://github.com/apache/cloudberry/discussions/new, selecting the
   category you named in step 3.

## Important Notes

- Filing a feature idea, proposal, or question as a GitHub **Issue** on this
  repo is the wrong venue — `config.yml`'s `contact_links` exist specifically
  to redirect that traffic to Discussions.
- Never fabricate the structured form's field names — fetch the real
  template (step 2) or read them off the live "new discussion" page; a
  plausible-looking guess is not the same as the real form.
- Do not attempt to create the Discussion via `gh` or any API call on the
  user's behalf — draft precisely, then let the human paste and submit it
  themselves, same as with ICLA forms or outbound email.
- A Proposal-category Discussion is not, by itself, an Apache-Way-compliant
  record of a decision — the `dev@cloudberry.apache.org` cross-post (step 5)
  is what makes it binding.
