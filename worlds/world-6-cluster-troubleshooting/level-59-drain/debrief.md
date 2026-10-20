# Maintenance Window

## What drain does
1. Cordon: `spec.unschedulable: true`. New pods do not land on the node.
2. Evict every pod through the Eviction API, which respects PodDisruptionBudgets.
3. Refuse to continue on: DaemonSet pods (needs `--ignore-daemonsets`), pods without a controller (needs `--force`, they are gone for good), pods with emptyDir (needs `--delete-emptydir-data`).

## The PDB trap
`minAvailable: 2` with 2 replicas means 0 allowed disruptions. Drain retries the eviction forever. The fix is a PDB that allows one pod to go: `minAvailable: 1` or `maxUnavailable: 1`. Then drain evicts one pod, waits for its replacement on another node, and evicts the next.

## Maintenance flow in the exam
`kubectl drain <node> --ignore-daemonsets` then do the work (often a kubeadm upgrade), then `kubectl uncordon <node>`. Read the task: here it said to leave the node cordoned.

## Your notes
- 8 Cluster Maintenance / Node Maintenance
- 3 Objects / Workloads / DaemonSet
