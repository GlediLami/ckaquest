#!/usr/bin/env bash
set -uo pipefail
source "$CQ_ROOT/lib/common.sh"
kubectl create serviceaccount node-inspector -n monitoring >/dev/null
kubectl delete clusterrole node-reader --ignore-not-found >/dev/null
kubectl delete clusterrolebinding node-inspector-binding --ignore-not-found >/dev/null
