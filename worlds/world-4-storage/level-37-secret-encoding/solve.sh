#!/usr/bin/env bash
kubectl create secret generic db-credentials -n ckaquest \
  --from-literal=username=admin --from-literal=password=secretpass123 \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl get pod database-client -n ckaquest -o yaml | kubectl replace --force -f -
