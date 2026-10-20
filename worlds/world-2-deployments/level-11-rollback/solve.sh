#!/usr/bin/env bash
kubectl rollout undo deployment/web-app -n rollback
kubectl rollout status deployment/web-app -n rollback --timeout=120s
