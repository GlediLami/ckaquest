# Install the CNI

## What happened
Kubernetes does not ship a pod network. The kubelet reports NotReady until a CNI plugin writes its config to `/etc/cni/net.d`. Calico runs as a DaemonSet (calico-node) and assigns pod IPs from its IP pool.

If the pool does not match `--pod-network-cidr`, kube-proxy and the CNI disagree about which IPs are pods. That causes hard-to-find routing problems.

## Exam angle
- Expect "install a CNI that supports NetworkPolicy" or "install from this manifest". Calico and Cilium support policies. Flannel does not.
- With the Tigera operator install, the CIDR lives in the `Installation` resource instead.

Bookmark: https://kubernetes.io/docs/concepts/cluster-administration/addons/

Your notes: CNI, Pod Networking
