#!/usr/bin/env bash
kubectl -n maint patch pdb web-pdb --type=merge -p '{"spec":{"minAvailable":1}}'
kubectl drain ckaquest-worker2 --ignore-daemonsets --delete-emptydir-data --force --timeout=180s
kubectl -n maint rollout status deploy/web --timeout=120s
