#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl delete pv drill-pv-a drill-pv-b drill-pv-c drill-pv-d --ignore-not-found --wait=false >/dev/null 2>&1
true
