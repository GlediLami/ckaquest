#!/usr/bin/env bash
kubectl delete sts postgres-cluster -n statefulset-volumes --ignore-not-found --wait=true
kubectl delete pvc database-storage -n statefulset-volumes --ignore-not-found --wait=false
kubectl apply -f solution.yaml
