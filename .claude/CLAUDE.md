# CLAUDE.md

Guidance for Claude (and other agents) working in this repository.

## What this is

paranoid-sre is an agent skill, `skills/paranoid/SKILL.md` plus reference
pages, packaged as a Claude Code plugin. Codex, Gemini CLI and GitHub
Copilot CLI load the same `SKILL.md` from `~/.agents/skills`, so keep the
skill free of anything only one agent understands. It makes an agent check
where it is, preview, find a way back and ask before changing
infrastructure or data. It pairs with [blast-radius](https://github.com/SandeepKomal/blast-radius), a
hook that enforces limits and whose dashboard shows this skill's steps.

## Checks

```bash
python3 scripts/check.py            # frontmatter rules and relative links
claude plugin validate . --strict   # plugin and marketplace manifests
```

Both run in CI, together with CodeQL, a gitleaks secret scan and OpenSSF
Scorecard.

## Rules for changing the skill

- Every command must be real and copy-pasteable. Recommend read-only checks
  and previews; anything that changes state must go through step 6 (ask).
- Never weaken the "ask before anything irreversible" step, the "Never,
  unless the user asks" list, or the personal data rules.
- Never add advice to work around a guard (blast-radius, policy engines,
  permission rules, hooks).
- Keep `SKILL.md` under 500 lines; tool detail goes in
  `skills/paranoid/references/<tool>.md`.
- Keep the frontmatter within what Claude.ai and the Skills API accept
  (`scripts/check.py` enforces it).
- blast-radius recognises the skill's steps from commands such as
  `terraform workspace show`, `kubectl config current-context`,
  `terraform plan`, `kubectl diff` and backups. If you change which commands
  the skill recommends, check its dashboard still recognises them.

## Releases

1. Update `CHANGELOG.md` and the `version` in `.claude-plugin/plugin.json`.
2. Merge to `main`, then either push a tag `vX.Y.Z` matching that version,
   or run the **release** workflow from the Actions tab with the version
   (`X.Y.Z`); it tags `main` itself once every check has passed.
3. The release workflow checks the skill, packages `paranoid.zip`, writes
   `checksums.txt`, attests build provenance and publishes the release.

## Repository hygiene

- GitHub Actions are pinned to full commit SHAs with the version in a
  comment; Dependabot updates them. Keep `persist-credentials: false` on
  checkouts and the narrowest `permissions`.
- Never commit secrets, real customer data or real account IDs in examples.
