#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_node_restore node02 /var/lib/kubelet/config.yaml
cq_node_sh node02 'systemctl restart kubelet' || true
cq_wait 120 bash -c "[ \"\$(kubectl get node ckaquest-worker2 -o jsonpath='{.status.conditions[?(@.type==\"Ready\")].status}')\" = True ]" || true
