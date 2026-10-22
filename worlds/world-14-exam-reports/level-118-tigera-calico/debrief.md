# Calico, the Operator Way

## What happened
The Tigera operator installs and manages Calico. You give it an `Installation` resource that describes what you want. The operator then creates the `calico-system` namespace, calico-node, typha and the kube-controllers.

The IP pool must match the cluster's pod CIDR. kubeadm writes it to kube-controller-manager as `--cluster-cidr`, from `--pod-network-cidr` at init. With a wrong pool, pods get addresses the rest of the cluster does not route.

## Operator or manifest
- Manifest (level 99): one big YAML, you edit `CALICO_IPV4POOL_CIDR` in the DaemonSet.
- Operator: two files, you edit the `Installation`. Upgrades go through the operator.

## Gotchas
- `kubectl create`, not `apply`. The CRDs are bigger than the `last-applied` annotation allows. `kubectl apply --server-side` also works.
- Calico supports NetworkPolicy. Flannel does not. A task that also needs policies wants Calico.

## Exam angle
- Reported with the Tigera docs link in the task. Read the CIDR from the cluster, do not guess.

Bookmark: https://docs.tigera.io/calico/latest/getting-started/kubernetes/self-managed-onprem/onpremises

Your notes: Networking, Cluster Install
