#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
kubectl get pods -n drill-108 -l app=shop -o jsonpath='{range .items[*]}{.metadata.name} {.spec.containers[?(@.name=="sidecar")].image}{"\n"}{end}' > "$CQ_WORK/108/sidecars.txt"
