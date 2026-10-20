#!/usr/bin/env bash
# PriorityClasses are cluster-scoped. Remove them so a replay starts clean.
kubectl delete pod critical-api dev-workload-1 -n ckaquest --ignore-not-found --wait=false >/dev/null 2>&1
kubectl delete priorityclass high-priority low-priority --ignore-not-found >/dev/null 2>&1
true
