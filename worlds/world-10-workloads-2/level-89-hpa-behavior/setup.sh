#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
kubectl create deployment api -n hpa-lab --image=nginx:1.27-alpine --replicas=2 >/dev/null
kubectl set resources deployment api -n hpa-lab --requests=cpu=50m,memory=32Mi >/dev/null
kubectl rollout status deployment api -n hpa-lab --timeout=90s >/dev/null
