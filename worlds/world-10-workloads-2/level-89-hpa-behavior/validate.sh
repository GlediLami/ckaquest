#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
H='{.spec.behavior.scaleDown'
check "min 2, max 6" out_eq "2 6" kubectl get hpa api -n hpa-lab -o jsonpath='{.spec.minReplicas} {.spec.maxReplicas}'
check "targets 60% CPU" field_eq hpa-lab hpa/api '{.spec.metrics[0].resource.target.averageUtilization}' 60
check 2 "scaleDown stabilization window is 300s" field_eq hpa-lab hpa/api "$H.stabilizationWindowSeconds}" 300
check 2 "scaleDown policy: 1 Pod per 60s" out_eq "Pods 1 60" kubectl get hpa api -n hpa-lab -o jsonpath="$H.policies[0].type} $H.policies[0].value} $H.policies[0].periodSeconds}"
check "HPA is active" field_eq hpa-lab hpa/api '{.status.conditions[?(@.type=="ScalingActive")].status}' True
finish
