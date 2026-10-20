#!/usr/bin/env bash
set -euo pipefail
source "$CQ_ROOT/lib/common.sh"
cq_node_backup node02 /var/lib/kubelet/config.yaml
cq_node_sh node02 "sed -i 's|clientCAFile: /etc/kubernetes/pki/ca.crt|clientCAFile: /etc/kubernetes/pki/ca-cert.pem|' /var/lib/kubelet/config.yaml && systemctl restart kubelet" || true
cq_wait 120 bash -c "[ \"\$(kubectl get node ckaquest-worker2 -o jsonpath='{.status.conditions[?(@.type==\"Ready\")].status}')\" != True ]"
echo "node02 is NotReady"
