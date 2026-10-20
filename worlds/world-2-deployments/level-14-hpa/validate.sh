#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
hpa_active() { [ "$(jp ckaquest hpa/web-backend-hpa '{.status.conditions[?(@.type=="ScalingActive")].status}')" = True ]; }
hpa_has_metric() { [ -n "$(jp ckaquest hpa/web-backend-hpa '{.status.currentMetrics[0].resource.current.averageUtilization}')" ]; }
check "HPA still targets 50% CPU, 1 to 5 replicas" out_eq "50 1 5" kubectl get hpa web-backend-hpa -n ckaquest -o jsonpath='{.spec.metrics[0].resource.target.averageUtilization} {.spec.minReplicas} {.spec.maxReplicas}'
check 2 "web-backend container has a CPU request" field_ne ckaquest deploy/web-backend '{.spec.template.spec.containers[0].resources.requests.cpu}' ""
check "web-backend is ready" deploy_ready ckaquest web-backend
check 2 "HPA condition ScalingActive is True" hpa_active
check "HPA shows a current CPU value (no <unknown>)" hpa_has_metric
finish
