# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[semantic versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-10-23

### Added

- A "Personal data and secrets" section in the skill: count instead of
  printing customer data, never copy production personal data elsewhere,
  never print secrets, and treat deleting personal data as irreversible.
- `docs/privacy.md` with a checklist for India's DPDP Act.
- README: screenshots of the skill's steps in the blast-radius dashboard,
  step-by-step install, how it works with blast-radius, and a trust and
  security checklist.
- `SECURITY.md`, `CODE_OF_CONDUCT.md` and `.claude/CLAUDE.md`.

### Security

- CodeQL, a gitleaks secret scan of the whole history and OpenSSF Scorecard
  run in CI.
- GitHub Actions are pinned to commit SHAs, checkouts don't keep
  credentials, and the Claude Code version used to validate the plugin is
  pinned.
- Releases include `checksums.txt` and signed build provenance for
  `paranoid.zip`.

## [0.1.0] - 2026-10-19

First release.

### Added

- The `paranoid` skill: find the environment, preview, rate, find a way back,
  keep the change small, ask before anything irreversible, and watch the result.
- Reference pages for Terraform, OpenTofu, Terragrunt and Pulumi; Kubernetes and
  Helm; AWS, Google Cloud and Azure; and SQL databases.
- Claude Code plugin and marketplace manifests.
- `paranoid.zip` on each release for Claude.ai and the Skills API.

[Unreleased]: https://github.com/SandeepKomal/paranoid-sre/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/SandeepKomal/paranoid-sre/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/SandeepKomal/paranoid-sre/releases/tag/v0.1.0
