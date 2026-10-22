# No Shell, No Problem

## What happened
Minimal images (distroless, scratch) have no shell, so `kubectl exec` has nothing to run. `kubectl debug` adds an **ephemeral container** to the running pod. With `--target=<container>` it joins that container's process namespace, so you see its processes, their environment (`/proc/<pid>/environ`) and their files (`/proc/<pid>/root`).

Ephemeral containers cannot be removed. They stay in the pod spec until the pod is deleted.

## Node debugging
`kubectl debug node/<name>` starts a pod on that node with the host's namespaces and the node's root filesystem at `/host`. It is the answer when ssh is not available. `chroot /host` gives you the node's own tools.

## Other modes
- `--copy-to=<new pod>`: a copy of the pod you can change, for example `--set-image` or a different command.
- `--profile=general|baseline|restricted|sysadmin`: how many privileges the debug container gets.

## Exam angle
- `kubectl debug` is part of "troubleshoot clusters and nodes". Know the three forms: ephemeral, copy, node.

Bookmark: https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/

Your notes: Troubleshooting
