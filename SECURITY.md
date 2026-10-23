# Security policy

paranoid-sre tells an AI agent how to behave around production
infrastructure and data. Advice that leads an agent to destroy something
without asking, leak a secret, or work around a guard is a security bug.

## Reporting a vulnerability

Use [GitHub's private vulnerability reporting](https://github.com/SandeepKomal/paranoid-sre/security/advisories/new).
Please don't open a public issue for it.

A useful report includes:

- the task you gave the agent, and the model and Claude Code version
- what the agent did, with the commands it ran
- which instruction in the skill was missing, wrong or ignored

You can expect an acknowledgement within 3 days and a fix or a plan within
14 days. Fixes are credited in the release notes unless you'd rather stay
anonymous.

## What counts

- A recommended command that changes state while presented as read-only.
- Wording that lets an agent skip the question before an irreversible
  change, or work around a guard such as blast-radius.
- Advice that exposes secrets or personal data, for example printing
  credentials or copying production data.
- Anything in the repository's workflows or release process that could let
  someone tamper with a published `paranoid.zip`.

An agent ignoring an instruction it was given is a model behaviour problem,
not a vulnerability in the skill, but reports are still welcome: we may be
able to make the instruction harder to miss. For hard limits, use
[blast-radius](https://github.com/SandeepKomal/blast-radius).

## Supply chain

- The skill is plain Markdown with no code that runs.
- Releases are built by GitHub Actions from a tag, with `checksums.txt` and
  signed build provenance. Verify before uploading to Claude.ai:
  `gh attestation verify paranoid.zip --repo SandeepKomal/paranoid-sre`.
- Every GitHub Action is pinned to a full commit SHA and updated by
  Dependabot. Workflows default to read-only tokens.
- CI runs CodeQL, a gitleaks scan of the whole history, and OpenSSF
  Scorecard.

## Supported versions

Fixes go into the latest release. Please upgrade before reporting.
