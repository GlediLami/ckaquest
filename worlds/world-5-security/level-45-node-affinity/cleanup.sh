#!/usr/bin/env bash
kubectl label nodes --all accelerator- >/dev/null 2>&1 || true
kubectl delete pod gpu-workload -n node-affinity --ignore-not-found --wait=false >/dev/null 2>&1
