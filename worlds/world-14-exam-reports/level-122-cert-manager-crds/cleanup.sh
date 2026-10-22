#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl get crd -o name | grep cert-manager.io | xargs -r kubectl delete --wait=false >/dev/null 2>&1
true
