#!/usr/bin/env bash
kubectl delete deployment database -n statefulset --ignore-not-found
kubectl apply -f solution.yaml
