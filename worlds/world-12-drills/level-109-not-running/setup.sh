#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
W="$(cq_work_dir 109)"; for f in "$W"/*; do [ -e "$f" ] && mv -f "$f" "$f.old"; done; true
kubectl create ns drill-109b --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl run ok -n drill-109 --image=nginx:1.27-alpine >/dev/null
kubectl run badimage -n drill-109 --image=nginx:no-such-tag-cq >/dev/null
kubectl run toobig -n drill-109b --image=nginx:1.27-alpine --overrides='{"spec":{"containers":[{"name":"toobig","image":"nginx:1.27-alpine","resources":{"requests":{"cpu":"64"}}}]}}' >/dev/null
sleep 5
