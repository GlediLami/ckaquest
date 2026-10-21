#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
kubectl create deployment cache -n anti-lab --image=nginx:1.27 --replicas=2 >/dev/null
kubectl rollout status deploy/cache -n anti-lab --timeout=120s >/dev/null 2>&1 || true
