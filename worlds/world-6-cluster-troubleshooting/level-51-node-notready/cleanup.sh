#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_node_sh node01 'systemctl enable --now kubelet' >/dev/null 2>&1 || true
cq_wait 120 bash -c "[ \"\$(kubectl get node ckaquest-worker -o jsonpath='{.status.conditions[?(@.type==\"Ready\")].status}')\" = True ]" || true
