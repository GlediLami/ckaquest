#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
K='kubectl --kubeconfig /etc/kubernetes/admin.conf'
cq_node_sh bare-controlplane "$K create -f /root/tigera-operator.yaml >/dev/null
cidr=\$(grep -o -- '--cluster-cidr=[^ ]*' /etc/kubernetes/manifests/kube-controller-manager.yaml | cut -d= -f2)
sed -i \"s#cidr: .*#cidr: \$cidr#\" /root/custom-resources.yaml
$K -n tigera-operator rollout status deploy/tigera-operator --timeout=180s >/dev/null
for i in \$(seq 60); do $K create -f /root/custom-resources.yaml >/dev/null 2>&1 && break; $K get installation default >/dev/null 2>&1 && break; sleep 5; done
$K get installation default >/dev/null"
ready() { cq_node_sh bare-controlplane "$K get nodes --no-headers | grep -q ' Ready'"; }
cq_wait 600 ready
