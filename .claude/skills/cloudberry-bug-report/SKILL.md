---
name: cloudberry-bug-report
description: Use when the user explicitly asks to file a bug report against Apache Cloudberry
disable-model-invocation: false
argument-hint: "file <summary> | check <description>"
---

# Cloudberry Bug Report

File (or triage) a bug report against `apache/cloudberry` on GitHub Issues, using
the repo's "Bug Report" issue form. See `../_cloudberry/README.md` for shared
project facts (repo, mailing lists, this user's PPMC status); this file inlines
only what's needed to file a bug.

## Argument

The verb in `$ARGUMENTS` selects the mode:

- `file <summary>` — draft a bug report from `<summary>` and walk it through to
  filing.
- `check <description>` — triage only: confirm `<description>` is really a
  reproducible bug (not a feature idea or question) and check for existing
  duplicates. Do not draft or file anything.
- No argument — behave as `file`, pulling the bug description from the
  surrounding conversation; ask the user for it if it isn't clear yet.

## Workflow

1. Triage (must-block — do not skip, for either verb).
   a. Confirm this describes a **reproducible bug in Apache Cloudberry itself**,
      not a feature request or a usage question. The repo's Issues tracker has
      no separate feature-request/question template (`config.yml` defines only
      the bug form) — feature ideas and questions belong on GitHub Discussions
      instead, via the `cloudberry-discuss` skill. If it's ambiguous, ask the
      user which it is rather than guessing.
   b. Confirm the bug is actually reproducible. The Bug Report template
      explicitly warns that non-reproducible issues will be closed, and
      suggests opening a Discussion first if reproduction steps aren't known
      yet. If the user can't yet reproduce it, say so and point them at
      `cloudberry-discuss` instead of filing.
   c. If invoked as `check`, stop here: report the triage verdict (bug vs.
      not-a-bug; reproducible vs. not) plus the duplicate-search result from
      step 2, and do not proceed to drafting or filing.

2. Search for duplicates (best-effort).
   Run `gh issue list --repo apache/cloudberry --search "<keywords>"` with a
   few keywords pulled from the bug summary. Skim the results; if a clear
   duplicate exists, surface it to the user and ask whether to comment there
   instead of filing a new issue.

3. Draft the content, mapping onto `.github/ISSUE_TEMPLATE/bug-report.yml`
   ("Bug Report"). Filing via this template auto-prefixes the issue title with
   `[Bug] ` and applies the `type: Bug` label — don't add either yourself.
   Required fields:
   - **What happened** — the observed behavior.
   - **How to reproduce** — concrete steps. This is the field the template
     warns will get the issue closed if it's missing or too vague.
   - **Operating System**.
   - **Code of Conduct checkbox** — "I agree to follow this project's Code of
     Conduct" must be checked to submit. It links `CODE_OF_CONDUCT.md`, which
     adopts the ASF Code of Conduct wholesale
     (https://www.apache.org/foundation/policies/conduct) — there are no
     Cloudberry-specific conduct rules beyond that.
   Optional fields (fill in if the user has the info, otherwise leave blank):
   - Apache Cloudberry version
   - What you think should happen instead
   - Anything else
   - "Are you willing to submit a PR?" checkbox

4. Present the full drafted title and field values to the user for review
   (must-block). Do not submit anything until the user has explicitly approved
   the exact text — filing a public GitHub issue notifies the whole project
   and isn't something to do unattended, the same principle as not sending
   email or ICLA forms without sign-off.

5. Once approved, file it (must-block on step 4's approval) via one of:
   - CLI: `gh issue create --repo apache/cloudberry --template bug-report.yml`
     (fill the interactive prompts with the approved field text, or pass
     `--body` with the assembled templated content).
   - Browser: send the user to
     https://github.com/apache/cloudberry/issues/new/choose to pick the
     "Bug Report" form themselves.
   Report back the resulting issue URL/number.

## Important Notes

- Never run `gh issue create` (or otherwise submit) before the user has signed
  off on the drafted content — treat it like sending an email or an ICLA
  submission, not something to fire off unattended.
- Apache Cloudberry issue tracking is GitHub-native; there is no separate JIRA.
- Feature requests and questions are out of scope for this skill — redirect
  those to `cloudberry-discuss` (GitHub Discussions) rather than forcing them
  into the bug template.
- For shared community facts (mailing lists, Slack, Discord, website sections,
  this user's PPMC status), see `../_cloudberry/README.md` rather than
  re-deriving them here.
