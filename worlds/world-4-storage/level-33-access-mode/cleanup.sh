#!/usr/bin/env bash
# PVs are cluster-scoped and survive the namespace reset. Remove them so a replay starts clean.
kubectl delete deploy/web-servers -n access-mode --ignore-not-found --timeout=60s >/dev/null 2>&1
kubectl delete pvc shared-pvc -n access-mode --ignore-not-found --timeout=60s >/dev/null 2>&1
kubectl delete pv shared-storage --ignore-not-found --timeout=60s >/dev/null 2>&1
true
