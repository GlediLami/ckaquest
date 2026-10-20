#!/usr/bin/env bash
kubectl delete deployment database -n ckaquest --ignore-not-found
kubectl apply -f solution.yaml
