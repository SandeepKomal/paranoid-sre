# paranoid-sre

[![ci](https://github.com/SandeepKomal/paranoid-sre/actions/workflows/ci.yml/badge.svg)](https://github.com/SandeepKomal/paranoid-sre/actions/workflows/ci.yml)
[![license](https://img.shields.io/github/license/SandeepKomal/paranoid-sre)](LICENSE)

A Claude skill that makes the agent handle infrastructure like a careful SRE:
check which environment it is in, preview the change, find a way back, and
ask before anything it can't undo.

Ask an agent to "clean up the old servers" and it will often just run the
delete. With this skill it works through the steps an experienced engineer
would, and comes back with something like:

```
Target:    AWS account 1234-5678-9012 (prod), us-east-1
Change:    terminate 3 instances: web-old-1, web-old-2, batch-legacy
Data loss: batch-legacy has an attached volume that is deleted with it
Way back:  none for the volume; I can snapshot it first
Command:   aws ec2 terminate-instances --instance-ids i-0a1 i-0b2 i-0c3
```

and waits for your answer.

## What it makes Claude do

1. **Find out where it is.** Workspace, kube context, cloud account,
   project or subscription, database host, checked with read-only commands.
   Anything it can't identify is treated as production.
2. **Preview the change** with the tool's own dry run: `terraform plan`,
   `kubectl diff`, `--dry-run=server`, `helm get manifest`,
   `pulumi preview`, `SELECT count(*)`.
3. **Rate it**: read-only, reversible, or irreversible. Replacements count
   as deletions; a namespace or resource group counts as everything in it.
4. **Make sure there is a way back**: backups, snapshots, deletion
   protection, versioning, a rollback command written down in advance.
5. **Keep it small**: named resources instead of wildcards, one
   environment and one changing command at a time.
6. **Ask before anything irreversible**, showing target, change, data loss,
   way back and the exact command. "Quickly" and "it's only staging" don't
   skip this.
7. **Watch the result** and stop if anything is unexpected, instead of
   retrying with `--force`.

It also lists what Claude must never do unless you ask for that exact
action, such as turning off deletion protection, skipping final snapshots,
force-unlocking state, removing finalizers, widening its own IAM
permissions, or working around a guard that blocked it.

Covers Terraform, OpenTofu, Terragrunt, Pulumi, Kubernetes, Helm, AWS,
Google Cloud, Azure and SQL databases, with a reference page for each in
[skills/paranoid/references](skills/paranoid/references).

## Install

### Claude Code plugin

```
/plugin marketplace add SandeepKomal/paranoid-sre
/plugin install paranoid-sre@paranoid-sre
```

Or from a terminal:

```bash
claude plugin marketplace add SandeepKomal/paranoid-sre
claude plugin install paranoid-sre@paranoid-sre
```

### Copy the skill

For yourself:

```bash
git clone https://github.com/SandeepKomal/paranoid-sre
mkdir -p ~/.claude/skills
cp -r paranoid-sre/skills/paranoid ~/.claude/skills/
```

For everyone working in a repository, copy `skills/paranoid` to
`.claude/skills/paranoid` in that repository and commit it.

### Claude.ai and the API

Each [release](https://github.com/SandeepKomal/paranoid-sre/releases) has a
`paranoid.zip` you can upload as a skill in Claude.ai, or send to the
[Skills API](https://platform.claude.com/docs/en/api/skills-guide).

## When it is used

Claude loads the skill on its own when a task involves changing
infrastructure or data: `terraform apply`, `kubectl delete`,
`helm uninstall`, cloud CLI changes, migrations, `DROP` and `DELETE`
statements, IAM, DNS and firewall changes, or requests to clean up, tear
down, reset or fix an environment. You can also call it directly with
`/paranoid-sre:paranoid` (or `/paranoid` when copied as a skill).

## Pair it with blast-radius

A skill is instructions. It makes Claude careful, but it can't stop a
command. [blast-radius](https://github.com/SandeepKomal/blast-radius) is a
hook that does: it previews what each command would destroy, asks for
approval, and blocks deletions in production. The skill uses
`blast-radius check` for previews when it is installed.

| | paranoid-sre | blast-radius |
| --- | --- | --- |
| What it is | Skill (instructions) | Hook (program) |
| When it acts | While Claude plans | Just before a command runs |
| Can Claude ignore it | It follows it like any instruction | No |

To set up both:

```bash
go install github.com/sandeepkomal/blast-radius@latest   # or download a release
blast-radius install
claude plugin marketplace add SandeepKomal/paranoid-sre
claude plugin install paranoid-sre@paranoid-sre
```

## Limitations

- It guides the agent; it does not enforce anything. Use blast-radius,
  Claude Code's permission rules and least-privilege credentials for hard
  limits.
- Asking before irreversible changes means more questions. That is the
  point, but it is slower for routine work in sandboxes.

## Contributing

Corrections and new reference pages are welcome. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
