# Never on the Same Node

## What happened
Pod anti-affinity looks at the pods already on a node. `topologyKey: kubernetes.io/hostname` makes every node its own domain. So a node with one cache pod refuses a second one. With 2 workers the third pod has nowhere to go. That Pending pod is proof the rule works.

## The rollout trap
The label `app=cache` also matches the old pods. During a rolling update the new pod is not allowed next to an old one, and the old ones are not removed until new ones are ready. The rollout hangs. Ways out:
- scale to 0 first, or delete the old pods
- `strategy: Recreate`
- `maxUnavailable: 1` so an old pod can go first

## Required or preferred
- `requiredDuringScheduling...`: hard rule. Pods stay Pending.
- `preferredDuringScheduling...` with a `weight`: soft rule. The scheduler tries, but packs pods together if it must.
- `podAffinity` is the opposite: run next to matching pods.

## Exam angle
- "One pod per node" can mean anti-affinity, or a DaemonSet if every node needs one. Read the task.
- Copy the block from the docs page "Assigning Pods to Nodes".

Bookmark: https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/

Your notes: Scheduling
