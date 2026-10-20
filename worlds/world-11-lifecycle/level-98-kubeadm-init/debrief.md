# kubeadm init

## What happened
`kubeadm init` runs preflight checks, creates the CA and certificates in `/etc/kubernetes/pki`, writes kubeconfigs, writes static pod manifests for etcd, apiserver, controller-manager and scheduler, starts the kubelet, and installs CoreDNS and kube-proxy.

The node stays NotReady until a CNI plugin is installed. CoreDNS stays Pending for the same reason.

## Flags worth knowing
- `--pod-network-cidr`: must match the CNI's pool.
- `--apiserver-advertise-address`: which IP the API server announces.
- `--control-plane-endpoint`: needed for HA later.
- `--kubernetes-version`.
- `--config` takes a ClusterConfiguration file instead of flags.

## Exam angle
- Save the join command from the output. You can always make a new one with `kubeadm token create --print-join-command`.

Bookmark: https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/

Your notes: Cluster Install (course section 11)
