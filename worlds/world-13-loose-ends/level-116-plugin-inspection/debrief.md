# What Runs Under the Hood

## What happened
Kubernetes plugs three things in through standard interfaces:
- **CRI** (container runtime): the kubelet talks gRPC to containerd, CRI-O or cri-dockerd through `containerRuntimeEndpoint`. `crictl` uses the same socket.
- **CNI** (network): the container runtime runs the first config file in `/etc/cni/net.d`, sorted by name, using the binaries in `/opt/cni/bin`. kind uses kindnet with the `ptp` plugin. Calico, Cilium and Flannel drop their own file there.
- **CSI** (storage): drivers register a CSIDriver object and run as pods. This cluster has none, because local-path is an older in-tree style provisioner. That is why expansion and snapshots do not work here.

## Where to look
- Kubelet: `/var/lib/kubelet/config.yaml`, `/var/lib/kubelet/kubeadm-flags.env`, `systemctl cat kubelet`.
- Runtime: `k get nodes -o wide`, `crictl info`.
- Network: `/etc/cni/net.d`, `/opt/cni/bin`, the CNI DaemonSet in kube-system.
- Storage: `k get csidriver`, `k get sc`.

## Exam angle
- The curriculum names CNI, CSI and CRI. Expect "find out and write to a file" questions like this one.
- Answer files are checked as text. No spaces, no extra lines.

Bookmark: https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/network-plugins/

Your notes: Cluster Architecture
