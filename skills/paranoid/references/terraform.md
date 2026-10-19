# Terraform, OpenTofu, Terragrunt and Pulumi

Everything here applies to `tofu` as well as `terraform`.

## Where am I

```bash
terraform workspace show          # TF_WORKSPACE overrides this if set
echo "$TF_WORKSPACE"
grep -A5 'backend' *.tf           # which state this directory uses
terraform state list | head       # read-only: what this state manages
```

A directory can point at different state depending on `-backend-config`,
`TF_WORKSPACE`, `-chdir` and `TF_DATA_DIR`. Check all of them, in the
directory and shell the command will run in.

## Preview

```bash
terraform plan -out=tfplan        # or: terraform plan -destroy -out=tfplan
terraform show tfplan             # read the whole plan
terraform apply tfplan            # applies exactly what you reviewed
```

Applying a saved plan is the safest form: if the state changed since the
plan, Terraform refuses it instead of applying something different.

Read the plan for:

- `will be destroyed` and `must be replaced`. Replacement deletes the
  resource first unless `create_before_destroy` is set.
- `forces replacement` next to an attribute: often a rename, a changed
  name prefix, a new availability zone or a changed engine version.
- The summary line `Plan: X to add, Y to change, Z to destroy.` If Z is not
  what the user expects, stop.
- Resources holding data: databases (`aws_db_instance`, `aws_rds_cluster`,
  `google_sql_database_instance`, `azurerm_*_server`), disks and volumes,
  buckets, file systems, KMS keys, secrets, DNS zones.

A rename or a module move shows as destroy plus create. Use a `moved` block
(Terraform 1.1+) or `terraform state mv` so the resource keeps its identity.

## Commands that need step 4 and step 6

| Command | Why |
| --- | --- |
| `terraform destroy`, `apply -destroy` | deletes everything in the state |
| `terraform apply` with destroys or replacements in the plan | deletes those resources |
| `terraform state rm` | Terraform forgets the resource; the next apply may create a duplicate |
| `terraform state push` | overwrites remote state |
| `terraform state mv`, `import` | changes what the next plan does |
| `terraform force-unlock` | another run may still be writing the state |
| `terraform workspace delete` | drops the workspace's state |
| `terraform taint` / `apply -replace=...` | forces a delete and re-create |

Before any state command, save a copy:

```bash
terraform state pull > "state-backup-$(date +%Y%m%d-%H%M%S).tfstate"
```

## Safety rails to respect

- `lifecycle { prevent_destroy = true }`: leave it. If the plan fails on it,
  report that to the user instead of removing it.
- `deletion_protection` (AWS RDS, GCP SQL and instances, many others):
  never set it to false as part of an unrelated change.
- `skip_final_snapshot = true` on a database the user wants to delete:
  point it out and suggest a final snapshot.
- Remote state locks: a lock usually means someone else is running. Wait
  and ask; do not `force-unlock`.

## Terragrunt

- `terragrunt plan` / `apply` work on one module, like Terraform.
- `terragrunt run-all apply|destroy` (or `--all`) runs across every module
  below the directory. Plan each affected module, or run
  `terragrunt run-all plan`, and show the user the list of modules first.
- Dependencies between modules mean a destroy can fail half way. Know the
  order before starting.

## Pulumi

```bash
pulumi stack --show-name          # or pulumi stack ls
pulumi preview --diff             # what up would do
pulumi preview --diff --refresh   # include drift
```

- `pulumi up --yes` and `pulumi destroy --yes` skip the confirmation; use
  them only after a preview in this session.
- `pulumi stack rm` deletes the stack and its state.
- `pulumi state delete` makes Pulumi forget a resource without deleting it.
- `protect: true` on a resource blocks deletion; do not unprotect it to get
  a command through.
