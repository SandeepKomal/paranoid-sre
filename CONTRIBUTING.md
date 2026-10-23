# Contributing

The skill is only as good as its advice, so the most useful contributions
are corrections: a command that is wrong, a flag that doesn't exist on some
version, or a destructive case the skill doesn't warn about.

## Ground rules

- Every command in the skill must be real and copy-pasteable. Say which
  version it needs if it is recent.
- Prefer read-only checks and previews over advice to "be careful".
- Keep `SKILL.md` short. Tool-specific detail goes in
  `skills/paranoid/references/<tool>.md`, linked from the list at the end of
  `SKILL.md`.
- Write for the agent: short imperative sentences, no filler.

## Checks

```bash
python3 scripts/check.py            # frontmatter rules and links
claude plugin validate . --strict   # plugin and marketplace manifests
```

To fuzz the checker (Python 3.12 on Linux):

```bash
pip install --require-hashes --only-binary ":all:" -r fuzz/requirements.txt
python fuzz/fuzz_check.py -max_total_time=60 fuzz/corpus
```

CI runs both on every pull request.

## Trying a change

```bash
mkdir -p ~/.claude/skills
cp -r skills/paranoid ~/.claude/skills/
```

Then give Claude a task in a sandbox, for example "delete the old pods in
this namespace", and check that it follows the steps.
