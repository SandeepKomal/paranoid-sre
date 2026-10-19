# Kubernetes and Helm

## Where am I

```bash
kubectl config current-context
kubectl config view --minify -o jsonpath='{..namespace}'   # empty means "default"
kubectl get nodes                                          # sanity check: is this the cluster you expect?
```

`--context`, `--kubeconfig`, `KUBECONFIG`, `-n` and `--namespace` on the
command itself override all of this. So does an earlier
`kubectl config use-context` or `kubectx` in the same script.

## Preview

```bash
kubectl diff -f manifest.yaml                 # what apply would change
kubectl apply -f manifest.yaml --dry-run=server
kubectl delete deploy web -n shop --dry-run=server
kubectl get deploy,svc -l app=web -n shop     # what a selector matches, before deleting by it
```

Before deleting something, save it:

```bash
kubectl get deploy web -n shop -o yaml > web-backup.yaml
```

## What deletes more than it looks like

| Command | What goes with it |
| --- | --- |
| `kubectl delete namespace X` | every object in X, including PVCs and secrets |
| `kubectl delete pvc` | the volume's data, if the PersistentVolume's reclaim policy is `Delete` |
| `kubectl delete -f dir/` | everything in every file in the directory |
| `kubectl delete ... --all` / `-l` | everything matching, in the namespace or across namespaces with `-A` |
| `kubectl apply --prune` | objects with the label that are not in the files |
| `kubectl delete crd` | every custom resource of that type, in every namespace |
| `kubectl scale --replicas=0` | the service is down until scaled back |
| `kubectl drain` | evicts every pod on the node |
| `kubectl replace --force` | deletes and re-creates the object |

Check the reclaim policy before deleting a PVC:

```bash
kubectl get pv -o custom-columns=NAME:.metadata.name,CLAIM:.spec.claimRef.name,POLICY:.spec.persistentVolumeReclaimPolicy
```

## Safer ways to do the same thing

- `kubectl rollout restart deploy/web` instead of deleting pods.
- `kubectl rollout undo deploy/web` to go back; `kubectl rollout history`
  shows the revisions.
- `kubectl cordon node` before `drain`, and check PodDisruptionBudgets
  (`kubectl get pdb -A`) first. Never `--disable-eviction` or
  `--delete-emptydir-data` without saying what it does.
- Scale down before deleting a workload, so the user can see nothing
  breaks before the delete.

## Never, without being asked for that exact action

- `--grace-period=0 --force` on pods (can corrupt data in stateful apps).
- Removing finalizers to get a stuck object deleted.
- Editing RBAC to get past a "forbidden" error.

## Helm

```bash
helm list -A
helm status web -n shop
helm get values web -n shop > web-values-backup.yaml
helm get manifest web -n shop          # every object an uninstall removes
helm history web -n shop               # revisions available for rollback
helm upgrade web ./chart -n shop --dry-run
helm diff upgrade web ./chart -n shop  # if the helm-diff plugin is installed
```

- `helm uninstall` removes every object in the release manifest. PVCs
  created by StatefulSet volume claim templates are usually kept, but
  check.
- `helm upgrade --install` creates the release if it does not exist: make
  sure the namespace and release name are the ones you mean.
- `helm rollback web <revision>` goes back to an earlier revision.
- `--force` on upgrade deletes and re-creates resources that fail to patch.
