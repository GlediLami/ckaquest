#!/usr/bin/env bash
kubectl delete namespace backend-ns --ignore-not-found --timeout=90s >/dev/null 2>&1
true
