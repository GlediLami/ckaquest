# Upgrade the Worker

## What happened
`kubeadm upgrade node` on a worker only updates the local kubelet config. The real change is the new kubelet binary and its restart.

## Exam angle
- Drain and uncordon run where kubectl has admin access, usually the control plane.
- After `exit` from the worker, check that you are back on the right host before you uncordon.
- A worker can stay one minor version behind for a while, so do the control plane first and the workers one by one.

Bookmark: https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/upgrading-linux-nodes/

Your notes: Cluster Upgrade, Node Maintenance
