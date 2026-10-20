#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl delete pod user -n sc-lab --ignore-not-found --wait=true --timeout=60s >/dev/null 2>&1
kubectl delete pvc data -n sc-lab --ignore-not-found --timeout=60s >/dev/null 2>&1
for pv in $(kubectl get pv -o jsonpath='{range .items[?(@.spec.storageClassName=="local-retain")]}{.metadata.name}{" "}{end}'); do kubectl delete pv "$pv" --wait=false >/dev/null 2>&1; done
kubectl delete sc local-retain --ignore-not-found >/dev/null 2>&1
kubectl annotate sc standard storageclass.kubernetes.io/is-default-class=true --overwrite >/dev/null 2>&1
true
