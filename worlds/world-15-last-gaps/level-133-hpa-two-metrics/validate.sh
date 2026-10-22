#!/usr/bin/env bash
source "$CQ_ROOT/lib/validate.sh"
M='{.spec.metrics'
metric() { kubectl get hpa api -n hpa-multi -o jsonpath="$M[?(@.resource.name==\"$1\")].resource.target.type} $M[?(@.resource.name==\"$1\")].resource.target.$2}"; }
reading() { [ "$(kubectl get hpa api -n hpa-multi -o jsonpath='{range .status.currentMetrics[*]}{.resource.name}{"\n"}{end}' | sort | paste -sd' ')" = "cpu memory" ]; }
check "HPA api targets Deployment api, 2 to 6" out_eq "Deployment api 2 6" kubectl get hpa api -n hpa-multi -o jsonpath='{.spec.scaleTargetRef.kind} {.spec.scaleTargetRef.name} {.spec.minReplicas} {.spec.maxReplicas}'
check 2 "CPU: Utilization 60" out_eq "Utilization 60" metric cpu averageUtilization
check 2 "memory: AverageValue 50Mi" out_eq "AverageValue 50Mi" metric memory averageValue
check 2 "the HPA reads current CPU and memory" reading
finish
