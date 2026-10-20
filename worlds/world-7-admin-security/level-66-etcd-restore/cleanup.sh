#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
source "$CQ_ROOT/lib/common.sh"
cq_restore_manifest etcd
sleep 15
cq_wait_api 300 || true
kubectl delete configmap ledger -n payments --ignore-not-found >/dev/null 2>&1 || true
true
