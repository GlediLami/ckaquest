#!/usr/bin/env bash
# PVs are cluster-scoped and survive the namespace reset. Remove them so a replay starts clean.
kubectl delete pod/database-pod -n ckaquest --ignore-not-found --timeout=60s >/dev/null 2>&1
kubectl delete pvc app-storage-claim -n ckaquest --ignore-not-found --timeout=60s >/dev/null 2>&1
kubectl delete pv app-storage --ignore-not-found --timeout=60s >/dev/null 2>&1
true
