#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
check 2 "release monitoring-stack is deployed in monitoring" out_match "deployed" bash -c "helm list -n monitoring | grep '^monitoring-stack'"
check "it runs chart webapp" out_match "webapp-" bash -c "helm list -n monitoring | grep '^monitoring-stack'"
check "values: replicaCount 3, service.type NodePort" out_match '"replicaCount":3.*NodePort|NodePort.*"replicaCount":3' helm get values monitoring-stack -n monitoring -o json
check 2 "3 pods Running" out_eq 3 bash -c "kubectl get pods -n monitoring --field-selector=status.phase=Running --no-headers | wc -l"
check "the Service is NodePort" out_match NodePort kubectl get svc -n monitoring -o jsonpath='{.items[*].spec.type}'
finish
