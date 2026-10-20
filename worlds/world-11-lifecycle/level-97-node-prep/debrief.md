# Prepare the Nodes

## What happened
Pods talk across nodes through Linux routing and bridges. `ip_forward` lets the node route packets. `br_netfilter` makes bridged traffic visible to iptables, which kube-proxy needs. `overlay` is the filesystem driver containerd uses.

Files in `/etc/modules-load.d` and `/etc/sysctl.d` make the settings survive a reboot. `modprobe` and `sysctl --system` apply them now.

## Also before kubeadm
- A container runtime with the systemd cgroup driver.
- Swap off, or kubelet configured to tolerate it.
- kubeadm, kubelet, kubectl from pkgs.k8s.io, held with `apt-mark hold`.

## Exam angle
- Node prep is in the curriculum ("prepare underlying infrastructure"). Copy the blocks from the container runtime docs page.

Bookmark: https://kubernetes.io/docs/setup/production-environment/container-runtimes/

Your notes: Cluster Install (course sections 10 and 11)
