# Just Below the Top

## What happened
A PriorityClass maps a name to a number. Pods with a higher priority are scheduled first and can preempt lower ones when the cluster is full. The built-in `system-cluster-critical` and `system-node-critical` sit far above every user class (2,000,000,000 and more). Never compete with them.

Admission writes the value into `pod.spec.priority` when the pod is created. Changing the Deployment rolls new pods with the new priority.

## kubectl patch
- strategic merge (default): `-p '{"spec":{...}}'`, merges like `apply`.
- `--type=merge`: plain JSON merge.
- `--type=json`: a list of operations, for list items and removals.

## Exam angle
- Reported: "a PriorityClass one less than the highest user-defined one, add it to a Deployment with kubectl patch only".
- `k get pc --sort-by=.value` gives the number fast.

Bookmark: https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/

Your notes: Scheduling
