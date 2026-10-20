#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_node_sh node01 'rm -f /etc/kubelet.d/miner.yaml' >/dev/null 2>&1
cq_node_restore node01 /var/lib/kubelet/config.yaml
cq_node_sh node01 'systemctl restart kubelet' >/dev/null 2>&1
cq_wait 90 bash -c "[ \"\$(kubectl get node ckaquest-worker -o jsonpath='{.status.conditions[?(@.type==\"Ready\")].status}')\" = True ]" || true
