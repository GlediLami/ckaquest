# Broken kubeconfig

## What happened
A kubeconfig has three lists (clusters, users, contexts) and one `current-context`. A context joins one cluster, one user and an optional namespace.

Two faults: `current-context` named a context that does not exist, and the cluster server had the wrong port.

## Read-only commands that always work
- `kubectl config view` (add `--raw` to see cert data)
- `kubectl config get-contexts`
- `kubectl config current-context`

## Exam angle
- Every exam task starts with a `kubectl config use-context` line. Run it every time.
- Fixes: `kubectl config set-cluster <name> --server=...`, `kubectl config use-context`, `kubectl config set-context --current --namespace=...`.
- The admin kubeconfig on a kubeadm control plane is `/etc/kubernetes/admin.conf`. Compare with it.

Bookmark: https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/

Your notes: KubeConfig
