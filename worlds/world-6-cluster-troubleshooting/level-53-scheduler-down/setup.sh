#!/usr/bin/env bash
set -euo pipefail
source "$CQ_ROOT/lib/common.sh"
cq_break_manifest kube-scheduler 's|- kube-scheduler$|- kube-schedular|'
# Wait until the healthy scheduler is gone, then create the workload
cq_wait 120 bash -c "! kubectl -n kube-system get pod kube-scheduler-ckaquest-control-plane -o jsonpath='{.status.containerStatuses[0].ready}' | grep -q true"
kubectl create deployment web -n "$NAMESPACE" --image=nginx:1.27-alpine --replicas=2 >/dev/null
