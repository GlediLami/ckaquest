#!/usr/bin/env bash
for n in ckaquest-worker ckaquest-worker2; do
  kubectl taint node "$n" dedicated- >/dev/null 2>&1 || true
done
kubectl delete pod regular-app -n taints-tolerations --ignore-not-found --wait=false >/dev/null 2>&1
