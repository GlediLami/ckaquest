# Scale Down Slowly

## What happened
The HPA looks at the highest recommendation within the stabilization window before it scales down. A longer window stops flapping. Policies cap the speed: Pods (absolute) or Percent.

## Defaults
- scaleDown window 300s, scaleUp window 0s.
- Without policies, scale up can double the pods every 15s.

## Exam angle
- `k autoscale` creates the basic HPA. Behavior needs YAML.
- `autoscaling/v2` is the only version with behavior and multiple metrics.

Bookmark: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/

Your notes: Horizontal Pod Autoscaler
