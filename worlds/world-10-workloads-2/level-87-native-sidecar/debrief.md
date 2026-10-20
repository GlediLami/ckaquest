# A Sidecar That Starts First

## What happened
Since Kubernetes 1.29 (GA in 1.33), an init container with `restartPolicy: Always` is a sidecar. It starts before the app containers, keeps running, is restarted if it dies, and stops after them. Jobs finish even though the sidecar never exits.

## Old way versus native
- A plain second container has no start order and keeps Jobs from completing.
- A native sidecar has a start order, has probes, and lets Jobs end.

## Exam angle
- "Add a sidecar" in a current exam means this pattern.
- `k logs <pod> -c <container>` for each container.

Bookmark: https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/

Your notes: Multi-Container Pods
