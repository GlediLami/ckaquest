# Even Across Zones

## What happened
A topology domain is every node with the same value of a label. `maxSkew: 1` means the pod count in the fullest and the emptiest domain may differ by at most 1. `DoNotSchedule` makes it a hard filter, so it beats the preferred node affinity, which only adds points.

Without zone labels the nodes are not in any domain. Real cloud nodes get `topology.kubernetes.io/zone` from the cloud provider. Here you set it yourself.

## The rollout detail
The scheduler only checks the spread when it places a pod. During a rolling update the old pods still count, so the final spread can end up uneven. `matchLabelKeys: [pod-template-hash]` limits the count to pods of the same ReplicaSet.

## Spread, anti-affinity or DaemonSet
- Anti-affinity: at most one per domain.
- Topology spread: as even as possible, many per domain allowed.
- DaemonSet: exactly one per node.

## Exam angle
- The docs page "Pod Topology Spread Constraints" has a full example.
- Check with `k get pods -o wide` and count per node.

Bookmark: https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/

Your notes: Scheduling
