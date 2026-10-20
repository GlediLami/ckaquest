#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl delete clusterrolebinding node-inspector-binding --ignore-not-found >/dev/null 2>&1
kubectl delete clusterrole node-reader --ignore-not-found >/dev/null 2>&1
true
