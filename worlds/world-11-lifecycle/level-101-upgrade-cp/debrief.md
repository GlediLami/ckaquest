# Upgrade the Control Plane

## What happened
kubeadm upgrades in a fixed order: kubeadm itself, then the control plane static pods (`upgrade apply`), then the kubelet on each node. The kubelet may be one minor version behind the API server, never ahead.

`kubeadm upgrade apply` also renews the control plane certificates.

## Rules to remember
- One minor version at a time: 1.36 to 1.37, never 1.35 to 1.37.
- Control plane first, then workers.
- Drain before the kubelet upgrade, uncordon after.
- `kubeadm upgrade apply` only on the first control plane. Other control planes and workers use `kubeadm upgrade node`.

## Exam angle
- The apt version format is `1.37.1-1.1`. Use `apt-cache madison` to see it, or `'1.37.1-*'`.
- The upgrade task is often worth more points and takes 10 minutes. Practice until it is routine.

Bookmark: https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/

Your notes: Cluster Upgrade
