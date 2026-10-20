# Nothing Gets Scheduled

## What happened
The scheduler static pod ran a binary name with a typo, so it could not start. Without a scheduler, a new pod never gets `spec.nodeName`. It stays Pending with **no events**. That missing event is the clue. A pod that a scheduler rejected would show `FailedScheduling`.

## Static pods
- The kubelet on the control plane reads `/etc/kubernetes/manifests/` (the `staticPodPath` in the kubelet config) and runs every YAML in it.
- It creates a read-only "mirror pod" in the API, named `<pod>-<node>`. Deleting the mirror pod does nothing. You fix the file.
- After you save the file, the kubelet restarts the pod by itself. It can take 20 to 60 seconds.

## Exam traps
- Never keep a backup copy in `/etc/kubernetes/manifests/`. The kubelet runs it too. Copy backups to `/root/` or `/tmp/`.
- vim swap files are also in that folder while you edit. Save and quit cleanly.
- If kubectl itself stops working, use `crictl ps -a` and `crictl logs <id>` on the node.

## Your notes
- 14 Troubleshooting / Control Plane Failure
- 5 Scheduling / Static Pods
- 2 Components / Control Plane / kube-scheduler
