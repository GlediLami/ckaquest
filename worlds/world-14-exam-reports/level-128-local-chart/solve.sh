#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
helm install monitoring-stack "$CQ_WORK/128/webapp" -n monitoring --create-namespace --set replicaCount=3 --set service.type=NodePort
kubectl rollout status deploy -n monitoring --timeout=120s
