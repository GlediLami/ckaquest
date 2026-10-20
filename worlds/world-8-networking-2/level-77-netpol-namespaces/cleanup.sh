#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl delete namespace frontend-ns other-ns --ignore-not-found --wait=false >/dev/null 2>&1
true
