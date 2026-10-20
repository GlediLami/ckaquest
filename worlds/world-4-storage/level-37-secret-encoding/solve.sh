#!/usr/bin/env bash
kubectl create secret generic db-credentials -n secret-encoding \
  --from-literal=username=admin --from-literal=password=secretpass123 \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl get pod database-client -n secret-encoding -o yaml | kubectl replace --force -f -
