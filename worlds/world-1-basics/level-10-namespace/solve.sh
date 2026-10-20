#!/usr/bin/env bash
kubectl delete pod client-app -n default --ignore-not-found --wait=false
kubectl delete svc backend-service -n default --ignore-not-found
kubectl apply -f solution.yaml
