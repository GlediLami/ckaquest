#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl delete clusterrolebinding backup-operator --ignore-not-found >/dev/null 2>&1
kubectl delete clusterrole backup-operator --ignore-not-found >/dev/null 2>&1
kubectl delete crd backups.ops.example.com --ignore-not-found --wait=false >/dev/null 2>&1
true
