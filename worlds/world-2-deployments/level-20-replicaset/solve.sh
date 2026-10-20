#!/usr/bin/env bash
kubectl delete rs web-app-rs -n replicaset --ignore-not-found
kubectl apply -f solution.yaml
