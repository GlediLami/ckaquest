#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
K='kubectl --kubeconfig /etc/kubernetes/admin.conf'
check "tigera-operator Deployment is available" node_ok bare-controlplane "$K -n tigera-operator rollout status deploy/tigera-operator --timeout=5s"
check 2 "Installation default uses the pod CIDR 10.50.0.0/16" node_ok bare-controlplane "[ \"\$($K get installation default -o jsonpath='{.spec.calicoNetwork.ipPools[0].cidr}')\" = 10.50.0.0/16 ]"
check 2 "calico-node runs" node_ok bare-controlplane "[ \"\$($K -n calico-system get ds calico-node -o jsonpath='{.status.numberReady}' 2>/dev/null)\" -ge 1 ]"
check 2 "the node is Ready" node_ok bare-controlplane "$K get nodes --no-headers | grep -q ' Ready'" 
finish
