#!/usr/bin/env bash
# PVs are cluster-scoped and survive the namespace reset. Remove them so a replay starts clean.
kubectl delete pod/data-writer -n reclaim-policy --ignore-not-found --timeout=60s >/dev/null 2>&1
kubectl delete pvc data-claim -n reclaim-policy --ignore-not-found --timeout=60s >/dev/null 2>&1
kubectl delete pv important-data --ignore-not-found --timeout=60s >/dev/null 2>&1
true
