#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
helm uninstall monitoring-stack -n monitoring >/dev/null 2>&1
kubectl delete ns monitoring --ignore-not-found --wait=false >/dev/null 2>&1
true
