---
name: cloudberry-license-check
description: Use when the user explicitly asks to run a license/RAT check before submitting a pull request to Apache Cloudberry, or a PR's apache-rat-audit CI check has failed
disable-model-invocation: false
argument-hint: "check | add-header <file>"
---

# Cloudberry License Check

Apache RAT (Release Audit Tool) enforces ASF license-header compliance on every
PR to `apache/cloudberry`. It runs automatically in CI via
`.github/workflows/apache-rat-audit.yml`, which is one of the required status
checks under `.asf.yaml` branch protection — a failing check blocks merge.
This skill runs that audit locally before push and walks through resolving
failures correctly. Shared project facts (mailing lists, repo URLs, this
user's role) live in `../_cloudberry/README.md`; this file covers only the
RAT/header mechanics.

## Argument

- `check` (default): run the RAT audit locally via `mvn apache-rat:check` and
  walk through any findings.
- `add-header <file>`: resolve one file that RAT flagged — either give it the
  standard ASF header or add a `pom.xml` exclusion, depending on who
  authored it (§3).

No-arg invocation runs `check`.

## Workflow

### §1. Run the local RAT check (must-block before push)
From the repo root, run:

```
mvn apache-rat:check
```

This is the same audit `.github/workflows/apache-rat-audit.yml` runs on every
PR. Running it locally first catches header problems before they surface as a
failed required check on the PR — treat a failure here as something that must
be resolved before telling the user the PR is ready to push.

### §2. Read the report if it failed (must-block)
If the check fails, read `target/rat.txt` for the detailed list of
unapproved/flagged files. If a browsable view is useful, optionally generate
the HTML report:

```
mvn apache-rat:rat
mvn site
```

### §3. Classify each flagged file before touching it (must-block)
For every file RAT flags, determine which case applies — do not default to
"just add a header":

- **§3.a Community-authored file missing a header.** If the file was newly
  originated by the community (written by a contributor, not vendored from
  elsewhere), add the standard Apache License 2.0 header to it. Every new
  community-originated file must carry it.
- **§3.b Third-party file, no header, but a compatible license.** Do **not**
  add or fabricate an ASF header on a file you did not author — that
  misrepresents its provenance. Instead add an exclusion entry for it to the
  RAT plugin configuration in `pom.xml` at the repo root so RAT skips that
  file. Confirm the file's actual license is genuinely
  Apache-2.0-compatible before excluding it; an exclusion is not a way to
  paper over an unresolved license question.
- If you cannot tell which case a file belongs in, say so explicitly and ask
  the human rather than guessing — misclassification is the main way this
  check gets handled wrong.

### §4. Re-run to confirm (must-block)
After making changes, re-run `mvn apache-rat:check` and confirm it passes
clean (`target/rat.txt` shows no unapproved files) before telling the human
the PR is ready to push.

### §5. Flag the boundary with reviewer license judgment (best-effort)
RAT is mechanical: it checks header presence/format and the exclusion list,
not the substance of what was included. A clean RAT check is not a substitute
for the human reviewer's separate license-*compatibility* judgment (no
GPLv2/3 or other non-OSI-compatible code) — that substantive review belongs
to a human reviewer (see `cloudberry-pr-checklist` if that skill exists in
this skills directory). Mention to the human that this remains a separate,
still-needed step even after RAT passes.

## Important Notes

- Never add an ASF license header to a file you did not author — use a
  `pom.xml` RAT exclusion instead for compatible-but-unheadered third-party
  files (§3.b).
- A failing `apache-rat-audit` CI check blocks merge; it is a required status
  check under `.asf.yaml` branch protection, not something to route around.
- RAT's header/metadata checking is separate from, and does not replace, a
  human reviewer's substantive license-compatibility review of what code was
  actually included.
