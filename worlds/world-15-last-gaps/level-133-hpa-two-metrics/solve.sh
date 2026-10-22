#!/usr/bin/env bash
source "$CQ_ROOT/lib/common.sh"
cat <<'EOF' | kubectl apply -f -
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api
  namespace: hpa-multi
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 6
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
  - type: Resource
    resource:
      name: memory
      target:
        type: AverageValue
        averageValue: 50Mi
EOF
reading() { [ "$(kubectl get hpa api -n hpa-multi -o jsonpath='{range .status.currentMetrics[*]}{.resource.name}{"\n"}{end}' | sort | paste -sd' ')" = "cpu memory" ]; }
cq_wait 180 reading
