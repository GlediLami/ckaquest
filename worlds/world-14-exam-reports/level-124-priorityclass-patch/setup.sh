#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
kubectl delete priorityclass high-priority --ignore-not-found >/dev/null 2>&1
for pc in "batch-low 1000" "team-standard 250000" "team-critical 750000"; do
  set -- $pc
  kubectl create priorityclass "$1" --value="$2" >/dev/null 2>&1 || true
done
kubectl create deployment busybox-logger -n priority-lab --image=busybox:1.36 -- sh -c "while true; do echo log; sleep 10; done" >/dev/null
kubectl rollout status deploy/busybox-logger -n priority-lab --timeout=120s >/dev/null 2>&1 || true
