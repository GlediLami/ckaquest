#!/usr/bin/env bash
set -euo pipefail
source "$CQ_ROOT/lib/common.sh"
cq_node_sh node01 'systemctl disable --now kubelet' >/dev/null 2>&1
# Wait until the control plane notices (node-monitor-grace-period)
cq_wait 120 bash -c "[ \"\$(kubectl get node ckaquest-worker -o jsonpath='{.status.conditions[?(@.type==\"Ready\")].status}')\" != True ]"
echo "node01 is NotReady"
