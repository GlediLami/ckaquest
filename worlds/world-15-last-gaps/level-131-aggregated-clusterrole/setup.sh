#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
kubectl delete clusterrole monitoring monitoring-pods monitoring-nodes --ignore-not-found >/dev/null 2>&1
kubectl delete clusterrolebinding monitoring --ignore-not-found >/dev/null 2>&1
kubectl create serviceaccount monitor -n agg-lab >/dev/null
