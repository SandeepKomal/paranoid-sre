# AWS, Google Cloud and Azure

Cloud CLIs act immediately. Most deletes cannot be undone, and few commands
have a dry run, so describe or list the exact resources first.

## AWS

```bash
aws sts get-caller-identity       # which account and role
aws configure list                # which profile, region and where they come from
echo "$AWS_PROFILE $AWS_REGION"
```

`--profile` and `--region` on the command win over the environment.

Preview and check first:

- `--dry-run` on EC2 calls such as `terminate-instances`, `run-instances`
  and `modify-instance-attribute`: a `DryRunOperation` error means it
  would have worked.
- `aws s3 rm s3://bucket/path --recursive --dryrun` and
  `aws s3 sync ... --delete --dryrun` list what would be removed.
- `describe-*` / `list-*` / `get-*` the exact resource before deleting it.

Data and recovery:

- RDS: take a snapshot before deleting or modifying in place
  (`aws rds create-db-snapshot`). Do not use `--skip-final-snapshot` or
  `--delete-automated-backups` unless asked. Do not turn off
  `--deletion-protection` to get a delete through.
- S3: check `aws s3api get-bucket-versioning --bucket X`. Without
  versioning, deleted objects are gone. `aws s3 rb --force` deletes every
  object first.
- DynamoDB: check point-in-time recovery with
  `aws dynamodb describe-continuous-backups --table-name X`.
- KMS: `schedule-key-deletion` makes everything encrypted with the key
  unreadable after the waiting period. Ask, and suggest `disable-key`
  instead.
- CloudFormation: `delete-stack` deletes every resource in the stack;
  `create-change-set` previews updates.

## Google Cloud

```bash
gcloud config list                # account, project and the active configuration
gcloud config configurations list
```

`--project`, `--configuration`, `CLOUDSDK_CORE_PROJECT` and an earlier
`gcloud config set project` change the target.

- `gcloud ... describe` the resource before `delete`.
- Cloud SQL: `gcloud sql backups create --instance=X` before risky changes.
  Deletion protection is set with `--deletion-protection`; leave it on.
- Compute: `deletion-protection` on instances; disks may be deleted with
  the instance (`--delete-disks`, `auto-delete`).
- Storage: `gcloud storage rm -r` / `gsutil rm -r` and `gsutil rsync -d`
  delete objects. Check object versioning and soft delete on the bucket.
- Deleting a project (`gcloud projects delete`) shuts everything in it down.

## Azure

```bash
az account show                   # subscription and tenant
az account list -o table
```

`--subscription`, `-g` / `--resource-group` and an earlier
`az account set` change the target.

- `az group delete` deletes every resource in the group. List them first
  with `az resource list -g X -o table`.
- `az deployment group what-if` previews ARM and Bicep deployments.
- Resource locks (`az lock list`) exist to stop deletes; do not remove them
  to get a command through.
- Key Vault and many storage services have soft delete; `purge` removes
  the soft-deleted copy for good.

## IAM, network and DNS

Treat these as irreversible even though they can be edited back: a wrong
change locks people out or takes services down at once.

- IAM and RBAC: show the current policy before changing it, change one
  binding at a time, and never widen your own permissions to finish a task.
- Security groups and firewall rules: removing a rule can cut off traffic,
  adding `0.0.0.0/0` exposes the service. Show the before and after.
- DNS: note the current record and TTL before changing it; a bad record
  can take hours to clear from caches.
