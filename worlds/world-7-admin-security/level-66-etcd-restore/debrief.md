# Restore etcd

## What happened
A restore never writes into the running data directory. It creates a new one from the snapshot. Then you point etcd at it.

## Two ways to point etcd at the new dir
1. Change the `hostPath` of the `etcd-data` volume (done here). The path inside the container stays `/var/lib/etcd`, so `--data-dir` does not change.
2. Change both `--data-dir` and the volume mount. More edits, more chances for a typo.

## Things that go wrong
- Restoring into an existing directory fails. Pick a new path.
- The API server is down for a minute while etcd restarts. Wait with `crictl ps`, do not edit more.
- Everything created after the snapshot is gone. That is the point of a restore.

## Exam angle
- `etcdutl snapshot restore` needs no endpoint or certs.
- Note the old path before you edit, so you can undo.
- Check with `k get` on the object the task names.

Bookmark: https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/#restoring-an-etcd-cluster

Your notes: Backup and Restore, Control Plane
