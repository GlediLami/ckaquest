#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl delete ns drill-109b --ignore-not-found --wait=false >/dev/null 2>&1
true
