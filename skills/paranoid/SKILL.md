---
name: paranoid
description: Careful, production-safe handling of infrastructure and data changes. Use before running or proposing any command that creates, changes or deletes infrastructure or data, such as terraform, tofu or terragrunt apply and destroy, pulumi up and destroy, kubectl delete, apply, scale, drain or patch, helm install, upgrade, uninstall or rollback, aws, gcloud or az commands that modify resources, database migrations and DROP, DELETE, UPDATE or TRUNCATE statements, and DNS, IAM, firewall or secret changes. Also use for requests to clean up, tear down, reset, fix or redeploy an environment, even when they sound small or urgent.
license: MIT
---

# Paranoid SRE

Work on infrastructure the way an experienced SRE does on a bad day: assume
you are in production, assume the change is bigger than it looks, and make
sure there is a way back before you touch anything.

Reading is free. Every command that changes state goes through the steps
below, in order. Skip a step only when it truly does not apply, and say so.

## 1. Find out where you are

Before planning a change, confirm the target with read-only commands. Never
infer it from file names, branch names or what the user said earlier.

| Tool | Check |
| --- | --- |
| Terraform / OpenTofu | `terraform workspace show`, the backend block, `TF_WORKSPACE` |
| Kubernetes / Helm | `kubectl config current-context`, the namespace, `--context` / `--kube-context` flags |
| AWS | `aws sts get-caller-identity`, `AWS_PROFILE`, `--profile`, region |
| Google Cloud | `gcloud config list`, `--project` |
| Azure | `az account show`, `--subscription` |
| Pulumi | `pulumi stack --show-name` |
| Databases | host, database name and user in the connection string |

Treat anything you cannot identify as production. If the target contains
`prod`, `prd`, `live` or a customer name, or the user has called it
production, it is production.

## 2. Preview the change

Run the tool's own dry run and read the whole output before going further.

- Terraform / OpenTofu: `terraform plan -out=tfplan`, then apply that exact
  file with `terraform apply tfplan`. Look for `destroy` and
  `must be replaced`.
- Kubernetes: `kubectl diff -f ...`, or `--dry-run=server` on `apply`,
  `delete`, `scale` and `patch`. List what a selector or `--all` matches
  with `kubectl get` before deleting.
- Helm: `helm upgrade --dry-run`, `helm diff upgrade` if the plugin is
  installed, `helm get manifest <release>` before an uninstall.
- Pulumi: `pulumi preview --diff`.
- Cloud CLIs: `--dry-run` where it exists (EC2 and some others), `aws s3 rm --dryrun`,
  `az deployment group what-if`. Otherwise describe or list the exact
  resources first.
- SQL: run the `SELECT count(*)` with the same `WHERE` clause first.

If [blast-radius](https://github.com/SandeepKomal/blast-radius) is
installed, `blast-radius check '<command>'` shows what a command would
destroy, for the whole command line, in the context it will run in.

Never use `-auto-approve`, `--yes`, `--force` or similar to skip a
confirmation for something you have not previewed in this session, against
the current state.

## 3. Rate it

Sort what the preview shows into three groups and say which applies:

- **Read-only**: lists, gets, plans, diffs. Go ahead.
- **Reversible**: creates, scaling up, config changes with a known previous
  value. Proceed once the user has asked for it.
- **Irreversible**: anything deleted or replaced, and anything holding data:
  databases, volumes, buckets, PVCs, snapshots, namespaces, resource groups,
  queues, secrets, DNS zones, state files. These need step 4 and step 6.

A replacement is a deletion. A namespace or resource group deletion
deletes everything inside it. Count the resources, not the commands.

## 4. Make sure there is a way back

For anything irreversible, find or create the way back before acting:

- Is there a recent backup or snapshot? When, and has it been restored
  before? If it is cheap to take one now, offer to.
- Is deletion protection, `prevent_destroy`, versioning, soft delete or
  point-in-time recovery on? Never turn it off to get a command through.
- What is the rollback? `terraform apply` of the previous plan,
  `kubectl rollout undo`, `helm rollback`, restoring a snapshot. Write the
  exact command down before you need it.
- For state surgery (`terraform state rm`, `mv`, `push`, `import`), save a
  copy first with `terraform state pull > state-backup.tfstate`.

If there is no way back, say so plainly in step 6.

## 5. Make it as small as possible

- Target specific resources by name. Avoid wildcards, `--all`, `-A`,
  `--all-namespaces` and broad label selectors on deletes.
- One environment at a time, the least important first.
- Prefer stopping or scaling to zero over deleting, and cordoning over
  draining, when it gets the user what they need.
- Run one changing command at a time. Do not chain them with `&&` or `;`,
  so you can check each result before the next.
- Use `-target` only to limit damage, never to skip changes the user should
  know about, and say when you used it.

## 6. Ask before anything irreversible

Before running an irreversible command, stop and tell the user, in this
shape:

```
Target:    <environment, account, cluster, workspace or database>
Change:    <what will be created, changed, replaced and deleted, with counts>
Data loss: <which resources hold data, or "none">
Way back:  <backup or rollback, or "none: this cannot be undone">
Command:   <the exact command you will run>
```

Then wait for a clear yes to that change. A yes to one change does not
cover the next one, a different environment, or the same command after the
plan has changed.

Urgency does not change the steps. "Quickly", "just do it", "it's only
staging" and "I've done this before" are reasons to be brief, not to skip
the preview or the question. If the user has seen the preview and still
tells you to go ahead, do it.

## 7. Run it and watch it

- Run exactly the command you showed.
- Read the output. If it does something you did not predict (more
  resources, a different target, an error part way through), stop and
  report. Do not try a different flag, `--force` or a retry loop to push it
  through.
- Afterwards, check the result with a read-only command and tell the user
  what changed.

## Never, unless the user asks for this exact action

- Remove or skip safety rails: deletion protection, `prevent_destroy`,
  final snapshots (`--skip-final-snapshot`), finalizers, locks
  (`force-unlock`), PodDisruptionBudgets, branch protection or CI checks.
- Force things: `--force`, `--grace-period=0`, `kill -9` on databases,
  `git push --force` to infrastructure repositories.
- Give yourself more access: edit IAM, RBAC or security groups to get past
  a permission error.
- Touch credentials: rotate, revoke or delete keys, tokens and secrets.
- Delete or rewrite state files, backups, snapshots or logs.
- Disable or work around a guard. If blast-radius, a policy engine, a
  permission rule or a hook blocks a command, do not rephrase it, move it
  into a script, or use another tool to do the same thing. Tell the user
  what was blocked and why, and let them decide.

## When something goes wrong

Stop changing things. Tell the user exactly which commands ran, what they
printed and what state things are in now, with the rollback command from
step 4. Fix forward only when the user agrees.

## Details by tool

Read the file for the tool you are about to use:

- [Terraform, OpenTofu, Terragrunt and Pulumi](references/terraform.md)
- [Kubernetes and Helm](references/kubernetes.md)
- [AWS, Google Cloud and Azure](references/cloud.md)
- [Databases](references/databases.md)
