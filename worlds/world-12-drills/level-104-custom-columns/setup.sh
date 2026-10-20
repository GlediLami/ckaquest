#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
W="$(cq_work_dir 104)"; for f in "$W"/*; do [ -e "$f" ] && mv -f "$f" "$f.old"; done; true
kubectl run zeta -n drill-104 --image=nginx:1.27-alpine >/dev/null
kubectl run alpha -n drill-104 --image=busybox:1.36 -- sleep 3600 >/dev/null
kubectl run mike -n drill-104 --image=nginx:1.28-alpine >/dev/null
kubectl wait --for=condition=Ready pod --all -n drill-104 --timeout=120s >/dev/null 2>&1 || true
