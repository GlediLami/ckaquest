#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl delete pod wffc-pod -n wffc-lab --ignore-not-found --wait=false >/dev/null 2>&1
kubectl delete pvc wffc-pvc -n wffc-lab --ignore-not-found --wait=false >/dev/null 2>&1
kubectl delete pv wffc-pv --ignore-not-found --wait=false >/dev/null 2>&1
kubectl delete sc local-wffc --ignore-not-found >/dev/null 2>&1
true
