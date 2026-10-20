#!/usr/bin/env bash
kubectl uncordon ckaquest-worker2 >/dev/null 2>&1
kubectl delete namespace maint --ignore-not-found --wait=false >/dev/null 2>&1
