#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cq_restore_manifest kube-apiserver
sleep 15
cq_wait_api 240 || true
kubectl delete namespace auto-created --ignore-not-found --wait=false >/dev/null 2>&1 || true
true
