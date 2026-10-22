# A Chart on Disk

## What happened
A chart can come from a repo (`repo/chart`), an archive (`chart.tgz`), a URL or a plain directory. Helm reads `Chart.yaml`, `values.yaml` and `templates/` the same way.

`-n` only picks the namespace. If it does not exist, the install fails unless you add `--create-namespace`.

## Overrides
- `--set a.b=c`: one value, nested with dots.
- `-f my-values.yaml`: many values. Later files win.
- `helm get values <release>`: what you set. Add `-a` for everything.

## Exam angle
- Read `values.yaml` for the exact key names. `replica_count` and `replicaCount` are different keys, and a wrong one is ignored without an error.

Bookmark: https://helm.sh/docs/helm/helm_install/

Your notes: Helm Basics
