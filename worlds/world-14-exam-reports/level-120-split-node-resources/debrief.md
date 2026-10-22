# Fair Shares

## What happened
The scheduler only looks at **requests**, never at real usage. A pod fits on a node when its requests fit into allocatable capacity minus what the pods already there request.

A pod's request is the larger of two values: the sum of its containers, or its biggest init container. Init containers run before the others, so their requests do not add up.

## The math
1. `k describe node node01`: Allocatable, and "Allocated resources" for the other pods.
2. Free = allocatable minus requests of the others.
3. Per pod = free / replicas, minus some headroom.
4. If a pod stays Pending, `k describe pod` says "Insufficient cpu" or "memory". Lower the request a little.

## The rollout trap
With a RollingUpdate, the new pods start before the old ones go. On a full node they cannot fit. Scale to 0 first, or set the requests before scaling up.

## Exam angle
- Reported: "divide node resources evenly across 3 replicas, with the same requests for init and main". Candidates say fixed rules like "leave 10%" did not always work. Read the node.
- `k set resources` is faster than editing YAML.

Bookmark: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/

Your notes: Scheduling
