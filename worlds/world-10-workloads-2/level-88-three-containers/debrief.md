# Three in One

## What happened
Containers in a pod share the network namespace (localhost) and can share volumes. They do not share a filesystem otherwise.

## Downward API
`fieldRef` exposes pod fields as env vars: `metadata.name`, `metadata.namespace`, `spec.nodeName`, `status.podIP`. `resourceFieldRef` exposes requests and limits.

## Exam angle
- Generate one container with `k run $do`, then copy and edit. Faster than typing three.
- Wrong indentation under `containers:` is the usual error. `k apply --dry-run=server -f` catches it.

Bookmark: https://kubernetes.io/docs/tasks/access-application-cluster/communicate-containers-same-pod-shared-volume/

Your notes: Multi-Container Pods, Environment Variables
