# Every Node, Really Every Node

## What happened
A DaemonSet places one pod per eligible node. The control plane has a NoSchedule taint, so without a toleration the DaemonSet skips it. DaemonSets get some tolerations automatically (not-ready, unreachable, disk-pressure), but not this one.

## Exam angle
- The Deployment-to-DaemonSet edit is the standard trick.
- `k get ds` shows DESIRED, CURRENT, READY. DESIRED counts nodes that match.
- Do not remove the control plane taint unless the task says so.

Bookmark: https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/

Your notes: Workloads, Taints and Tolerations
