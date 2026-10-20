# Back Up etcd

## What happened
etcd holds the whole cluster state. A snapshot is a single file you can restore later.

## Where the flags come from
The etcd manifest at `/etc/kubernetes/manifests/etcd.yaml`:
- `--listen-client-urls` gives the endpoint.
- `--trusted-ca-file` gives `--cacert`.
- `--cert-file` and `--key-file` give `--cert` and `--key`. The `healthcheck-client` or `apiserver-etcd-client` pairs work too.

## etcdctl or etcdutl
Since etcd 3.5, `etcdutl` does the offline work: `snapshot status` and `snapshot restore`. `etcdctl` talks to a running etcd and does `snapshot save`. Old commands like `etcdctl snapshot restore` still print a deprecation warning. Both work in the exam.

## Exam angle
- Copy the cert paths from the manifest. Do not type them from memory.
- `ETCDCTL_API=3` is the default now. Setting it does no harm.
- Write to exactly the path the task names.

Bookmark: https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/

Your notes: Backup and Restore
