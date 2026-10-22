#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
kubectl delete ns legacy-host --ignore-not-found --wait=true >/dev/null 2>&1
kubectl create ns legacy-host >/dev/null
kubectl run legacy-backend -n legacy-host --image=hashicorp/http-echo:1.0 --port=5678 -- -text="legacy backend" -listen=:5678 >/dev/null
kubectl wait --for=condition=Ready pod/legacy-backend -n legacy-host --timeout=120s >/dev/null 2>&1 || true
