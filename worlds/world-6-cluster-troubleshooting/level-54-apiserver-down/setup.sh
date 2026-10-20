#!/usr/bin/env bash
set -euo pipefail
source "$CQ_ROOT/lib/common.sh"
cq_break_manifest kube-apiserver 's|--etcd-servers=https://127.0.0.1:2379|--etcd-servers=https://127.0.0.1:2397|'
cq_wait 120 bash -c '! kubectl get --raw=/readyz --request-timeout=3s' || true
echo "The API server went away"
